#!/usr/bin/env python3
"""Import Summer 2026 Bank 2 reading and math PDFs.

Sources:
  /Users/vedsingh/Downloads/10 RW Qs- With Answers.pdf
  /Users/vedsingh/Downloads/49 Math Qs- With answers.pdf

Practice PDF buttons point at unanswered copies (Correct Answer / Rationale redacted).
Existing question IDs and prompt fingerprints are skipped.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402

from extract_questions import (  # noqa: E402
    MATH_CHOICE_IMG,
    MATH_DOMAINS,
    MATH_FIG,
    MATH_PDF_PREVIEW,
    READING_FIG,
    RW_DOMAINS,
    build_math_prompt,
    clean_text,
    correct_answer,
    crop_math_figure,
    crop_math_pdf_preview,
    crop_reading_figure,
    extract_choice_objects,
    extract_choices_text,
    extract_explanation,
    extract_question_body,
    extract_source,
    find_stem_y,
    group_pages,
    join_words,
    ocr_looks_broken,
    ocr_math_stem,
    parse_meta,
    polish_ocr_stem,
    prompt_looks_broken,
    should_prefer_ocr_stem,
    split_passage_and_prompt,
    strip_chart_noise,
    words_in_band,
)
from fix_reading_ocr_spaces import format_explanation, normalize_prose  # noqa: E402

POOL = "Summer 2026 Bank 2"
RW_SRC = Path("/Users/vedsingh/Downloads/10 RW Qs- With Answers.pdf")
MATH_SRC = Path("/Users/vedsingh/Downloads/49 Math Qs- With answers.pdf")
DATA = ROOT / "src" / "data"
READING_JSON = DATA / "readingQuestions.json"
MATH_JSON = DATA / "mathQuestions.json"
READING_COUNTS = DATA / "readingSkillCounts.json"
MATH_COUNTS = DATA / "mathSkillCounts.json"
PUBLIC_READING = ROOT / "public" / "qbank" / "reading"
PUBLIC_MATH = ROOT / "public" / "qbank" / "math"
RW_UNANSWERED_NAME = "Summer-2026-Bank-2-Reading-Unanswered.pdf"
MATH_UNANSWERED_NAME = "Summer-2026-Bank-2-Math-Unanswered.pdf"


def fingerprint(*parts: str) -> str:
    blob = " ".join(parts).lower()
    blob = re.sub(r"[^a-z0-9]+", " ", blob)
    blob = re.sub(r"\s+", " ", blob).strip()
    letters = re.sub(r"[^a-z]+", "", blob)
    if len(letters) < 80:
        return ""
    return blob[:240]


def make_unanswered_pdf(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(src)
    for page in doc:
        starts = []
        for label in ("Correct Answer", "Rationale"):
            for hit in page.search_for(label) or []:
                if hit.x0 < 160:
                    starts.append(hit.y0)
        if not starts:
            continue
        y0 = max(page.rect.y0, min(starts) - 3)
        page.add_redact_annot(
            fitz.Rect(page.rect.x0, y0, page.rect.x1, page.rect.y1),
            fill=(1, 1, 1),
        )
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dest, garbage=4, deflate=True)
    doc.close()


def format_math_explanation(raw: str) -> str:
    text = clean_text(raw or "")
    if not text:
        return ""
    parts = re.split(r"(?=\bChoice\s+[A-D]\s+is incorrect\b)", text, flags=re.I)
    parts = [p.strip() for p in parts if p and p.strip()]
    if len(parts) <= 1:
        return text
    return "\n\n".join(parts)


def polish_reading_field(text: str) -> str:
    return normalize_prose(clean_text(text or ""))


def rebuild_skill_counts(questions: list[dict], path: Path) -> None:
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
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_reading_item(group: dict, doc: fitz.Document, pdf_url: str) -> dict | None:
    qid = group["id"].lower()
    text = group["text"]
    domain, skill, difficulty = parse_meta(text, "Reading and Writing", RW_DOMAINS)
    body = extract_question_body(text)
    passage, prompt = split_passage_and_prompt(body)
    choices = extract_choices_text(text)
    kind, ans = correct_answer(text)
    explanation = format_explanation(extract_explanation(text))
    if not choices or kind != "mc" or domain is None:
        print(f"  skip reading {qid}: domain={domain} kind={kind} choices={bool(choices)}")
        return None

    page = doc[group["pages"][0]]
    figure, _clip, passage_y = crop_reading_figure(page, READING_FIG / f"{qid}.jpg", text)
    if figure and passage_y is not None:
        stem_y = find_stem_y(page)
        passage = join_words(words_in_band(page, passage_y - 0.5, stem_y)) or passage
        a_y = page.rect.height
        for lab in ("Answer", "Correct Answer"):
            hits = page.search_for(lab) or []
            header = [h for h in hits if h.width < 70 and h.x0 < 80]
            if header:
                a_y = min(a_y, header[0].y0)
        rebuilt_prompt = join_words(words_in_band(page, stem_y - 0.5, a_y))
        if rebuilt_prompt:
            prompt = rebuilt_prompt

    source, passage = extract_source(passage)
    item = {
        "id": qid,
        "topic": domain,
        "domain": domain,
        "skill": skill,
        "difficulty": difficulty,
        "pool": POOL,
        "passageTitle": "Passage",
        "passage": polish_reading_field(passage),
        "prompt": polish_reading_field(prompt),
        "choices": [{"text": polish_reading_field(c)} for c in choices],
        "answer": ans,
        "type": "mc",
        "explanation": explanation,
        "pdf": pdf_url,
        "pdfPage": group["pages"][0] + 1,
    }
    if source:
        item["source"] = polish_reading_field(source)
    if figure:
        item["figure"] = figure
    return item


def build_math_item(group: dict, src_doc: fitz.Document, src_idx: int, pdf_url: str) -> dict | None:
    qid = group["id"].lower()
    text = group["text"]
    domain, skill, difficulty = parse_meta(text, "Math", MATH_DOMAINS)
    kind, ans = correct_answer(text)
    explanation = format_math_explanation(extract_explanation(text))
    if domain is None or kind is None:
        print(f"  skip math {qid}: domain={domain} kind={kind}")
        return None

    page = src_doc[src_idx]
    figure, figure_rect = crop_math_figure(page, MATH_FIG / f"{qid}.jpg", text)
    prompt, equation_images = build_math_prompt(page, text, figure_rect=figure_rect, qid=qid)
    built_prompt_snapshot = prompt
    ocr_prompt = polish_ocr_stem(ocr_math_stem(page, figure_rect=figure_rect))
    kept_eqs = list(equation_images)
    if should_prefer_ocr_stem(prompt, ocr_prompt, bool(figure)):
        prompt = ocr_prompt
        equation_images = []
    elif prompt_looks_broken(prompt) and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        prompt = ocr_prompt
        equation_images = []
    elif figure and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        bare = re.sub(r"\{\{eq:\d+\}\}", "", prompt)
        if prompt_looks_broken(prompt) or len(ocr_prompt) > len(bare):
            prompt = ocr_prompt
            equation_images = []
    if (
        kept_eqs
        and not equation_images
        and re.search(r"(?i)\bgiven (system|equation)", prompt or "")
        and "{{eq:" not in (prompt or "")
    ):
        equation_images = kept_eqs
        prefix_parts = [f"{{{{eq:{i}}}}}" for i in range(len(equation_images))]
        prompt = "\n".join(prefix_parts + [prompt])
    prompt = polish_ocr_stem(prompt)
    if figure or re.search(r"(?i)\b(scatterplot|table|graph|figure)\b", prompt or ""):
        prompt = strip_chart_noise(prompt)
        prompt = polish_ocr_stem(prompt)
    if equation_images and "{{eq:" not in (prompt or ""):
        equation_images = []
    if (
        kept_eqs
        and re.search(r"(?i)expression \{\{eq:", built_prompt_snapshot or "")
        and ("{{eq:" not in (prompt or "") or prompt_looks_broken(prompt))
    ):
        prompt = built_prompt_snapshot
        equation_images = kept_eqs

    pdf_choices = extract_choices_text(text) if kind == "mc" else None
    choice_objs = extract_choice_objects(page, qid, pdf_choices) if kind == "mc" else []
    if kind == "spr" and not prompt:
        prompt = clean_text(extract_question_body(text)) or "Enter your answer."

    item = {
        "id": qid,
        "topic": skill or domain,
        "domain": domain,
        "skill": skill,
        "difficulty": difficulty,
        "pool": POOL,
        "prompt": prompt,
        "type": kind,
        "explanation": explanation,
        "pdf": pdf_url,
        "pdfPage": src_idx + 1,
    }
    preview = crop_math_pdf_preview(page, MATH_PDF_PREVIEW / f"{qid}.jpg")
    if preview:
        item["pdfPreview"] = f"/{preview}"
    if figure:
        item["figure"] = figure
        item["prompt"] = polish_ocr_stem(strip_chart_noise(item["prompt"]))
    if equation_images:
        item["equations"] = equation_images
    if kind == "mc":
        item["choices"] = choice_objs
        item["answer"] = ans
    else:
        item["choices"] = []
        item["acceptedAnswers"] = ans
        item["answer"] = ans[0] if ans else ""
    return item


def import_reading(existing: list[dict], skip_ids: set[str], skip_fp: set[str]) -> list[dict]:
    if not RW_SRC.exists():
        raise SystemExit(f"missing {RW_SRC}")
    PUBLIC_READING.mkdir(parents=True, exist_ok=True)
    READING_FIG.mkdir(parents=True, exist_ok=True)
    answered = PUBLIC_READING / "Summer-2026-Bank-2-Reading.pdf"
    unanswered = PUBLIC_READING / RW_UNANSWERED_NAME
    shutil.copy2(RW_SRC, answered)
    make_unanswered_pdf(RW_SRC, unanswered)
    pdf_url = f"/qbank/reading/{RW_UNANSWERED_NAME}"
    print(f"reading unanswered -> {unanswered.relative_to(ROOT)}")

    doc = fitz.open(RW_SRC)
    added = []
    for group in group_pages(doc):
        qid = group["id"].lower()
        if qid in skip_ids:
            print(f"  skip reading {qid}: duplicate id")
            continue
        item = build_reading_item(group, doc, pdf_url)
        if not item:
            continue
        fp = fingerprint(item.get("passage") or "", item.get("prompt") or "")
        if fp and fp in skip_fp:
            print(f"  skip reading {qid}: duplicate fingerprint")
            continue
        added.append(item)
        skip_ids.add(qid)
        if fp:
            skip_fp.add(fp)
        print(f"  + reading {qid} {item['domain']} / {item['skill']} {item['difficulty']}")
    doc.close()
    return added


def import_math(existing: list[dict], skip_ids: set[str], skip_fp: set[str]) -> list[dict]:
    if not MATH_SRC.exists():
        raise SystemExit(f"missing {MATH_SRC}")
    PUBLIC_MATH.mkdir(parents=True, exist_ok=True)
    MATH_FIG.mkdir(parents=True, exist_ok=True)
    MATH_CHOICE_IMG.mkdir(parents=True, exist_ok=True)
    MATH_PDF_PREVIEW.mkdir(parents=True, exist_ok=True)
    (ROOT / "public" / "qbank" / "math" / "equations").mkdir(parents=True, exist_ok=True)

    answered = PUBLIC_MATH / "Summer-2026-Bank-2-Math.pdf"
    unanswered = PUBLIC_MATH / MATH_UNANSWERED_NAME
    shutil.copy2(MATH_SRC, answered)
    make_unanswered_pdf(MATH_SRC, unanswered)
    pdf_url = f"/qbank/math/{MATH_UNANSWERED_NAME}"
    print(f"math unanswered -> {unanswered.relative_to(ROOT)}")

    src = fitz.open(MATH_SRC)
    unanswered_doc = fitz.open(unanswered)
    groups = group_pages(src)
    unanswered_by_id = {g["id"].lower(): g["pages"][0] for g in group_pages(unanswered_doc)}
    added = []
    for n, group in enumerate(groups, 1):
        qid = group["id"].lower()
        if qid in skip_ids:
            print(f"  skip math {qid}: duplicate id")
            continue
        src_idx = unanswered_by_id.get(qid, group["pages"][0])
        item = build_math_item(group, unanswered_doc, src_idx, pdf_url)
        if not item:
            continue
        fp = fingerprint(item.get("prompt") or "")
        if fp and fp in skip_fp:
            print(f"  skip math {qid}: duplicate fingerprint")
            continue
        added.append(item)
        skip_ids.add(qid)
        if fp:
            skip_fp.add(fp)
        preview = (item.get("prompt") or "").replace("\n", " | ")[:90]
        print(f"  + math {n}/{len(groups)} {qid} {item['domain']}: {preview}")
    src.close()
    unanswered_doc.close()
    return added


def main() -> int:
    reading = json.loads(READING_JSON.read_text(encoding="utf-8"))
    mathq = json.loads(MATH_JSON.read_text(encoding="utf-8"))
    reading = [q for q in reading if q.get("pool") != POOL]
    mathq = [q for q in mathq if q.get("pool") != POOL]

    skip_ids = {str(q.get("id") or "").lower() for q in reading + mathq}
    skip_fp = {
        fingerprint(q.get("passage") or "", q.get("prompt") or "")
        for q in reading + mathq
        if q.get("prompt")
    }
    skip_fp.discard("")

    print("=== Reading ===")
    added_r = import_reading(reading, skip_ids, skip_fp)
    print("=== Math ===")
    added_m = import_math(mathq, skip_ids, skip_fp)

    if not added_r and not added_m:
        print("no new questions")
        return 1

    merged_r = reading + added_r
    merged_m = mathq + added_m
    READING_JSON.write_text(json.dumps(merged_r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MATH_JSON.write_text(json.dumps(merged_m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rebuild_skill_counts(merged_r, READING_COUNTS)
    rebuild_skill_counts(merged_m, MATH_COUNTS)
    print(f"added reading={len(added_r)} math={len(added_m)}")
    print(f"totals reading={len(merged_r)} math={len(merged_m)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
