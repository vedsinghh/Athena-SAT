#!/usr/bin/env python3
"""Update mathQuestions.json from Program Readable PDF (with images).

- Updates prompts/choices from the readable WITH_IMAGES PDF
- Crops figures from the original Unanswered/Answered PDFs (not the full-card
  screenshots embedded in the readable PDF)
- Keeps original pdf / pdfPage / pdfPreview for the in-app PDF button
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SRC_PDF = Path("/Users/vedsingh/Downloads/Math_Questions_Program_Readable_WITH_IMAGES.pdf")
DEST_PDF = ROOT / "public/qbank/math/Math-Questions-Program-Readable.pdf"
FIG_DIR = ROOT / "public/qbank/math/figures"
JSON_PATH = ROOT / "src/data/mathQuestions.json"

# When a figure already shows the visual, keep the prompt to essentials only.
FIGURE_PROMPT_OVERRIDES = {
    "559476f4": "What is the frequency of data value 2 in this data set?",
    "5f10c095": (
        "The graph of a system of a linear equation and a quadratic equation is shown. "
        "A solution to the system is (x, y). What is a possible value of x?"
    ),
    "f123e039": (
        "The graph of a system of a linear and a quadratic equation is shown. "
        "Which system of equations is represented by the graph?"
    ),
    "080e75c2": (
        "The functions f and g model the number of participants, in thousands, in two different "
        "programs x years since 2010. The graphs of y = f(x) and y = g(x) are shown. "
        "Which of the following could represent functions f and g?"
    ),
    "18ac8354": (
        "The graph of line g is shown in the xy-plane. Line k is defined by 165x + py = w, "
        "where p and w are constants. If line k is graphed in this xy-plane, resulting in the graph "
        "of a system of two linear equations, the system of two linear equations will have infinitely "
        "many solutions. What is the value of p + w?"
    ),
    "d4572f55": (
        "For a linear relationship between x and y, the table gives three values of x and their "
        "corresponding values of y, where t is a constant. Which equation represents this relationship?"
    ),
    "f496d2c0": (
        "The table shows the distribution of rooms in a certain facility by seating capacity. "
        "If a room in this facility is selected at random, which of the following is closest to the "
        "probability of selecting a room that has a seating capacity greater than 65 seats, given that "
        "the room has a seating capacity of at least 18 seats?"
    ),
    "590d662d": (
        "While walking on a trail, Mary stopped to read a trail sign. The graph shows the total distance y, "
        "in meters, Mary had walked on the trail x minutes after leaving the trail sign. What distance, "
        "in meters, did Mary walk on the trail in the 10 minutes after leaving the trail sign?"
    ),
    "f6c18a66": (
        "For data set A, the table summarizes the distribution of the number of deliveries received by an "
        "office each day during a period of 11 days. The data value 13 was recorded in error and is removed "
        "from data set A to create data set B, which consists of the remaining 10 data values. Which "
        "statement best compares the median of data set A and the median of data set B?"
    ),
    "89ff6a0a": (
        "For 100 buttons, the table summarizes the distribution by group and diameter. One of these buttons "
        "will be selected at random. What is the probability of selecting a button with a diameter that is "
        "less than or equal to 30 millimeters, given that it is not in group 2? (Express your answer as a "
        "decimal or fraction, not as a percent.)"
    ),
    "1fe41c6b": (
        "The table gives the areas and perimeters of two similar rectangles, where n is a constant. "
        "What is the value of n?"
    ),
}


def clean_figured_prompt(prompt: str) -> str:
    p = str(prompt or "")
    # Drop transcribed TABLE dumps — the figure/image carries that data.
    p = re.sub(
        r"\s*TABLE:\s*.+?(?=(?:\n\s*)?(?:If |Which |What |One |A |The |In |For ))",
        " ",
        p,
        flags=re.I | re.S,
    )
    p = re.sub(r"\s*The frequencies are:[^.]*\.", "", p, flags=re.I)
    p = re.sub(
        r"(are shown\.|is shown\.)\s+"
        r"(?:The decreasing line.+?\.|The quadratic is.+?\.|The line passes through.+?\.|The line is horizontal.+?\.)+",
        r"\1",
        p,
        flags=re.I | re.S,
    )
    p = re.sub(
        r"(are shown\.|is shown\.)\s+The line passes through the origin.+?\.",
        r"\1",
        p,
        flags=re.I | re.S,
    )
    p = re.sub(
        r"(trail sign\.)\s+The line passes through.+?\.",
        r"\1",
        p,
        flags=re.I | re.S,
    )
    p = re.sub(r"[ \t]+\n", "\n", p)
    p = re.sub(r"\n{3,}", "\n\n", p)
    p = re.sub(r"[ \t]{2,}", " ", p)
    return p.strip()


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


def extract_page_image(page: fitz.Page, out_path: Path) -> bool:
    """Save the largest embedded image on the page as a JPEG figure."""
    infos = page.get_image_info(xrefs=True)
    if not infos:
        return False

    def area(info: dict) -> float:
        r = fitz.Rect(info["bbox"])
        return abs(r.width * r.height)

    infos = sorted(infos, key=area, reverse=True)
    best = infos[0]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    xref = best.get("xref") or 0

    if xref:
        try:
            pix = fitz.Pixmap(page.parent, xref)
            if pix.n - pix.alpha >= 4:  # CMYK
                pix = fitz.Pixmap(fitz.csRGB, pix)
            if pix.alpha:
                pix = fitz.Pixmap(pix, 0)
            pix.save(str(out_path))
            if out_path.exists() and out_path.stat().st_size > 500:
                return True
        except Exception as exc:
            print(f"warn: xref extract failed ({exc}); falling back to clip render")

    clip = fitz.Rect(best["bbox"])
    # pad slightly so axes/labels aren't clipped
    clip = fitz.Rect(clip.x0 - 4, clip.y0 - 4, clip.x1 + 4, clip.y1 + 4) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(2.8, 2.8), clip=clip, alpha=False)
    pix.save(str(out_path))
    return out_path.exists() and out_path.stat().st_size > 500


def main():
    if not SRC_PDF.exists():
        raise SystemExit(f"Missing source PDF: {SRC_PDF}")
    DEST_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_PDF, DEST_PDF)

    doc = fitz.open(str(DEST_PDF))
    id_to_page: dict[str, int] = {}
    id_to_has_image: dict[str, bool] = {}
    pages: list[str] = []
    for i in range(doc.page_count):
        page = doc[i]
        text = page.get_text()
        pages.append(text)
        m = re.search(r"QUESTION_ID:\s*(\S+)", text)
        if not m:
            continue
        qid = m.group(1)
        id_to_page[qid] = i + 1
        out_fig = FIG_DIR / f"{qid}.jpg"
        has_img = bool(page.get_images())
        if has_img:
            ok = extract_page_image(page, out_fig)
            id_to_has_image[qid] = ok
            if not ok:
                print(f"warn: failed to extract image for {qid}")
        else:
            id_to_has_image[qid] = False

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
                "has_image": id_to_has_image.get(qid, False),
            }

    data = json.loads(JSON_PATH.read_text())
    updated = 0
    figures_set = 0
    skipped = []
    for q in data:
        qid = q["id"]
        if qid not in parsed:
            skipped.append(qid)
            continue
        src = parsed[qid]
        prompt = src["prompt"]

        # Attach / refresh figure from the readable-with-images PDF when present.
        fig_path = FIG_DIR / f"{qid}.jpg"
        if src["has_image"] and fig_path.exists():
            q["figure"] = f"/qbank/math/figures/{qid}.jpg"
            figures_set += 1
            prompt = FIGURE_PROMPT_OVERRIDES.get(qid, clean_figured_prompt(prompt))
        elif q.get("figure"):
            # Keep existing figure; still clean descriptive dumps.
            prompt = FIGURE_PROMPT_OVERRIDES.get(qid, clean_figured_prompt(prompt))

        q["prompt"] = prompt
        if src["is_spr"] or not src["choices"]:
            q["choices"] = []
            q["type"] = "spr"
        else:
            # Prefer text choices from readable PDF; drop broken choice images when text exists.
            q["choices"] = src["choices"]
            q["type"] = "mc"
        # Keep original pdf / pdfPage / pdfPreview for the PDF viewer button.
        updated += 1

    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"updated {updated}; figures set {figures_set}; skipped {len(skipped)}: {skipped}")


if __name__ == "__main__":
    main()
