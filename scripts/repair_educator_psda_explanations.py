#!/usr/bin/env python3
"""Rebuild Educator Bank Problem-Solving and Data Analysis explanations from the bank PDF.

Math in Rationales is often drawn (not extractable text), so PDF text leaves blanks.
OCR the Rationale band and prefer the denser, non-hollow result.

Format: correct-answer block, blank line, then each incorrect Choice as its own paragraph.
"""

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

from extract_questions import clean_text  # noqa: E402

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Problem-Solving and Data Analysis 1.pdf")
DATA = ROOT / "src" / "data" / "mathQuestions.json"
POOL = "SAT Educator Bank 1"
DOMAIN = "Problem-Solving and Data Analysis"


def normalize_inequalities(s: str) -> str:
    return (s or "").replace("<=", "≤").replace(">=", "≥")


def expand_combined_incorrects(text: str) -> str:
    """Turn 'Choices A, B, and C are incorrect ...' into separate paragraphs."""
    out = text

    out = re.sub(
        r"Choices?\s+([A-D])\s*,\s*([A-D])\s*,?\s*and\s*([A-D])\s+are incorrect([^\n]*)",
        lambda m: "\n\n".join(
            f"Choice {L} is incorrect{m.group(4).rstrip('.')}.".replace("..", ".")
            if m.group(4).strip()
            else f"Choice {L} is incorrect and may result from conceptual or calculation errors."
            for L in (m.group(1).upper(), m.group(2).upper(), m.group(3).upper())
        ),
        out,
        flags=re.I,
    )
    out = re.sub(
        r"Choices?\s+([A-D])\s+and\s+([A-D])\s+are incorrect([^\n]*)",
        lambda m: "\n\n".join(
            f"Choice {L} is incorrect{m.group(3).rstrip('.')}.".replace("..", ".")
            if m.group(3).strip()
            else f"Choice {L} is incorrect and may result from conceptual or calculation errors."
            for L in (m.group(1).upper(), m.group(2).upper())
        ),
        out,
        flags=re.I,
    )
    return out


def format_explanation(raw: str) -> str:
    text = clean_text(raw or "")
    text = normalize_inequalities(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = expand_combined_incorrects(text)
    parts = re.split(r"(?=\bChoice\s+[A-D]\s+is incorrect\b)", text, flags=re.I)
    parts = [p.strip() for p in parts if p and p.strip()]
    if len(parts) <= 1:
        return text.strip()
    return "\n\n".join(parts)


def fix_common_ocr(text: str) -> str:
    """Light post-OCR cleanup for PSDA rationales."""
    if not text:
        return text
    t = text
    # Superscript / unit glyphs
    t = t.replace("cm?", "cm²").replace("cm®", "cm³").replace("m®", "m³")
    t = t.replace("cm°", "cm³").replace("m°", "m³")
    t = re.sub(r"\bcm3\b", "cm³", t)
    t = re.sub(r"\bm3\b", "m³", t)
    t = re.sub(r"\bcm2\b", "cm²", t)
    # Italic ℓ / l in volume formulas often OCR'd as ?, 7, |, @, 1
    t = re.sub(r"\bV\s*=\s*[?|@1]\s*wh\b", "V = lwh", t)
    t = re.sub(r"\bV\s*=\s*[?|@1]wh\b", "V = lwh", t)
    t = re.sub(r"\bwhere\s+Z\s+is the length\b", "where l is the length", t)
    t = re.sub(r"\bSubstituting\s+(\d+)\s+for\s+7\b", r"Substituting \1 for l", t)
    t = re.sub(r"\bfor\s+7,\s*", "for l, ", t)
    t = re.sub(r"\bfor hin\b", "for h in", t)
    t = re.sub(r"\bV\s*=\s*nr\^?2h\b", "V = πr²h", t, flags=re.I)
    t = re.sub(r"\bV\s*=\s*7r\^?2h\b", "V = πr²h", t)
    t = re.sub(r"\bV\s*=\s*mr\^?2h\b", "V = πr²h", t, flags=re.I)
    t = re.sub(r"\bA\s*=\s*nr\^?2\b", "A = πr²", t, flags=re.I)
    t = re.sub(r"\bC\s*=\s*2nr\b", "C = 2πr", t, flags=re.I)
    t = re.sub(r"\bC\s*=\s*27r\b", "C = 2πr", t)
    # Angle / triangle OCR
    t = re.sub(r"\bmeasure of Z([A-Z]{1,4})\b", r"measure of ∠\1", t)
    t = re.sub(r"(?<![A-Za-z])Z([A-Z]{2,4})(?![A-Za-z])", r"∠\1", t)
    t = re.sub(r"\bIn A([A-Z]{3})\b", r"In △\1", t)
    # Pi often OCR'd oddly
    t = re.sub(r"\bn\s*r\^?2\b", "πr²", t, flags=re.I)
    t = re.sub(r"\b7r\b", "πr", t)
    t = re.sub(r"\bnr\b", "πr", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def ocr_rationale(page: fitz.Page) -> str:
    """OCR from Rationale header to bottom of page."""
    hits = [h for h in page.search_for("Rationale") if h.x0 < 120]
    if not hits:
        return ""
    r0 = hits[-1]
    clip = fitz.Rect(12, r0.y0 + 10, page.rect.width - 12, page.rect.height - 8)
    if clip.height < 20:
        return ""
    pix = page.get_pixmap(matrix=fitz.Matrix(3.2, 3.2), clip=clip, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    candidates = []
    for psm in (6, 4):
        txt = pytesseract.image_to_string(img, config=f"--psm {psm}")
        candidates.append(txt)
    text = max(candidates, key=lambda t: len(re.sub(r"\s+", "", t)))
    text = clean_text(text)
    text = re.split(r"\nQuestion ID:", text, maxsplit=1)[0].strip()
    text = re.sub(r"(?i)\bRationale\b\s*", "", text).strip()
    return text


def pdf_text_rationale(page: fitz.Page) -> str:
    t = page.get_text() or ""
    m = re.search(r"\nRationale\n([\s\S]*)$", t)
    if not m:
        return ""
    return clean_text(m.group(1))


def looks_hollow(text: str) -> bool:
    """Detect missing math slots (blank where a digit/variable should be)."""
    if not text or len(text) < 40:
        return True
    # Empty answer / empty formula slots: "is ." "yields ," "formula ,"
    holes = len(
        re.findall(
            r"(?i)\b(yields|equals|answer is|formula|substituting|represents)\s*[.,]",
            text,
        )
    )
    holes += len(re.findall(r"(?i)\b(is|of|for|by|as)\s+[.,](?!\d)", text))
    # Doubled commas: "volume, , of" / "for , for"
    holes += len(re.findall(r",\s*,", text))
    if holes >= 3:
        return True
    if re.search(r"(?i)^The correct answer is\s*[.,]\s", text):
        return True
    # Units with no preceding number: "length of meters"
    if (
        len(re.findall(r"(?i)\bof\s+(meters|units|centimeters|feet|inches)\b", text)) >= 2
        and len(re.findall(r"\d", text)) < 2
    ):
        return True
    return False


def prefer_better(a: str, b: str) -> str:
    """Prefer the less-hollow, longer rationale."""
    if not a:
        return b
    if not b:
        return a
    ha, hb = looks_hollow(a), looks_hollow(b)
    if ha and not hb:
        return b
    if hb and not ha:
        return a

    def score(t: str) -> float:
        return (
            len(t)
            + 8 * len(re.findall(r"[=+\-*/^√π∠△]", t))
            + 4 * len(re.findall(r"\d", t))
            - 20 * (1 if looks_hollow(t) else 0)
            - 10 * len(re.findall(r",\s*,", t))
        )

    return a if score(a) >= score(b) else b


def main() -> None:
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not BANK_PDF.exists():
        raise SystemExit(f"Missing {BANK_PDF}")
    bank = fitz.open(BANK_PDF)
    index: dict[str, int] = {}
    for i, page in enumerate(bank):
        m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", page.get_text() or "", re.I)
        if m:
            index[m.group(1).lower()] = i

    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = []
    still_hollow = []
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        qid = q["id"]
        if only and qid not in only:
            continue
        if qid not in index:
            print(f"skip missing page {qid}")
            continue
        page = bank[index[qid]]
        text_r = pdf_text_rationale(page)
        ocr_r = ocr_rationale(page)
        best = prefer_better(text_r, ocr_r)
        existing = q.get("explanation") or ""
        best = prefer_better(best, existing)
        formatted = format_explanation(fix_common_ocr(best))
        if formatted and formatted != existing:
            q["explanation"] = formatted
            touched.append(qid)
        final = q.get("explanation") or formatted
        if looks_hollow(final):
            still_hollow.append(qid)
        print(
            f"{qid}: text={len(text_r)} ocr={len(ocr_r)} final={len(final)} "
            f"{'HOLLOW' if looks_hollow(final) else 'ok'}"
        )

    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nUpdated {len(touched)} explanations")
    print(f"Still hollow ({len(still_hollow)}): {still_hollow}")


if __name__ == "__main__":
    main()
