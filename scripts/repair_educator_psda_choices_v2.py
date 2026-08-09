#!/usr/bin/env python3
"""OCR MC answer choices from PSDA PDF pages into text (replace image-only choices)."""

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

from extract_questions import clean_text, extract_choices_text, find_label_rect, group_pages  # noqa: E402

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Problem-Solving and Data Analysis 1.pdf")
DATA = ROOT / "src" / "data" / "mathQuestions.json"
POOL = "SAT Educator Bank 1"
DOMAIN = "Problem-Solving and Data Analysis"


def ocr_clip(page: fitz.Page, clip: fitz.Rect, scale: float = 4.0) -> str:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img).filter(ImageFilter.SHARPEN)
    txt = pytesseract.image_to_string(img, config="--psm 6")
    return clean_text(txt)


def normalize_choice(text: str) -> str:
    t = clean_text(text or "")
    t = t.replace("\n", " ")
    t = re.sub(r"^[A-D][\.)\:]\s*", "", t)
    t = t.replace("<=", "≤").replace(">=", "≥")
    t = t.replace("—", "-").replace("–", "-")
    t = re.sub(r"\s{2,}", " ", t).strip()
    # common OCR: degrees / percent glued
    t = re.sub(r"(\d)\s*%", r"\1%", t)
    return t


def looks_bad(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if "between and" in t or re.search(r"\band\s+\.\s*$", t):
        return True
    # mostly garbage glyphs
    letters = len(re.findall(r"[A-Za-z]", t))
    if letters >= 3 and re.search(r"[|]{1,}|§", t):
        return True
    return False


def ocr_choices_from_page(page: fitz.Page) -> list[str] | None:
    """Crop each A/B/C/D band between Answer and Correct Answer/Rationale."""
    # Find letter markers
    markers = {}
    for letter in "ABCD":
        hits = []
        for pat in (f"{letter}.", f"{letter})"):
            for h in page.search_for(pat):
                if h.x0 < 80:
                    hits.append(h)
        if hits:
            markers[letter] = min(hits, key=lambda r: r.y0)
    if len(markers) < 4:
        return None

    end_y = page.rect.height - 8
    for lab in ("Correct Answer", "Rationale"):
        for h in page.search_for(lab):
            if h.x0 < 120 and h.y0 > markers["A"].y0:
                end_y = min(end_y, h.y0 - 2)

    ordered = [(L, markers[L]) for L in "ABCD"]
    out = []
    for i, (L, rect) in enumerate(ordered):
        y0 = rect.y0 - 1
        y1 = ordered[i + 1][1].y0 - 2 if i < 3 else end_y
        if y1 <= y0 + 4:
            y1 = y0 + 22
        clip = fitz.Rect(max(8, rect.x0 - 2), y0, page.rect.width - 10, y1)
        raw = ocr_clip(page, clip)
        # strip the leading letter line
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if lines and re.match(rf"^{L}[\.)]?", lines[0], re.I):
            lines = lines[1:] or lines
        text = normalize_choice(" ".join(lines))
        # also try stripping letter from joined
        text = re.sub(rf"^{L}[\.)\:]\s*", "", text)
        out.append(text)
    if len(out) == 4 and not all(looks_bad(t) for t in out):
        return out
    return out if all(str(t).strip() for t in out) else None


def needs_fix(q: dict) -> bool:
    if q.get("type") != "mc":
        return False
    ch = q.get("choices") or []
    if len(ch) != 4:
        return True
    texts = []
    for c in ch:
        if isinstance(c, dict):
            texts.append((c.get("text") or "").strip())
            if c.get("image") and not (c.get("text") or "").strip():
                return True
        else:
            texts.append(str(c or "").strip())
    return any(looks_bad(t) for t in texts)


def main() -> None:
    bank = fitz.open(BANK_PDF)
    groups = {g["id"]: g for g in group_pages(bank)}
    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = 0
    still_bad = []
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        if not needs_fix(q):
            continue
        g = groups.get(q["id"])
        if not g:
            still_bad.append(q["id"])
            continue
        page = bank[g["pages"][0]]
        # 1) PDF extractable text
        pdf_choices = extract_choices_text(g["text"])
        chosen = None
        if pdf_choices and len(pdf_choices) == 4 and all(str(t).strip() for t in pdf_choices):
            chosen = [normalize_choice(t) for t in pdf_choices]
        # 2) OCR page bands
        if not chosen or any(looks_bad(t) for t in chosen):
            ocr = ocr_choices_from_page(page)
            if ocr and sum(1 for t in ocr if not looks_bad(t)) >= sum(1 for t in (chosen or []) if not looks_bad(t)):
                chosen = ocr
        if chosen and all(str(t).strip() for t in chosen):
            q["choices"] = [{"text": t} for t in chosen]
            touched += 1
            flag = "BAD" if any(looks_bad(t) for t in chosen) else "ok"
            print(f"{q['id']}: {flag} {chosen}")
            if flag == "BAD":
                still_bad.append(q["id"])
        else:
            still_bad.append(q["id"])
            print(f"fail {q['id']}: {chosen}")

    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {touched}; still rough {len(still_bad)}: {still_bad}")


if __name__ == "__main__":
    main()
