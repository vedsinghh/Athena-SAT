#!/usr/bin/env python3
"""Import S. Bank reading PDFs into readingQuestions.json."""

from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402

from extract_questions import (  # noqa: E402
    READING_FIG,
    clean_text,
    extract_choices_text,
    extract_source,
    find_passage_start_y,
    find_stem_y,
    join_words,
    looks_like_table_data_row,
    render_figure_clip,
    split_passage_and_prompt,
    words_in_band,
)
from fix_reading_ocr_spaces import format_explanation, normalize_prose  # noqa: E402

FOLDER = Path("/Users/vedsingh/Downloads/Student Bank 1")
POOL = "S. Bank"
DATA = ROOT / "src" / "data"
PUBLIC_PDF_DIR = ROOT / "public" / "qbank" / "reading"
READING_JSON = DATA / "readingQuestions.json"
SKILL_COUNTS = DATA / "readingSkillCounts.json"

DOMAIN_PDFS = {
    "Information and Ideas": FOLDER / "Information and Ideas.pdf",
    "Craft and Structure": FOLDER / "Craft and Structure.pdf",
    "Expression of Ideas": FOLDER / "Expression of Ideas.pdf",
    "Standard English Conventions": FOLDER / "Standard English Conventions.pdf",
}

QID_RE = re.compile(r"Question ID[:\s]+([0-9a-fA-F]{8})\b", re.I)
DIFF_RE = re.compile(r"Question\s+Di(?:ffi|ﬃ)culty:\s*(Easy|Medium|Hard)", re.I)
KNOWN_SKILLS = [
    "Central Ideas and Details",
    "Command of Evidence",
    "Inferences",
    "Words in Context",
    "Text Structure and Purpose",
    "Cross-Text Connections",
    "Rhetorical Synthesis",
    "Transitions",
    "Boundaries",
    "Form, Structure, and Sense",
]


def fingerprint(passage: str, prompt: str) -> str:
    blob = f"{passage}\n{prompt}".lower()
    blob = re.sub(r"[^a-z0-9]+", " ", blob)
    return re.sub(r"\s+", " ", blob).strip()[:240]


def normalize_unicode(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return (
        text.replace("\u00a0", " ")
        .replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("ﬃ", "ffi")
        .replace("ﬄ", "ffl")
        .replace("ﬀ", "ff")
    )


def fix_text_label_joins(text: str) -> str:
    # Student Bank PDFs / OCR sometimes glue "in"/"of" onto "Text 1/2".
    return re.sub(r"\b(in|of|to|from|and)(Text\s*[12])\b", r"\1 \2", text or "")


def polish_field(text: str) -> str:
    text = text or ""
    if "\n" in text and looks_like_verse_block(text):
        lines = [fix_text_label_joins(normalize_prose(normalize_unicode(line))) for line in text.split("\n")]
        return "\n".join(line for line in lines if line)
    return fix_text_label_joins(normalize_prose(normalize_unicode(text)))


def looks_like_verse_block(text: str) -> bool:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < 3:
        return False
    short = sum(1 for ln in lines if len(ln) <= 90)
    speaker = any(re.match(r"^[A-Z][A-Z .'-]{0,24}:", ln) for ln in lines)
    return speaker or short >= len(lines) - 1


def strip_copyright_line(text: str) -> str:
    return re.sub(r"(?:\n|^)\s*©\s*\d{4}\s+by\s+.+$", "", text or "", flags=re.I | re.M).strip()


def split_student_source(passage: str) -> tuple[str, str]:
    """Pull College Board attribution/context into `source`, leave the excerpt in `passage`."""
    text = strip_copyright_line(passage or "")
    if not re.match(
        r"^(?:The following text is (?:adapted from|from)|Text \d+ is adapted from|Adapted from)\b",
        text,
        re.I,
    ):
        return extract_source(text)

    for pat in (
        r"\n(?=[A-Z][A-Z .'-]{0,24}:)",  # MIRANDA:
        r"\n(?=\[[^\]]+\])",  # [Jay Gatsby]
        r"\n(?=[\"\u201c])",
    ):
        m = re.search(pat, text)
        if m:
            return clean_text(text[: m.start()]), text[m.end() :].lstrip("\n")

    flat = re.sub(r"\s*\n\s*", " ", text)
    flat = re.sub(r" +", " ", flat).strip()
    # Avoid splitting on initials ("A. Christina", "Charles A. Eastman").
    sentences = re.split(r"(?<=[a-z0-9)\]\"'”’])\.\s+(?=[A-Z\[\"'\u201c\u2018])", flat)
    # re.split drops the `.`; put it back on each head sentence except possibly the last.
    if len(sentences) > 1:
        rebuilt = []
        for i, part in enumerate(sentences):
            part = part.strip()
            if not part:
                continue
            if i < len(sentences) - 1 and not part.endswith("."):
                part += "."
            rebuilt.append(part)
        sentences = rebuilt
    if not sentences:
        return "", text

    def is_context(sentence: str, idx: int) -> bool:
        if idx == 0:
            return True
        s = sentence.strip()
        if re.match(
            r"^(?:In the text\b|The (?:text|narrator|author|speaker|passage)\b|"
            r"A [A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*)? is (?:a|an)\b)",
            s,
            re.I,
        ):
            return True
        if re.search(r"\bis a reference to\b", s, re.I):
            return True
        if re.match(
            r"^[A-Z][a-z]+ is (?:walking|talking|standing|sitting|looking|traveling|describing)\b",
            s,
        ):
            return True
        if re.search(r"\b(?:brother|sister) and\b", s) and len(s) < 180:
            return True
        return False

    n = 0
    while n < len(sentences) and is_context(sentences[n], n):
        n += 1
    if n == 0:
        n = 1
    source = clean_text(" ".join(sentences[:n]))
    rest = clean_text(" ".join(sentences[n:])) if n < len(sentences) else ""
    return source, rest


def trim_prompt(prompt: str) -> str:
    prompt = (prompt or "").strip()
    prompt = re.split(r"\nA\.\s", prompt, maxsplit=1)[0]
    prompt = re.split(r"\s+A\.\s", prompt, maxsplit=1)[0]
    return prompt.strip()


def split_student_passage_and_prompt(body: str) -> tuple[str, str]:
    """Like extract_questions.split_passage_and_prompt, plus Student Bank stems."""
    lines = body.split("\n")
    stem_idx = None
    # Prefer specific stems; avoid bare "Based on"/"According to" which often open passages.
    stem_starts = (
        "Which choice", "As used in", "The writer", "The student",
        "Based on the text", "Based on the table", "Based on the graph",
        "Based on the figure", "Based on Text", "Based on passages",
        "According to the text", "According to Text", "According to the author",
        "According to the passage",
        "What is the", "What choice", "What does the text", "What does the dialogue",
        "Which quotation", "Which finding", "Which statement", "Which of the following",
        "Which detail", "Which word", "Taken together",
        "The text most", "The text suggests", "The text indicates",
        "In the text", "How does", "Why does",
        "It can most reasonably",
    )
    for i, line in enumerate(lines):
        s = line.strip()
        if any(s.startswith(p) for p in stem_starts):
            stem_idx = i
            break
    if stem_idx is None:
        flat = clean_text(body)
        for start in stem_starts:
            idx = flat.find(start)
            if idx > 0:
                return clean_text(flat[:idx]), clean_text(flat[idx:])
        return flat, "Select the best answer."
    passage = clean_text("\n".join(lines[:stem_idx]))
    prompt = clean_text("\n".join(lines[stem_idx:]))
    if not passage:
        # Stem matched the first line of a passage (false positive) — keep searching.
        for j in range(1, len(lines)):
            s = lines[j].strip()
            if any(s.startswith(p) for p in stem_starts):
                return (
                    clean_text("\n".join(lines[:j])),
                    clean_text("\n".join(lines[j:])),
                )
        return clean_text(body), "Select the best answer."
    return passage, prompt


def public_pdf_name(domain: str, *, unanswered: bool = False) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", domain).strip("-")
    suffix = "-Unanswered" if unanswered else ""
    return f"Student-Bank-1-{slug}{suffix}.pdf"


def answer_section_top_y(page: fitz.Page) -> float | None:
    """Y where the answer key / rationale begins (below the choices)."""
    text = page.get_text("text") or ""
    candidates: list[float] = []
    for m in re.finditer(r"ID:\s*([0-9a-fA-F]{8})\s+Answer", text):
        qid = m.group(1)
        for needle in (f"ID: {qid}", qid):
            for hit in page.search_for(needle) or []:
                # Skip the header ID under the question title.
                if hit.y0 > page.rect.height * 0.28:
                    candidates.append(hit.y0)
    # These labels can sit at the very top of continuation pages (even slightly
    # above y=0), so don't require a mid-page threshold.
    for label in ("Correct Answer", "Rationale"):
        for hit in page.search_for(label) or []:
            candidates.append(hit.y0)
    if candidates:
        return max(page.rect.y0, min(candidates) - 3)

    # Continuation pages that are rationale-only (no question header / choice list).
    if not (page.search_for("Question ID") or []):
        has_choice_key = bool(re.search(r"Choice [A-D] is (?:incorrect|the best)\b", text, re.I))
        has_choice_list = bool(re.search(r"\n[A-D]\.\s", text))
        has_diff_footer = bool(re.search(r"Question\s+Di(?:ffi|ﬃ)culty\b", text, re.I))
        if (
            has_choice_key
            or (has_diff_footer and not has_choice_list)
            or re.search(r"\b(?:incorrect because|best answer because)\b", text, re.I)
        ):
            return page.rect.y0
    return None


def write_unanswered_pdf(src: Path, dest: Path) -> None:
    """Copy a Student Bank PDF with answer keys and rationales redacted."""
    doc = fitz.open(src)
    for page in doc:
        y = answer_section_top_y(page)
        if y is None:
            continue
        page.add_redact_annot(
            fitz.Rect(page.rect.x0, max(page.rect.y0, y), page.rect.x1, page.rect.y1),
            fill=(1, 1, 1),
        )
        page.apply_redactions()
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dest, garbage=4, deflate=True)
    doc.close()


def strip_page_footer_meta(text: str) -> str:
    """Remove the Assessment/Test/Domain/Skill footer that Student Bank pages append."""
    text = text or ""
    text = re.split(r"\nAssessment\nSAT\nTest\n", text, maxsplit=1)[0]
    text = re.split(r"\nQuestion\s+Di(?:ffi|ﬃ)culty:\s*(?:Easy|Medium|Hard)\s*$", text, maxsplit=1)[0]
    return text.rstrip()


def group_pages(doc: fitz.Document) -> list[dict]:
    pages = []
    for i in range(doc.page_count):
        text = normalize_unicode(doc[i].get_text("text") or "")
        m = QID_RE.search(text)
        pages.append({"index": i, "id": m.group(1).lower() if m else None, "text": text})

    groups: list[dict] = []
    current = None
    for page in pages:
        if page["id"]:
            if current:
                groups.append(current)
            current = {
                "id": page["id"],
                "pages": [page["index"]],
                # Keep full page text for Domain/Skill/Difficulty (footer strip removes them).
                "meta_text": page["text"],
                "text": strip_page_footer_meta(page["text"]),
            }
        elif current is not None and page["text"].strip():
            current["pages"].append(page["index"])
            current["meta_text"] += "\n" + page["text"]
            current["text"] += "\n" + strip_page_footer_meta(page["text"])
    if current:
        groups.append(current)
    return groups


def parse_meta(text: str, fallback_domain: str) -> tuple[str, str, str]:
    difficulty = "Medium"
    m = DIFF_RE.search(text)
    if m:
        difficulty = m.group(1).title()

    domain = fallback_domain
    skill = ""
    # Bottom-of-page labeled fields (most reliable on Student Bank PDFs).
    dm = re.search(
        r"\nDomain\n([\s\S]*?)\nSkill\n([\s\S]*?)(?:\nDi(?:ffi|ﬃ)culty\b|\Z)",
        text,
        re.I,
    )
    if dm:
        domain_raw = re.sub(r"\s+", " ", dm.group(1)).strip()
        skill_raw = re.sub(r"\s+", " ", dm.group(2)).strip()
        for known in sorted(KNOWN_SKILLS, key=len, reverse=True):
            if known.lower() in skill_raw.lower() or skill_raw.lower() in known.lower():
                skill = known
                break
        if not skill:
            skill = skill_raw
        for known_domain in DOMAIN_PDFS:
            if known_domain.lower() in domain_raw.lower() or domain_raw.lower() in known_domain.lower():
                domain = known_domain
                break

    if not skill:
        for known in KNOWN_SKILLS:
            if known in text:
                skill = known
                break
    if not skill:
        skill = "Other"
    return domain, skill, difficulty


def extract_body(text: str, qid: str) -> str:
    # Body starts after the repeated "ID: <qid>" line under the header table.
    m = re.search(rf"\nID:\s*{re.escape(qid)}\s*\n", text, re.I)
    if not m:
        m = re.search(rf"Question ID[:\s]+{re.escape(qid)}\s*\nID:\s*{re.escape(qid)}\s*\n", text, re.I)
    if not m:
        return ""
    body = text[m.end() :]
    body = re.split(rf"\nID:\s*{re.escape(qid)}\s+Answer\b", body, maxsplit=1, flags=re.I)[0]
    body = re.split(r"\nCorrect Answer:", body, maxsplit=1)[0]
    body = re.split(r"\nA\.\s", body, maxsplit=1)[0]
    return body.strip()


def extract_explanation(text: str) -> str:
    m = re.search(r"\nRationale\n([\s\S]*)$", text)
    if not m:
        return ""
    expl = m.group(1).strip()
    expl = re.split(r"\nQuestion ID[:\s]+", expl, maxsplit=1)[0].strip()
    expl = re.split(r"\nQuestion\s+Di(?:ffi|ﬃ)culty:", expl, maxsplit=1)[0].strip()
    expl = re.split(r"\nAssessment\n", expl, maxsplit=1)[0].strip()
    return clean_text(normalize_unicode(expl))


def strip_chart_ocr_prefix(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text

    def looks_like_chart_line(ln: str) -> bool:
        if looks_like_table_data_row(ln):
            return True
        if re.fullmatch(r"[\d.,:%\-\s]+", ln):
            return True
        low = ln.lower()
        if low in {
            "percent",
            "percentage",
            "year",
            "years",
            "number",
            "count",
            "age",
            "jobs",
            "marketing year",
            "uncertainty",
            "(larger values = more uncertainty)",
        }:
            return True
        if len(ln) <= 40 and not re.search(r"[.!?]", ln):
            if ln[:1].isdigit():
                return True
            if any(
                low.startswith(p)
                for p in (
                    "percentage of",
                    "marketing year",
                    "argentina",
                    "brazil",
                    "united states",
                    "area of",
                    "employment in",
                    "jasmonic",
                    "economic policy",
                )
            ):
                return True
        return False

    i = 0
    while i < len(lines):
        ln = lines[i]
        if looks_like_table_data_row(ln):
            i += 1
            continue
        if len(ln) >= 55 and re.search(r"[a-z]", ln) and (
            "." in ln or "," in ln or " and " in ln.lower()
        ):
            break
        if looks_like_chart_line(ln) or (
            len(ln) < 55 and not re.search(r"[.!?]$", ln) and not ln.startswith("Text ")
        ):
            i += 1
            continue
        break
    return "\n".join(lines[i:]) if i < len(lines) else text


def crop_student_figure(page: fitz.Page, out_path: Path, text: str) -> tuple[str | None, float | None]:
    """Crop chart/table between the ID line and the passage prose."""
    if not re.search(r"\b(graph|table|figure|chart|scatterplot|diagram)\b", text, re.I):
        return None, None

    id_hits = page.search_for("ID:")
    if not id_hits:
        return None, None
    # Prefer the upper ID label (under the header), not the Answer section.
    top_ids = [r for r in id_hits if r.y0 < page.rect.height * 0.45]
    id_rect = (top_ids or id_hits)[0]
    y0 = id_rect.y1 + 2

    stem_y = find_stem_y(page) or (page.rect.height * 0.75)
    passage_y = find_passage_start_y(page, y0 + 8, stem_y)
    if passage_y is None:
        passage_y = stem_y - 8
    if passage_y - y0 < 80:
        return None, None

    clip = fitz.Rect(
        page.rect.x0 + 18,
        max(page.rect.y0 + 8, y0),
        page.rect.x1 - 18,
        # Keep the table's bottom rule; passage_y is the first prose baseline.
        min(page.rect.y1 - 8, passage_y),
    )
    if clip.height < 70 or clip.width < 120:
        return None, None

    rel = render_figure_clip(page, out_path, clip, scale=3.4)
    if not rel:
        return None, None
    return f"/{rel}", passage_y


def build_item(group: dict, doc: fitz.Document, *, domain: str, pdf_url: str) -> dict | None:
    qid = group["id"]
    text = group["text"]
    domain, skill, difficulty = parse_meta(group.get("meta_text") or text, domain)

    choices = extract_choices_text(text)
    ans_m = re.search(r"Correct Answer:\s*([A-D])\b", text)
    if not choices or not ans_m:
        print(f"skip {qid}: missing choices/answer")
        return None
    answer = ord(ans_m.group(1).upper()) - ord("A")

    body = extract_body(text, qid)
    if not body:
        print(f"skip {qid}: empty body")
        return None

    page = doc[group["pages"][0]]
    figure = None
    passage_y = None
    fig_path = READING_FIG / f"{qid}.jpg"
    figure, passage_y = crop_student_figure(page, fig_path, text)

    if figure and passage_y is not None:
        stem_y = find_stem_y(page) or page.rect.height
        rebuilt_passage = join_words(words_in_band(page, passage_y - 0.5, stem_y)) or ""
        # Prefer stem from the PDF body so choice A isn't glued onto the prompt.
        body_clean = strip_chart_ocr_prefix(body)
        _, prompt_from_body = split_student_passage_and_prompt(body_clean.replace("\r", ""))
        if rebuilt_passage:
            passage = rebuilt_passage
            prompt = trim_prompt(prompt_from_body) or "Select the best answer."
        else:
            passage, prompt = split_student_passage_and_prompt(body_clean.replace("\r", ""))
            prompt = trim_prompt(prompt)
    else:
        body = strip_chart_ocr_prefix(body)
        passage, prompt = split_student_passage_and_prompt(body.replace("\r", ""))
        prompt = trim_prompt(prompt)

    source_note, passage = split_student_source(passage)

    passage = polish_field(passage) if passage else ""
    prompt = polish_field(prompt) if prompt else "Select the best answer."
    if source_note:
        source_note = polish_field(source_note)
    passage = strip_copyright_line(passage)
    if source_note:
        source_note = strip_copyright_line(source_note)

    # Keep Text 1 / Text 2 labels when present.
    if re.search(r"\bText\s+[12]\b", text) and "Text 1" not in passage:
        rebuilt = polish_field(strip_chart_ocr_prefix(body).replace("\n", " "))
        psg, prm = split_student_passage_and_prompt(rebuilt)
        if "Text 1" in psg and "Text 2" in psg:
            passage, prompt = psg, polish_field(prm)

    item = {
        "id": qid,
        "topic": domain,
        "domain": domain,
        "skill": skill,
        "difficulty": difficulty,
        "pool": POOL,
        "passageTitle": "Passage",
        "passage": passage,
        "prompt": prompt,
        "choices": [{"text": polish_field(c)} for c in choices],
        "answer": answer,
        "type": "mc",
        "explanation": fix_text_label_joins(format_explanation(extract_explanation(text))),
        "pdf": pdf_url,
        "pdfPage": group["pages"][0] + 1,
    }
    if source_note:
        item["source"] = source_note
    if figure:
        item["figure"] = figure
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
    SKILL_COUNTS.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    existing = json.loads(READING_JSON.read_text(encoding="utf-8"))
    # Drop any prior Student Bank 1 rows so re-runs stay idempotent.
    existing = [q for q in existing if q.get("pool") != POOL]
    existing_ids = {str(q.get("id") or "").lower() for q in existing}

    PUBLIC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    READING_FIG.mkdir(parents=True, exist_ok=True)
    for p in READING_FIG.glob("_test_*.jpg"):
        p.unlink()

    added: list[dict] = []
    for domain, pdf_path in DOMAIN_PDFS.items():
        if not pdf_path.exists():
            print(f"missing {pdf_path}")
            return 1
        dest = PUBLIC_PDF_DIR / public_pdf_name(domain)
        shutil.copy2(pdf_path, dest)
        unanswered = PUBLIC_PDF_DIR / public_pdf_name(domain, unanswered=True)
        write_unanswered_pdf(dest, unanswered)
        # Practice PDF button must not reveal answers / rationales.
        pdf_url = f"/qbank/reading/{unanswered.name}"
        print(f"copied {pdf_path.name} -> {dest.relative_to(ROOT)}")
        print(f"unanswered -> {unanswered.relative_to(ROOT)}")

        doc = fitz.open(pdf_path)
        groups = group_pages(doc)
        print(f"{domain}: {len(groups)} questions")
        for group in groups:
            qid = group["id"]
            if qid in existing_ids or any(a["id"] == qid for a in added):
                print(f"  skip {qid}: already in bank")
                continue
            item = build_item(group, doc, domain=domain, pdf_url=pdf_url)
            if not item:
                continue
            added.append(item)

    if not added:
        print("no new questions")
        return 1

    merged = existing + added
    READING_JSON.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_skill_counts(merged)

    by_domain = Counter(q["domain"] for q in added)
    by_skill = Counter(q["skill"] for q in added)
    figs = sum(1 for q in added if q.get("figure"))
    print(f"added {len(added)} Student Bank 1 questions (figures={figs})")
    print("domains:", dict(by_domain))
    print("skills:", dict(by_skill))
    print(f"total reading questions now: {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
