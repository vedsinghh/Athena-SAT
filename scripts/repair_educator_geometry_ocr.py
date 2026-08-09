#!/usr/bin/env python3
"""Recover skipped Geometry SPR items and patch hollow-glyph OCR."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402

from extract_questions import (  # noqa: E402
    MATH_FIG,
    MATH_PDF_PREVIEW,
    crop_math_figure,
    crop_math_pdf_preview,
    find_label_rect,
    group_pages,
)

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Geometry and Trignometry 1.pdf")
DATA = ROOT / "src" / "data"
POOL = "SAT Educator Bank 1"
DOMAIN = "Geometry and Trigonometry"
UNANSWERED_URL = "/qbank/math/Educator-Bank-1-Geometry-Trigonometry-Unanswered.pdf"

# Skipped because Correct Answer label had hollow glyphs (answer only in Rationale).
RECOVER = {
    "f88f27e5": {
        "prompt": "Intersecting lines r, s, and t are shown below.\nWhat is the value of x?",
        "skill": "Lines, angles, and triangles",
        "difficulty": "Hard",
        "type": "spr",
        "answer": "97",
        "acceptedAnswers": ["97"],
        "explanation": (
            "The correct answer is 97. The intersecting lines form a triangle, and the angle with "
            "measure of x° is an exterior angle of this triangle. The measure of an exterior angle of "
            "a triangle is equal to the sum of the measures of the two nonadjacent interior angles of "
            "the triangle. One angle has measure of 23° and the other, which is supplementary to the "
            "angle with measure 106°, has measure of 180° - 106° = 74°. Therefore, the value of x is "
            "23 + 74 = 97."
        ),
        "needs_figure": True,
    },
    "947a3cde": {
        "prompt": (
            "In the figure above, MQ and NR intersect at point P, NP = QP, and MP = PR. What is the "
            "measure, in degrees, of angle QMR? (Disregard the degree symbol when gridding your answer.)"
        ),
        "skill": "Lines, angles, and triangles",
        "difficulty": "Hard",
        "type": "spr",
        "answer": "30",
        "acceptedAnswers": ["30"],
        "explanation": (
            "The correct answer is 30. It is given that the measure of angle QPR is 60°. Angle MPR and "
            "angle QPR are collinear and therefore are supplementary angles, so the measure of angle "
            "MPR is 120°. Since MP = PR, triangle MPR is isosceles, so angle QMR and angle NRM are "
            "congruent. The sum of those two angles is 60°, so each measures 30°."
        ),
        "needs_figure": True,
    },
    "ec5d4823": {
        "prompt": (
            "What is the volume, in cubic centimeters, of a right rectangular prism that has a length "
            "of 4 centimeters, a width of 9 centimeters, and a height of 10 centimeters?"
        ),
        "skill": "Area and volume",
        "difficulty": "Medium",
        "type": "spr",
        "answer": "360",
        "acceptedAnswers": ["360"],
        "explanation": (
            "The correct answer is 360. The volume of a right rectangular prism is calculated by "
            "multiplying its dimensions: length, width, and height. Multiplying the values given for "
            "these dimensions yields a volume of (4)(9)(10) = 360 cubic centimeters."
        ),
        "needs_figure": False,
    },
    "bd87bc09": {
        "prompt": (
            "Triangle ABC above is a right triangle, and sin(B) = 5/13. What is the length of side BC?"
        ),
        "skill": "Right triangles and trigonometry",
        "difficulty": "Hard",
        "type": "spr",
        "answer": "24",
        "acceptedAnswers": ["24"],
        "explanation": (
            "The correct answer is 24. The sine of an acute angle in a right triangle is the ratio of "
            "the length of the opposite side to the length of the hypotenuse. For angle B, "
            "sin(B) = AC/AB. Given AB = 26 and sin(B) = 5/13, it follows that 5/13 = AC/26, so AC = 10. "
            "By the Pythagorean theorem, 26^2 = 10^2 + BC^2, so BC^2 = 576 and BC = 24."
        ),
        "needs_figure": True,
    },
}

PROMPT_FIXES = {
    "f67e4efc": {
        "prompt": (
            "A right circular cylinder has a volume of 45π. If the height of the cylinder is 5, "
            "what is the radius of the cylinder?"
        ),
        "choices": [{"text": "3"}, {"text": "4.5"}, {"text": "9"}, {"text": "40"}],
        "answer": 0,
    },
    "096c7ef5": {
        "prompt": (
            "The three points shown define a circle. The circumference of this circle is kπ, "
            "where k is a constant. What is the value of k?"
        ),
    },
    "b2528e6b": {
        "prompt": (
            "The three points shown define a circle. The circumference of this circle is kπ, "
            "where k is a constant. What is the value of k?"
        ),
    },
    "2bddbc1b": {
        "prompt": "What is the value of cos A in the triangle shown?",
        "choices": [
            {"text": "42/41"},
            {"text": "41/42"},
            {"text": "1/42"},
            {"text": "1/41"},
        ],
    },
    "38517165": {
        "prompt": (
            "A circle has a circumference of 31π centimeters. What is the diameter, in centimeters, "
            "of the circle?"
        ),
        "answer": "31",
        "acceptedAnswers": ["31"],
    },
    "6b4707aa": {
        "prompt": (
            "(x + 5)^2 + (y - 5)^2 = 25\n"
            "Circle A in the xy-plane has the equation above. Circle B has the same center as circle A. "
            "The radius of circle B is twice the radius of circle A. The equation defining circle B in "
            "the xy-plane is (x + 5)^2 + (y - 5)^2 = k, where k is a constant. What is the value of k?"
        ),
        "answer": "100",
        "acceptedAnswers": ["100"],
    },
    "b8a225ff": {
        "prompt": (
            "(x + 5)^2 + (y - 5)^2 = 4\n"
            "Circle A in the xy-plane has the equation above. Circle B has the same center as circle A. "
            "The radius of circle B is twice the radius of circle A. The equation defining circle B in "
            "the xy-plane is (x + 5)^2 + (y - 5)^2 = k, where k is a constant. What is the value of k?"
        ),
    },
}


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
    (DATA / "mathSkillCounts.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    answered = fitz.open(BANK_PDF)
    groups = {g["id"]: g for g in group_pages(answered)}
    qs = json.loads((DATA / "mathQuestions.json").read_text(encoding="utf-8"))
    by = {q["id"]: q for q in qs}
    existing_ids = set(by)

    # Generic π OCR cleanup across educator geometry
    pi_subs = [
        (r"\bJT\b", "π"),
        (r"\bjt\b", "π"),
        (r"\bk77\b", "kπ"),
        (r"\bkis a\b", "k is a"),
        (r"\b317 centimeters\b", "31π centimeters"),
        (r"\b45 JT\b", "45π"),
        (r"\b43 JT\b", "45π"),
        (r"\bf cos\b", "cos"),
        (r"\bzy-plane\b", "xy-plane"),
        (r"\(z \+ 5\)", "(x + 5)"),
        (r"\(y—5\)", "(y - 5)"),
        (r"\(y-5\)°", "(y - 5)^2"),
        (r"\(y—5\)°", "(y - 5)^2"),
        (r"\)\" \+", ")^2 +"),
        (r"\)° =", ")^2 ="),
    ]

    patched = 0
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        p = q.get("prompt") or ""
        orig = p
        for pat, rep in pi_subs:
            p = re.sub(pat, rep, p)
        if p != orig:
            q["prompt"] = p
            patched += 1

    for qid, fix in PROMPT_FIXES.items():
        if qid not in by:
            print("missing for fix", qid)
            continue
        by[qid].update(fix)
        print("fixed", qid)

    # Recover skipped items
    for qid, meta in RECOVER.items():
        if qid in existing_ids:
            print("already have", qid)
            continue
        g = groups[qid]
        page = answered[g["pages"][0]]
        figure = None
        if meta["needs_figure"]:
            figure, _ = crop_math_figure(page, MATH_FIG / f"{qid}.jpg", g["text"])
            if not figure:
                # fallback: crop Question → Rationale band drawings
                q = find_label_rect(page, "Question")
                end = page.rect.height
                for lab in ("Rationale", "Correct Answer", "Answer"):
                    for hit in page.search_for(lab):
                        if hit.x0 < 120 and hit.y0 > (q.y1 if q else 0):
                            end = min(end, hit.y0)
                if q:
                    # wide crop of figure region
                    from extract_questions import render_clip

                    clip = fitz.Rect(40, q.y1 + 4, 520, end - 4)
                    rel = render_clip(page, MATH_FIG / f"{qid}.jpg", clip, scale=2.8)
                    if rel:
                        figure = f"/{rel}" if not str(rel).startswith("/") else rel
        preview = crop_math_pdf_preview(page, MATH_PDF_PREVIEW / f"{qid}.jpg")
        item = {
            "id": qid,
            "topic": meta["skill"],
            "domain": DOMAIN,
            "skill": meta["skill"],
            "difficulty": meta["difficulty"],
            "pool": POOL,
            "prompt": meta["prompt"],
            "type": meta["type"],
            "explanation": meta["explanation"],
            "pdf": UNANSWERED_URL,
            "pdfPage": g["pages"][0] + 1,
            "choices": [],
            "acceptedAnswers": meta["acceptedAnswers"],
            "answer": meta["answer"],
        }
        if preview:
            item["pdfPreview"] = f"/{preview}" if not str(preview).startswith("/") else preview
        if figure:
            item["figure"] = figure if str(figure).startswith("/") else f"/{figure}"
        qs.append(item)
        by[qid] = item
        print("recovered", qid, "figure", bool(figure))

    (DATA / "mathQuestions.json").write_text(
        json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    update_skill_counts(qs)
    geo = [q for q in qs if q.get("pool") == POOL and q.get("domain") == DOMAIN]
    print(f"Educator Geometry total: {len(geo)} (generic π patches: {patched})")
    print(f"Total math questions: {len(qs)}")


if __name__ == "__main__":
    main()
