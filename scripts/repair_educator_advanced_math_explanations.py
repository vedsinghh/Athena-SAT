#!/usr/bin/env python3
"""Rebuild Educator Bank Advanced Math explanations from the bank PDF.

- OCR the Rationale band (math glyphs are often drawings, not extractable text)
- Format: correct-answer block, blank line, then each incorrect Choice as its own paragraph
- Expand combined "Choices A, B, and C are incorrect..." lines
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

from extract_questions import clean_text, find_label_rect  # noqa: E402

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Advanced Math 1.pdf")
DATA = ROOT / "src" / "data" / "mathQuestions.json"
POOL = "SAT Educator Bank 1"
DOMAIN = "Advanced Math"


def normalize_inequalities(s: str) -> str:
    return (s or "").replace("<=", "≤").replace(">=", "≥")


def expand_combined_incorrects(text: str) -> str:
    """Turn 'Choices A, B, and C are incorrect ...' into separate paragraphs."""
    out = text

    def repl(m: re.Match) -> str:
        letters = re.findall(r"[A-D]", m.group("letters"))
        rest = m.group("rest").strip()
        if not letters:
            return m.group(0)
        # drop leading "and may..." duplication issues
        if rest.lower().startswith("are incorrect"):
            rest = rest[len("are incorrect") :].lstrip(" .")
        body = rest if rest else "and may result from conceptual or calculation errors."
        if not body.lower().startswith("and ") and not body.lower().startswith("because"):
            if not body.lower().startswith("may "):
                # keep as trailing clause
                if body and not body.startswith("("):
                    body = body
        paras = []
        for L in letters:
            if body.lower().startswith("and ") or body.lower().startswith("because") or body.lower().startswith("may "):
                paras.append(f"Choice {L} is incorrect {body}".strip())
            elif body:
                paras.append(f"Choice {L} is incorrect. {body[0].upper() + body[1:] if body else body}".strip())
            else:
                paras.append(
                    f"Choice {L} is incorrect and may result from conceptual or calculation errors."
                )
        return "\n\n".join(paras)

    out = re.sub(
        r"Choices?\s+(?P<letters>(?:[A-D]\s*,\s*)+[A-D](?:\s*,?\s*and\s*[A-D])?|[A-D]\s+and\s+[A-D])\s+"
        r"(?P<rest>are incorrect[\s\S]*?)(?=(?:\n\nChoice\s+[A-D]\s+is incorrect)|\Z)",
        repl,
        out,
        flags=re.I,
    )
    # Simpler common form: "Choices A, B, and C are incorrect and may result from calculation errors."
    out = re.sub(
        r"Choices?\s+([A-D])\s*,\s*([A-D])\s*,?\s*and\s*([A-D])\s+are incorrect([^\n]*)",
        lambda m: "\n\n".join(
            f"Choice {L} is incorrect{m.group(4).rstrip('.') }.".replace("..", ".")
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
    # Split before each incorrect choice
    parts = re.split(r"(?=\bChoice\s+[A-D]\s+is incorrect\b)", text, flags=re.I)
    parts = [p.strip() for p in parts if p and p.strip()]
    if len(parts) <= 1:
        return text.strip()
    # Ensure correct block doesn't trail into incorrect without break
    return "\n\n".join(parts)


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
    # Try a couple PSM modes and pick the longer clean result
    candidates = []
    for psm in (6, 4):
        txt = pytesseract.image_to_string(img, config=f"--psm {psm}")
        candidates.append(txt)
    text = max(candidates, key=lambda t: len(re.sub(r"\s+", "", t)))
    text = clean_text(text)
    # Drop footer / next-question bleed
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
    if not text or len(text) < 40:
        return True
    holes = len(
        re.findall(
            r"(?i)\b(yields|equals|as|by|of|where|function|equation|expression|form|value|point|is|represents)\s*[.,]",
            text,
        )
    )
    if holes >= 3:
        return True
    if re.search(r"(?i)^The correct answer is\s*[.,]", text):
        return True
    if re.search(r"(?i)Choice [A-D] is correct\.\s*It'?s given that a rectangle has a length that is\s+times", text):
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
    # Prefer more math-like characters / digits
    def score(t: str) -> float:
        return len(t) + 8 * len(re.findall(r"[=+\-*/^√]", t)) + 4 * len(re.findall(r"\d", t)) - 20 * (
            1 if looks_hollow(t) else 0
        )

    return a if score(a) >= score(b) else b


def main() -> None:
    if not BANK_PDF.exists():
        raise SystemExit(f"Missing {BANK_PDF}")
    bank = fitz.open(BANK_PDF)
    index: dict[str, int] = {}
    for i, page in enumerate(bank):
        m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", page.get_text() or "", re.I)
        if m:
            index[m.group(1)] = i

    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = []
    still_hollow = []
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        qid = q["id"]
        if qid not in index:
            print(f"skip missing page {qid}")
            continue
        page = bank[index[qid]]
        text_r = pdf_text_rationale(page)
        ocr_r = ocr_rationale(page)
        best = prefer_better(text_r, ocr_r)
        # If still hollow, keep existing if it looks better
        existing = q.get("explanation") or ""
        best = prefer_better(best, existing)
        formatted = format_explanation(best)
        if formatted and formatted != existing:
            q["explanation"] = formatted
            touched.append(qid)
        if looks_hollow(formatted):
            still_hollow.append(qid)
        print(
            f"{qid}: text={len(text_r)} ocr={len(ocr_r)} final={len(formatted)} "
            f"{'HOLLOW' if looks_hollow(formatted) else 'ok'}"
        )

    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nUpdated {len(touched)} explanations")
    print(f"Still hollow ({len(still_hollow)}): {still_hollow}")


if __name__ == "__main__":
    main()
