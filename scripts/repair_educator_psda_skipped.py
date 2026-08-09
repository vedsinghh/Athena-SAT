#!/usr/bin/env python3
"""Recover PSDA Educator Bank items skipped because Correct Answer glyphs were hollow."""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import fitz
import pytesseract
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_questions import (  # noqa: E402
    MATH_FIG,
    MATH_PDF_PREVIEW,
    build_math_prompt,
    clean_text,
    crop_math_figure,
    crop_math_pdf_preview,
    extract_choice_objects,
    extract_choices_text,
    extract_explanation,
    group_pages,
    ocr_math_stem,
    parse_meta,
    polish_ocr_stem,
    strip_chart_noise,
)
from import_educator_bank_math_psda import (  # noqa: E402
    BANK_PDF,
    DATA,
    DOMAIN,
    POOL,
    UNANSWERED_NAME,
    UNANSWERED_URL,
    format_explanation,
    light_ocr_fixes,
    normalize_inequalities,
    strip_equation_slots,
    update_skill_counts,
)

SKIP_IDS = [
    "3f5398a6",
    "65c49824",
    "000259aa",
    "90eed2e5",
    "8e528129",
    "0231050d",
    "d4413871",
    "fea831fc",
    "07f2829b",
    "7ac5d686",
    "3638f413",
]


def ocr_region(page: fitz.Page, clip: fitz.Rect, scale: float = 3.5) -> str:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img).filter(ImageFilter.SHARPEN)
    return clean_text(pytesseract.image_to_string(img, config="--psm 6"))


def recover_answer(page: fitz.Page, text: str) -> tuple[str, object] | None:
    """Return ('mc', index) or ('spr', [answers])."""
    is_mc = bool(re.search(r"\nA\.\s", text))
    # Prefer rationale letter for MC
    m = re.search(r"Choice\s+([A-D])\s+is correct", text, re.I)
    if is_mc and m:
        return "mc", "ABCD".index(m.group(1).upper())

    # OCR Correct Answer band
    hits = [h for h in page.search_for("Correct Answer") if h.x0 < 120]
    ca_txt = ""
    if hits:
        r0 = hits[0]
        ca_txt = ocr_region(page, fitz.Rect(12, r0.y0 - 2, page.rect.width - 12, min(r0.y0 + 40, page.rect.height)))
    # Also OCR start of rationale for "The correct answer is …"
    rh = [h for h in page.search_for("Rationale") if h.x0 < 120]
    rat_txt = ""
    if rh:
        r0 = rh[-1]
        rat_txt = ocr_region(
            page,
            fitz.Rect(12, r0.y0 + 8, page.rect.width - 12, min(r0.y0 + 90, page.rect.height)),
        )

    blob = f"{ca_txt}\n{rat_txt}\n{text}"
    if is_mc:
        m = re.search(r"Choice\s+([A-D])\s+is correct", blob, re.I)
        if m:
            return "mc", "ABCD".index(m.group(1).upper())
        m = re.search(r"Correct Answer:\s*([A-D])\b", blob, re.I)
        if m:
            return "mc", "ABCD".index(m.group(1).upper())
        return None

    m = re.search(
        r"(?i)(?:Correct Answer:|The correct answer is)\s*([0-9][0-9,/.\s]*)",
        blob,
    )
    if not m:
        return None
    raw = m.group(1).strip().rstrip(".")
    # normalize
    raw = re.sub(r"\s+", "", raw)
    raw = raw.replace(",", "")
    # keep decimals
    if not re.fullmatch(r"\d+(\.\d+)?", raw):
        # try first number token
        m2 = re.search(r"\d+(?:\.\d+)?", raw)
        if not m2:
            return None
        raw = m2.group(0)
    answers = [raw]
    if "." in raw:
        # also accept without trailing zeros? keep as-is
        pass
    return "spr", answers


def build_recovered(g: dict, unanswered: fitz.Document, unanswered_by_id: dict[str, int], answered: fitz.Document) -> dict | None:
    qid = g["id"]
    text = g["text"]
    domain, skill, difficulty = parse_meta(text, "Math", [DOMAIN])
    domain = DOMAIN
    skill = skill or DOMAIN
    difficulty = difficulty or "Medium"

    src_idx = unanswered_by_id.get(qid, g["pages"][0])
    page_a = answered[g["pages"][0]]
    page_u = unanswered[src_idx] if qid in unanswered_by_id else page_a

    recovered = recover_answer(page_a, text)
    if not recovered:
        print(f"fail {qid}: could not recover answer")
        return None
    kind, ans = recovered

    explanation = format_explanation(extract_explanation(text))
    figure, figure_rect = crop_math_figure(page_u, MATH_FIG / f"{qid}.jpg", text)
    prompt, equation_images = build_math_prompt(page_u, text, figure_rect=figure_rect, qid=qid)
    ocr_prompt = polish_ocr_stem(ocr_math_stem(page_u, figure_rect=figure_rect))
    if ocr_prompt and len(ocr_prompt) > len(strip_equation_slots(prompt or "")):
        prompt = ocr_prompt
        equation_images = []
    prompt = polish_ocr_stem(prompt)
    if figure or re.search(r"(?i)\b(scatterplot|table|graph|figure)\b", prompt or ""):
        prompt = strip_chart_noise(prompt)
        prompt = polish_ocr_stem(prompt)
    if not equation_images:
        prompt = strip_equation_slots(prompt)
    prompt = light_ocr_fixes(normalize_inequalities(prompt))
    if not prompt.strip():
        print(f"fail {qid}: empty prompt")
        return None

    preview = crop_math_pdf_preview(page_u, MATH_PDF_PREVIEW / f"{qid}.jpg")
    item = {
        "id": qid,
        "topic": skill,
        "domain": DOMAIN,
        "skill": skill,
        "difficulty": difficulty,
        "pool": POOL,
        "prompt": prompt,
        "type": kind,
        "explanation": explanation,
        "pdf": UNANSWERED_URL,
        "pdfPage": src_idx + 1,
    }
    if preview:
        item["pdfPreview"] = f"/{preview}" if not str(preview).startswith("/") else preview
    if figure:
        item["figure"] = figure if str(figure).startswith("/") else f"/{figure}"
    if equation_images:
        item["equations"] = equation_images

    if kind == "mc":
        pdf_choices = extract_choices_text(text)
        choice_objs = extract_choice_objects(page_u, qid, pdf_choices)
        for c in choice_objs:
            if c.get("text"):
                c["text"] = normalize_inequalities(c["text"])
        item["choices"] = choice_objs
        item["answer"] = ans
    else:
        item["choices"] = []
        item["acceptedAnswers"] = ans
        item["answer"] = ans[0]

    print(f"recover {qid}: {kind} {ans} :: {(prompt or '')[:70].replace(chr(10), ' ')}")
    return item


def main() -> None:
    unanswered_path = ROOT / "public" / "qbank" / "math" / UNANSWERED_NAME
    answered = fitz.open(BANK_PDF)
    unanswered = fitz.open(unanswered_path)
    groups = {g["id"]: g for g in group_pages(answered)}
    unanswered_by_id = {g["id"]: g["pages"][0] for g in group_pages(unanswered)}

    qs = json.loads((DATA / "mathQuestions.json").read_text(encoding="utf-8"))
    existing = {q["id"] for q in qs}
    added = []
    for qid in SKIP_IDS:
        if qid in existing:
            print(f"skip {qid}: already present")
            continue
        g = groups.get(qid)
        if not g:
            print(f"skip {qid}: not in PDF")
            continue
        item = build_recovered(g, unanswered, unanswered_by_id, answered)
        if item:
            qs.append(item)
            added.append(qid)

    (DATA / "mathQuestions.json").write_text(
        json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    update_skill_counts(qs)
    print(f"Recovered {len(added)}: {added}")


if __name__ == "__main__":
    main()
