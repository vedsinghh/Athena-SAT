#!/usr/bin/env python3
"""Import Information and Ideas questions from Educator Bank extract PDF."""

from __future__ import annotations

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
    join_words,
    split_passage_and_prompt,
    words_in_band,
    find_stem_y,
)
from fix_reading_ocr_spaces import normalize_prose, format_explanation  # noqa: E402

FOLDER = Path("/Users/vedsingh/Downloads/Information and Ideas 1")
EXTRACT_PDF = FOLDER / "Information and Ideas Extract.pdf"
POOL = "SAT Educator Bank 1"
DOMAIN = "Information and Ideas"
DATA = ROOT / "src" / "data"
PUBLIC_PDF_DIR = ROOT / "public" / "qbank" / "reading"
PUBLIC_PDF_NAME = "Information-and-Ideas-Educator-Bank-1.pdf"
PUBLIC_PDF_URL = f"/qbank/reading/{PUBLIC_PDF_NAME}"

SOURCE_PDF_BY_SKILL = {
    "Central Ideas and Details": FOLDER / "Central Ideas and Details.pdf",
    "Command of Evidence": FOLDER / "Command of Evidence.pdf",
    "Inferences": FOLDER / "Inferences.pdf",
}

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
    "The text",
    "How does",
    "Why does",
    "It can most reasonably",
    "What does the text",
)


def fingerprint(passage: str, prompt: str) -> str:
    blob = f"{passage}\n{prompt}".lower()
    blob = re.sub(r"[^a-z0-9]+", " ", blob)
    return re.sub(r"\s+", " ", blob).strip()[:240]


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
        meta["question"] = (q_m.group(1).strip() if q_m else "")
        c_m = CHOICE_RE.search(body)
        if c_m:
            meta["choices"] = [clean_text(c.replace("\n", " ")) for c in c_m.groups()]
        else:
            meta["choices"] = None
        r_m = re.search(r"RATIONALE:\s*\n(.*)$", body, re.S)
        rationale = (r_m.group(1) if r_m else "").strip()
        rationale = re.sub(r"^\s*[er]\s*\n", "", rationale)
        meta["rationale"] = clean_text(rationale.replace("\n", " "))
        best = re.search(r"Choice\s*([A-D])\s+is the best answer", meta["rationale"], re.I)
        meta["answer"] = ord(best.group(1).upper()) - ord("A") if best else None
        blocks.append(meta)

    # map extract page numbers (1-based) by scanning pages
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


def index_source_pdfs() -> dict[str, tuple[fitz.Document, int]]:
    """qid -> (doc, page_index)"""
    index: dict[str, tuple[fitz.Document, int]] = {}
    docs = {}
    for skill, path in SOURCE_PDF_BY_SKILL.items():
        if not path.exists():
            print(f"warn: missing source PDF for {skill}: {path}")
            continue
        doc = fitz.open(path)
        docs[skill] = doc
        for i, page in enumerate(doc):
            text = page.get_text() or ""
            m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", text, re.I)
            if m:
                index[m.group(1)] = (doc, i)
    return index


def strip_chart_ocr_prefix(text: str) -> str:
    """Remove axis/label OCR dumped before the real passage."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text

    def looks_like_chart_line(ln: str) -> bool:
        if re.fullmatch(r"[\d.,:%\-\s]+", ln):
            return True
        if ln.lower() in {"percent", "percentage", "year", "years", "number", "count", "age"}:
            return True
        if re.fullmatch(r"(house of representatives|senate|male|female|yes|no)", ln, re.I):
            return True
        if len(ln) <= 28 and not re.search(r"[.!?]", ln) and not any(
            ln.startswith(p) for p in PROMPT_STARTS
        ):
            # short title-ish fragments without sentence punctuation
            words = ln.split()
            if 1 <= len(words) <= 6 and sum(ch.isalpha() for ch in ln) >= 3:
                # keep if it looks like a normal sentence start with verb-ish later — heuristic: Title Case chart titles often stay
                if ln[:1].isdigit():
                    return True
                if ln.lower().startswith("percentage of") or ln.lower().endswith("1953-2023"):
                    return True
        return False

    # Drop leading chart lines until we hit a long prose sentence
    i = 0
    while i < len(lines):
        ln = lines[i]
        if len(ln) >= 60 and re.search(r"[a-z]", ln) and (
            "." in ln or "," in ln or " and " in ln.lower()
        ):
            break
        if looks_like_chart_line(ln) or (len(ln) < 55 and not re.search(r"[.!?]$", ln)):
            i += 1
            continue
        break
    return "\n".join(lines[i:]) if i < len(lines) else text


def rebuild_from_source_page(page: fitz.Page, figure_path: Path, text: str) -> tuple[str | None, str, str]:
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
    # Prefer existing formatter if Choice X is incorrect markers exist
    return format_explanation(text)


def build_item(block: dict, source_index: dict, extract_doc: fitz.Document) -> dict | None:
    qid = block["id"]
    skill = block["skill"]
    if not block["choices"] or block["answer"] is None:
        print(f"skip {qid}: missing choices/answer")
        return None

    question_text = block["question"]
    # Convert to body shape expected by split_passage_and_prompt
    body = strip_chart_ocr_prefix(question_text)
    passage, prompt = split_passage_and_prompt(body.replace("\r", ""))

    figure = None
    source_note = ""
    # Prefer rebuilding from official source PDF pages (better figures / passage)
    if qid in source_index:
        doc, page_i = source_index[qid]
        page = doc[page_i]
        page_text = page.get_text() or ""
        needs_fig = bool(re.search(r"\b(graph|table|figure|chart|scatterplot)\b", block["raw"], re.I))
        if needs_fig:
            fig_path = READING_FIG / f"{qid}.jpg"
            fig, rebuilt_passage, rebuilt_prompt = rebuild_from_source_page(page, fig_path, page_text)
            if fig:
                figure = f"/{fig}" if not str(fig).startswith("/") else str(fig)
                # crop_reading_figure returns path relative to public without leading /
                if not figure.startswith("/"):
                    figure = "/" + figure.lstrip("/")
                # public path helper returns like qbank/reading/figures/id.jpg
                if figure.startswith("/qbank") or figure.startswith("qbank"):
                    figure = "/" + figure.lstrip("/")
            if rebuilt_passage:
                passage = rebuilt_passage
            if rebuilt_prompt:
                prompt = rebuilt_prompt
        # Also try extract_source on passage from page when no figure
        if not needs_fig and not passage:
            # fallback body from page Question section
            pass

    # Fallback: pull embedded image from extract page
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

    choices = []
    for c in block["choices"]:
        choices.append({"text": normalize_prose(c)})

    item = {
        "id": qid,
        "topic": DOMAIN,
        "domain": DOMAIN,
        "skill": skill,
        "difficulty": block["difficulty"],
        "pool": POOL,
        "passageTitle": "Passage",
        "passage": passage,
        "prompt": prompt,
        "choices": choices,
        "answer": block["answer"],
        "type": "mc",
        "explanation": format_rationale(block["rationale"]),
        "pdf": PUBLIC_PDF_URL,
        "pdfPage": block.get("extract_page") or block.get("source_page") or 1,
    }
    if source_note:
        item["source"] = source_note
    if figure:
        # normalize figure path
        fig = figure
        if fig.startswith("qbank/"):
            fig = "/" + fig
        item["figure"] = fig
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
        domain: {
            "total": data["total"],
            "skills": dict(data["skills"]),
        }
        for domain, data in counts.items()
    }
    (DATA / "readingSkillCounts.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if not EXTRACT_PDF.exists():
        print(f"missing {EXTRACT_PDF}")
        return 1

    extract_doc = fitz.open(EXTRACT_PDF)
    blocks = parse_extract_blocks(extract_doc)
    print(f"parsed {len(blocks)} questions from extract")

    source_index = index_source_pdfs()
    print(f"indexed {len(source_index)} source-PDF question ids")

    existing_path = DATA / "readingQuestions.json"
    existing = json.loads(existing_path.read_text(encoding="utf-8"))
    existing_ids = {q["id"] for q in existing}
    existing_fps = {fingerprint(q.get("passage") or "", q.get("prompt") or "") for q in existing}

    READING_FIG.mkdir(parents=True, exist_ok=True)
    PUBLIC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    dest_pdf = PUBLIC_PDF_DIR / PUBLIC_PDF_NAME
    if not dest_pdf.exists() or dest_pdf.stat().st_size != EXTRACT_PDF.stat().st_size:
        shutil.copy2(EXTRACT_PDF, dest_pdf)
        print(f"copied extract PDF -> {dest_pdf}")

    added = []
    skipped_dup_id = 0
    skipped_dup_fp = 0
    skipped_bad = 0

    for block in blocks:
        qid = block["id"]
        if qid in existing_ids:
            skipped_dup_id += 1
            continue
        item = build_item(block, source_index, extract_doc)
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
        f"added {len(added)} new questions (pool={POOL}); "
        f"skipped id-dups={skipped_dup_id}, content-dups={skipped_dup_fp}, bad={skipped_bad}; "
        f"with figures={fig_n}; bank total={len(merged)}"
    )
    by_skill = Counter(q["skill"] for q in added)
    print("added by skill:", dict(by_skill))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
