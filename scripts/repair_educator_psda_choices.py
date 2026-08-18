#!/usr/bin/env python3
"""Convert PSDA Educator Bank image-only MC choices to text via OCR / PDF text."""

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

from extract_questions import clean_text, extract_choices_text, group_pages  # noqa: E402

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Problem-Solving and Data Analysis 1.pdf")
DATA = ROOT / "src" / "data" / "mathQuestions.json"
POOL = "E. Bank"
DOMAIN = "Problem-Solving and Data Analysis"
PUBLIC = ROOT / "public"


def ocr_image(path: Path) -> str:
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img).filter(ImageFilter.SHARPEN)
    # try a couple modes
    cands = [
        pytesseract.image_to_string(img, config="--psm 6"),
        pytesseract.image_to_string(img, config="--psm 7"),
    ]
    text = max(cands, key=lambda t: len(re.sub(r"\s+", "", t)))
    text = clean_text(text)
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s{2,}", " ", text)
    # drop leading choice letters if present
    text = re.sub(r"^[A-D][\.)]\s*", "", text)
    return text.strip()


def normalize_choice(text: str) -> str:
    t = text or ""
    t = t.replace("<=", "≤").replace(">=", "≥")
    t = t.replace("—", "-").replace("–", "-")
    # common OCR for percent / pi
    t = re.sub(r"\s*%", "%", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


def main() -> None:
    bank = fitz.open(BANK_PDF)
    index = {}
    for g in group_pages(bank):
        index[g["id"]] = g

    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = []
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN or q.get("type") != "mc":
            continue
        choices = q.get("choices") or []
        if len(choices) != 4:
            continue
        texts = [(c.get("text") if isinstance(c, dict) else str(c or "")) or "" for c in choices]
        imgs = [(c.get("image") if isinstance(c, dict) else None) for c in choices]
        if not (all(not t.strip() for t in texts) and any(imgs)):
            # also fill partial empties when image present
            if not any((not (texts[i] or "").strip()) and imgs[i] for i in range(4)):
                continue

        # Prefer extractable PDF choice text
        g = index.get(q["id"])
        pdf_choices = extract_choices_text(g["text"]) if g else None
        new_texts = [None] * 4
        if pdf_choices and len(pdf_choices) == 4 and all(str(t).strip() for t in pdf_choices):
            new_texts = [normalize_choice(str(t)) for t in pdf_choices]
        else:
            for i, (txt, img) in enumerate(zip(texts, imgs)):
                if txt.strip():
                    new_texts[i] = normalize_choice(txt)
                    continue
                if not img:
                    continue
                rel = str(img).lstrip("/")
                path = PUBLIC / rel
                if not path.exists():
                    # try without leading qbank path quirks
                    path = ROOT / "public" / rel
                if path.exists():
                    new_texts[i] = normalize_choice(ocr_image(path))

        if all(new_texts) and all(str(t).strip() for t in new_texts):
            q["choices"] = [{"text": t} for t in new_texts]
            touched.append(q["id"])
            print(f"{q['id']}: {new_texts}")
        else:
            print(f"partial {q['id']}: {new_texts}")

    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {len(touched)} questions to text choices")


if __name__ == "__main__":
    main()
