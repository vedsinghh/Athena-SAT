#!/usr/bin/env python3
"""Import Educator Bank extract PDFs into readingQuestions.json (SAT Educator Bank 1)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402

from extract_questions import (  # noqa: E402
    READING_FIG,
    clean_text,
    crop_reading_figure,
    extract_source,
    find_stem_y,
    join_words,
    split_passage_and_prompt,
    words_in_band,
)
from fix_reading_ocr_spaces import format_explanation, normalize_prose  # noqa: E402

DATA = ROOT / "src" / "data"
PUBLIC_PDF_DIR = ROOT / "public" / "qbank" / "reading"
DEFAULT_POOL = "SAT Educator Bank 1"

CHOICE_RE = re.compile(
    r"\nA\.\s*(.*?)\nB\.\s*(.*?)\nC\.\s*(.*?)\nD\.\s*(.*?)(?:\nCORRECT_ANSWER:|\nRATIONALE:|\Z)",
    re.S,
)
PROMPT_STARTS = (
    "Which choice",
    "As used in",
    "The writer",
    "The student",
    "Based on",
    "According to",
    "What is the",
    "What choice",
    "Which quotation",
    "Which finding",
    "Which statement",
    "Which of the following",
    "Which word",
    "The text",
    "How does",
    "Why does",
    "It can most reasonably",
    "What does the text",
    "What does the dialogue",
)


def fingerprint(passage: str, prompt: str) -> str:
    blob = f"{passage}\n{prompt}".lower()
    blob = re.sub(r"[^a-z0-9]+", " ", blob)
    return re.sub(r"\s+", " ", blob).strip()[:240]


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name.strip()).strip("-")
    return s or "Educator-Bank"


def resolve_source_pdfs(folder: Path) -> dict[str, Path]:
    """Map skill name -> source PDF path by filename stem match."""
    pdfs = [p for p in folder.glob("*.pdf") if "Extract" not in p.name]
    mapping: dict[str, Path] = {}
    for pdf in pdfs:
        stem = pdf.stem.strip()
        mapping[stem] = pdf
        # Also allow loose match without trailing (1)
        mapping[re.sub(r"\(\d+\)$", "", stem).strip()] = pdf
    return mapping


def parse_extract_blocks(doc: fitz.Document) -> list[dict]:
    full = "\n".join((p.get_text() or "") for p in doc)
    blocks = []
    for m in re.finditer(
        r"QUESTION_ID:\s*([0-9a-fA-F]+)\s*\n(.*?)(?=\nEND_QUESTION\b)",
        full,
        re.S,
    ):
        qid = m.group(1)
        body = m.group(2)
        meta = {
            "id": qid,
            "source_file": (re.search(r"^SOURCE_FILE:\s*(.+)$", body, re.M) or [None, ""])[1].strip(),
            "source_page": int((re.search(r"^SOURCE_PAGE:\s*(\d+)", body, re.M) or [None, "0"])[1]),
            "skill": (re.search(r"^SKILL:\s*(.+)$", body, re.M) or [None, ""])[1].strip(),
            "difficulty": (re.search(r"^DIFFICULTY:\s*(.+)$", body, re.M) or [None, ""])[1].strip(),
            "extract_page": None,
            "raw": body,
        }
        q_m = re.search(
            r"QUESTION:\s*\n(.*?)(?:\nANSWER_CHOICES:|\nCORRECT_ANSWER:)",
            body,
            re.S,
        )
        meta["question"] = q_m.group(1).strip() if q_m else ""
        c_m = CHOICE_RE.search(body)
        meta["choices"] = (
            [clean_text(c.replace("\n", " ")) for c in c_m.groups()] if c_m else None
        )
        r_m = re.search(r"RATIONALE:\s*\n(.*)$", body, re.S)
        rationale = (r_m.group(1) if r_m else "").strip()
        rationale = re.sub(r"^\s*[er]\s*\n", "", rationale)
        # Expand terse "Choice C" openings into full sentence when needed
        if re.match(r"^Choice\s*[A-D]\s*$", rationale.strip(), re.I):
            letter = re.match(r"^Choice\s*([A-D])", rationale.strip(), re.I).group(1)
            rationale = f"Choice {letter.upper()} is the best answer. {rationale[len(rationale.strip()):]}".strip()
        meta["rationale"] = clean_text(rationale.replace("\n", " "))

        ans = None
        ca = re.search(r"^CORRECT_ANSWER:\s*([A-D])\s*$", body, re.M | re.I)
        if ca:
            ans = ord(ca.group(1).upper()) - ord("A")
        else:
            best = re.search(r"Choice\s*([A-D])\s+is the best answer", meta["rationale"], re.I)
            if best:
                ans = ord(best.group(1).upper()) - ord("A")
            else:
                # Some rationales start with "Choice C" only
                short = re.search(r"^Choice\s*([A-D])\b", meta["rationale"], re.I)
                if short:
                    ans = ord(short.group(1).upper()) - ord("A")
        meta["answer"] = ans
        blocks.append(meta)

    for i, page in enumerate(doc):
        text = page.get_text() or ""
        m = re.search(r"QUESTION_ID:\s*([0-9a-fA-F]+)", text)
        if not m:
            continue
        qid = m.group(1)
        for b in blocks:
            if b["id"] == qid and b["extract_page"] is None:
                b["extract_page"] = i + 1
                break
    return blocks


def index_source_pdfs(folder: Path, skills: set[str]) -> dict[str, tuple[fitz.Document, int]]:
    by_name = resolve_source_pdfs(folder)
    index: dict[str, tuple[fitz.Document, int]] = {}
    opened: dict[str, fitz.Document] = {}

    for skill in skills:
        path = by_name.get(skill)
        if path is None:
            # try SOURCE_FILE style names without extension
            for key, pdf in by_name.items():
                if key.lower() == skill.lower() or skill.lower() in key.lower():
                    path = pdf
                    break
        if path is None:
            print(f"warn: no source PDF matched skill {skill!r}")
            continue
        key = str(path)
        if key not in opened:
            opened[key] = fitz.open(path)
        doc = opened[key]
        for i, page in enumerate(doc):
            text = page.get_text() or ""
            m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", text, re.I)
            if m:
                index[m.group(1)] = (doc, i)
    return index


def strip_chart_ocr_prefix(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text

    def looks_like_chart_line(ln: str) -> bool:
        if re.fullmatch(r"[\d.,:%\-\s]+", ln):
            return True
        if ln.lower() in {"percent", "percentage", "year", "years", "number", "count", "age"}:
            return True
        if len(ln) <= 28 and not re.search(r"[.!?]", ln) and not any(
            ln.startswith(p) for p in PROMPT_STARTS
        ):
            if ln[:1].isdigit():
                return True
            if ln.lower().startswith("percentage of"):
                return True
        return False

    i = 0
    while i < len(lines):
        ln = lines[i]
        if len(ln) >= 60 and re.search(r"[a-z]", ln) and (
            "." in ln or "," in ln or " and " in ln.lower() or ln.startswith("Text ")
        ):
            break
        if looks_like_chart_line(ln) or (len(ln) < 55 and not re.search(r"[.!?]$", ln) and not ln.startswith("Text ")):
            i += 1
            continue
        break
    return "\n".join(lines[i:]) if i < len(lines) else text


def rebuild_from_source_page(page: fitz.Page, figure_path: Path, text: str):
    figure, _clip, passage_y = crop_reading_figure(page, figure_path, text)
    passage = ""
    prompt = ""
    if figure and passage_y is not None:
        stem_y = find_stem_y(page)
        a_y = None
        for label in ("Answer", "Correct Answer", "Rationale"):
            hits = page.search_for(label)
            if hits:
                a_y = hits[0].y0
                break
        if a_y is None:
            a_y = page.rect.height
        passage = join_words(words_in_band(page, passage_y - 0.5, stem_y)) or ""
        prompt = join_words(words_in_band(page, stem_y - 0.5, a_y)) or ""
    return figure, passage, prompt


def format_rationale(raw: str) -> str:
    text = normalize_prose(raw)
    if re.match(r"^Choice\s*[A-D]\b", text) and "is the best answer" not in text[:40].lower():
        letter = re.match(r"^Choice\s*([A-D])", text, re.I).group(1).upper()
        rest = text[re.match(r"^Choice\s*[A-D]\s*", text, re.I).end() :].lstrip(" .")
        text = f"Choice {letter} is the best answer. {rest}".strip()
    return format_explanation(text)


def build_item(
    block: dict,
    source_index: dict,
    extract_doc: fitz.Document,
    *,
    domain: str,
    pool: str,
    pdf_url: str,
) -> dict | None:
    qid = block["id"]
    skill = block["skill"]
    if not block["choices"] or block["answer"] is None:
        print(f"skip {qid}: missing choices/answer")
        return None

    body = strip_chart_ocr_prefix(block["question"])
    passage, prompt = split_passage_and_prompt(body.replace("\r", ""))

    figure = None
    if qid in source_index:
        doc, page_i = source_index[qid]
        page = doc[page_i]
        page_text = page.get_text() or ""
        needs_fig = bool(re.search(r"\b(graph|table|figure|chart|scatterplot)\b", block["raw"], re.I))
        if needs_fig:
            fig_path = READING_FIG / f"{qid}.jpg"
            fig, rebuilt_passage, rebuilt_prompt = rebuild_from_source_page(page, fig_path, page_text)
            if fig:
                figure = "/" + str(fig).lstrip("/")
                if not figure.startswith("/qbank"):
                    # relative to public
                    figure = "/" + str(fig).lstrip("/")
            if rebuilt_passage:
                passage = rebuilt_passage
            if rebuilt_prompt:
                prompt = rebuilt_prompt

    if figure is None and block.get("extract_page"):
        page = extract_doc[block["extract_page"] - 1]
        images = page.get_images()
        if images and re.search(r"\b(graph|table|figure|chart)\b", block["raw"], re.I):
            xref = images[0][0]
            pix = fitz.Pixmap(extract_doc, xref)
            if pix.n >= 5:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            out = READING_FIG / f"{qid}.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            pix.save(str(out))
            figure = f"/qbank/reading/figures/{qid}.jpg"
            passage = strip_chart_ocr_prefix(passage)

    source_note, passage = extract_source(passage)
    passage = normalize_prose(passage) if passage else ""
    prompt = normalize_prose(prompt) if prompt else "Select the best answer."
    if source_note:
        source_note = normalize_prose(source_note)

    # Preserve Text 1 / Text 2 labels for dual-passage rendering
    if re.search(r"\bText\s+[12]\b", block["question"]) and "Text 1" not in passage:
        # If normalize collapsed structure, rebuild lightly from question text
        rebuilt = normalize_prose(strip_chart_ocr_prefix(block["question"]).replace("\n", " "))
        # split prompt off again
        psg, prm = split_passage_and_prompt(rebuilt)
        if "Text 1" in psg and "Text 2" in psg:
            passage, prompt = psg, prm

    item = {
        "id": qid,
        "topic": domain,
        "domain": domain,
        "skill": skill,
        "difficulty": block["difficulty"],
        "pool": pool,
        "passageTitle": "Passage",
        "passage": passage,
        "prompt": prompt,
        "choices": [{"text": normalize_prose(c)} for c in block["choices"]],
        "answer": block["answer"],
        "type": "mc",
        "explanation": format_rationale(block["rationale"]),
        "pdf": pdf_url,
        "pdfPage": block.get("extract_page") or block.get("source_page") or 1,
    }
    if source_note:
        item["source"] = source_note
    if figure:
        fig = figure if figure.startswith("/") else "/" + figure.lstrip("/")
        if fig.startswith("/qbank") or "qbank/" in fig:
            item["figure"] = fig if fig.startswith("/") else "/" + fig
        else:
            item["figure"] = "/qbank/reading/figures/" + Path(fig).name
    return item


def update_skill_counts(questions: list[dict]) -> None:
    counts: dict[str, dict] = {}
    for q in questions:
        domain = q.get("domain") or "Other"
        skill = q.get("skill") or "Other"
        bucket = counts.setdefault(domain, {"total": 0, "skills": Counter()})
        bucket["total"] += 1
        bucket["skills"][skill] += 1
    out = {
        domain: {"total": data["total"], "skills": dict(data["skills"])}
        for domain, data in counts.items()
    }
    (DATA / "readingSkillCounts.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def import_extract(
    *,
    folder: Path,
    extract_pdf: Path,
    domain: str,
    pool: str,
    public_pdf_name: str,
) -> int:
    if not extract_pdf.exists():
        print(f"missing {extract_pdf}")
        return 1

    pdf_url = f"/qbank/reading/{public_pdf_name}"
    extract_doc = fitz.open(extract_pdf)
    blocks = parse_extract_blocks(extract_doc)
    print(f"parsed {len(blocks)} questions from {extract_pdf.name}")

    skills = {b["skill"] for b in blocks if b.get("skill")}
    source_index = index_source_pdfs(folder, skills)
    print(f"indexed {len(source_index)} source-PDF question ids")

    existing_path = DATA / "readingQuestions.json"
    existing = json.loads(existing_path.read_text(encoding="utf-8"))
    existing_ids = {q["id"] for q in existing}
    existing_fps = {
        fingerprint(q.get("passage") or "", q.get("prompt") or "") for q in existing
    }

    READING_FIG.mkdir(parents=True, exist_ok=True)
    PUBLIC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    dest_pdf = PUBLIC_PDF_DIR / public_pdf_name
    if not dest_pdf.exists() or dest_pdf.stat().st_size != extract_pdf.stat().st_size:
        shutil.copy2(extract_pdf, dest_pdf)
        print(f"copied extract PDF -> {dest_pdf}")

    added = []
    skipped_dup_id = skipped_dup_fp = skipped_bad = 0
    for block in blocks:
        qid = block["id"]
        if qid in existing_ids:
            skipped_dup_id += 1
            continue
        item = build_item(
            block,
            source_index,
            extract_doc,
            domain=domain,
            pool=pool,
            pdf_url=pdf_url,
        )
        if not item:
            skipped_bad += 1
            continue
        fp = fingerprint(item.get("passage") or "", item.get("prompt") or "")
        if fp and fp in existing_fps:
            skipped_dup_fp += 1
            print(f"skip duplicate content {qid}")
            continue
        added.append(item)
        existing_ids.add(qid)
        if fp:
            existing_fps.add(fp)

    merged = existing + added
    existing_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_skill_counts(merged)

    fig_n = sum(1 for q in added if q.get("figure"))
    print(
        f"added {len(added)} ({domain}, pool={pool}); "
        f"skipped id-dups={skipped_dup_id}, content-dups={skipped_dup_fp}, bad={skipped_bad}; "
        f"figures={fig_n}; bank total={len(merged)}"
    )
    print("added by skill:", dict(Counter(q["skill"] for q in added)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--folder", type=Path, required=True, help="Folder with Extract + skill PDFs")
    ap.add_argument("--extract", type=Path, default=None, help="Extract PDF path (default: *Extract.pdf in folder)")
    ap.add_argument("--domain", required=True, help='Domain name, e.g. "Craft and Structure"')
    ap.add_argument("--pool", default=DEFAULT_POOL)
    ap.add_argument("--public-pdf-name", default=None, help="Filename under public/qbank/reading/")
    args = ap.parse_args()

    folder = args.folder
    extract = args.extract
    if extract is None:
        matches = sorted(folder.glob("*Extract.pdf"))
        if not matches:
            print(f"no *Extract.pdf in {folder}")
            return 1
        extract = matches[0]
    public_name = args.public_pdf_name or f"{slugify(args.domain)}-Educator-Bank-1.pdf"

    return import_extract(
        folder=folder,
        extract_pdf=extract,
        domain=args.domain,
        pool=args.pool,
        public_pdf_name=public_name,
    )


if __name__ == "__main__":
    raise SystemExit(main())
