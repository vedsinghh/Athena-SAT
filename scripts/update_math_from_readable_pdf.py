#!/usr/bin/env python3
"""Update mathQuestions.json prompts/choices from Program Readable PDF. Keeps figures."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SRC_PDF = Path("/Users/vedsingh/Downloads/Math_Questions_Program_Readable_FIXED.pdf")
DEST_PDF = ROOT / "public/qbank/math/Math-Questions-Program-Readable.pdf"
PDF_URL = "/qbank/math/Math-Questions-Program-Readable.pdf"
JSON_PATH = ROOT / "src/data/mathQuestions.json"


def parse_block(block: str):
    mid = re.search(r"QUESTION_ID:\s*(\S+)", block)
    qid = mid.group(1) if mid else None
    qm = re.search(
        r"QUESTION:\s*(.*?)\s*(?:ANSWER_CHOICES:|CORRECT_ANSWER:|ACCEPTED_ANSWERS:|END_QUESTION)",
        block,
        re.S,
    )
    prompt = (qm.group(1).strip() if qm else "")
    prompt = re.sub(r"[ \t]+\n", "\n", prompt)
    prompt = re.sub(r"\n{3,}", "\n\n", prompt).strip()

    cm = re.search(
        r"ANSWER_CHOICES:\s*(.*?)\s*(?:CORRECT_ANSWER:|ACCEPTED_ANSWERS:|END_QUESTION)",
        block,
        re.S,
    )
    choices_raw = cm.group(1).strip() if cm else ""
    choices = []
    is_spr = bool(re.search(r"\[FREE_RESPONSE\]", choices_raw))
    if not is_spr and choices_raw:
        for line in choices_raw.splitlines():
            m = re.match(r"^([A-D])\.\s*(.*)$", line.strip())
            if m:
                choices.append({"text": m.group(2).strip()})
    return qid, prompt, choices, is_spr


def main():
    if not SRC_PDF.exists():
        raise SystemExit(f"Missing source PDF: {SRC_PDF}")
    DEST_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_PDF, DEST_PDF)

    doc = fitz.open(DEST_PDF)
    id_to_page = {}
    pages = []
    for i in range(doc.page_count):
        text = doc[i].get_text()
        pages.append(text)
        m = re.search(r"QUESTION_ID:\s*(\S+)", text)
        if m:
            id_to_page[m.group(1)] = i + 1

    parts = [
        p.strip()
        for p in re.split(r"(?=QUESTION_ID:\s*)", "\n".join(pages))
        if p.strip().startswith("QUESTION_ID")
    ]
    parsed = {}
    for block in parts:
        qid, prompt, choices, is_spr = parse_block(block)
        if qid:
            parsed[qid] = {
                "prompt": prompt,
                "choices": choices,
                "is_spr": is_spr,
                "pdfPage": id_to_page.get(qid),
            }

    data = json.loads(JSON_PATH.read_text())
    updated = 0
    skipped = []
    for q in data:
        qid = q["id"]
        if qid not in parsed:
            skipped.append(qid)
            continue
        src = parsed[qid]
        q["prompt"] = src["prompt"]
        if src["is_spr"] or not src["choices"]:
            q["choices"] = []
            q["type"] = "spr"
        else:
            q["choices"] = src["choices"]
            q["type"] = "mc"
        q["pdf"] = PDF_URL
        if src["pdfPage"]:
            q["pdfPage"] = src["pdfPage"]
        q.pop("pdfPreview", None)
        updated += 1

    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"updated {updated}; skipped {len(skipped)}: {skipped}")


if __name__ == "__main__":
    main()
