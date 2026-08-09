#!/usr/bin/env python3
"""Repair Educator Bank Geometry OCR: angles, triangles, stems, and simple choices."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

DATA = ROOT / "src/data/mathQuestions.json"
POOL = "SAT Educator Bank 1"
DOMAIN = "Geometry and Trigonometry"

# Screenshot / PDF ground-truth stem+choice fixes
HAND_FIXES: dict[str, dict] = {
    "6d99b141": {
        "prompt": (
            "In the figure, AC = CD. The measure of angle EBC is 45°, and the measure of "
            "angle ACD is 104°. What is the value of x?"
        ),
    },
    "9912e19f": {
        "prompt": (
            "Triangles EFG and JKL are congruent, where E, F, and G correspond to J, K, and L, "
            "respectively. The measure of angle E is 45° and the measure of angle F is 20°. "
            "What is the measure of angle J?"
        ),
        "choices": [
            {"text": "20°"},
            {"text": "45°"},
            {"text": "135°"},
            {"text": "160°"},
        ],
        "answer": 1,
    },
    "e10d8313": {
        "prompt": (
            "In the figure shown, points Q, R, S, and T lie on line segment PV, and line segment "
            "RU intersects line segment SX at point W. The measure of ∠SQX is 48°, the measure of "
            "∠SXQ is 86°, the measure of ∠SWU is 85°, and the measure of ∠VTU is 162°. What is the "
            "measure, in degrees, of ∠TUR?"
        ),
    },
    "33e29881": {
        "prompt": (
            "In right triangle RST, the sum of the measures of angle R and angle S is 90 degrees. "
            "The value of sin(R) is sqrt(15)/4. What is the value of cos(S)?"
        ),
        "choices": [
            {"text": "sqrt(15)/15"},
            {"text": "sqrt(15)/4"},
            {"text": "4sqrt(15)/15"},
            {"text": "sqrt(15)"},
        ],
        "answer": 1,
    },
    "cbe8ca31": {
        "prompt": (
            "In △XYZ, the measure of ∠X is 24° and the measure of ∠Y is 98°. "
            "What is the measure of ∠Z?"
        ),
        "choices": [
            {"text": "58°"},
            {"text": "74°"},
            {"text": "122°"},
            {"text": "212°"},
        ],
        "answer": 0,
    },
    "5a7e3b46": {
        "prompt": (
            "In △ABC, ∠B is a right angle and the length of BC is 136 millimeters. "
            "If cos A = 3/5, what is the length, in millimeters, of AB?"
        ),
        "choices": [
            {"text": "34"},
            {"text": "102"},
            {"text": "136"},
            {"text": "170"},
        ],
        "answer": 1,
    },
    "bcb66188": {
        "prompt": (
            "Triangle FGH is similar to triangle JKL, where angle F corresponds to angle J and "
            "angles G and K are right angles. If sin(F) = 308/317, what is the value of sin(J)?"
        ),
        "choices": [
            {"text": "75/317"},
            {"text": "308/317"},
            {"text": "317/308"},
            {"text": "317/75"},
        ],
        "answer": 1,
    },
    "babd7461": {
        "prompt": (
            "In the figure shown, triangle JKL is similar to triangle RST, where J corresponds to R "
            "and K corresponds to S. The length of JK is 15, and the perimeter of triangle JKL is 36. "
            "The length of RS is 135. What is the perimeter of triangle RST?"
        ),
    },
    "055aafe7": {
        "prompt": (
            "Triangle ABC is similar to triangle XYZ, where A, B, and C correspond to X, Y, and Z, "
            "respectively. In triangle ABC, the length of AB is 170 and the length of BC is 850. "
            "In triangle XYZ, the length of YZ is 60. What is the length of XY?"
        ),
    },
    "2d2cb85e": {
        "prompt": (
            "In the figure, RT = TU, the measure of angle VST is 29°, and the measure of angle RVS "
            "is 41°. What is the value of x?"
        ),
    },
    "901c3215": {
        "prompt": (
            "In triangles ABC and DEF, angles B and E each have measure 27° and angles C and F each "
            "have measure 41°. Which additional piece of information is sufficient to determine "
            "whether triangle ABC is congruent to triangle DEF?"
        ),
        "choices": [
            {"text": "The measure of angle A"},
            {"text": "The length of side AB"},
            {"text": "The lengths of sides BC and EF"},
            {"text": "No additional information is necessary."},
        ],
        "answer": 2,
    },
    "2f7c92ad": {
        "prompt": (
            "In the figure shown, triangle CAE is similar to triangle CBD. The measure of angle CBD "
            "is 57°, and AE = 26(BD). What is the measure of angle CAE?"
        ),
        "choices": [
            {"text": "(26·57)°"},
            {"text": "(26 + 57)°"},
            {"text": "57°"},
            {"text": "26°"},
        ],
        "answer": 2,
    },
    "b1e1c2f5": {
        "prompt": (
            "In right triangle ABC, angle C is the right angle and BC = 162. Point D on side AB is "
            "connected by a line segment with point E on side AC such that line segment DE is "
            "parallel to side BC and CE = 2AE. What is the length of line segment DE?"
        ),
    },
    "498d6795": {
        "prompt": (
            "In triangle ABC, angle B is a right angle. The length of side AB is 10sqrt(37) and the "
            "length of side BC is 24sqrt(37). What is the length of side AC?"
        ),
        "choices": [
            {"text": "14sqrt(37)"},
            {"text": "26sqrt(37)"},
            {"text": "34sqrt(37)"},
            {"text": "sqrt(34·37)"},
        ],
        "answer": 1,
    },
    "3b225698": {
        "prompt": (
            "Triangle XYZ is similar to triangle RST such that X, Y, and Z correspond to R, S, and T, "
            "respectively. The measure of ∠Z is 20° and 2XY = RS. What is the measure of ∠T?"
        ),
    },
    "a6dbad6b": {
        "prompt": (
            "In the figure above, lines ℓ and m are parallel, y = 20, and z = 60. What is the value of x?"
        ),
    },
    "81b664bc": {
        "prompt": (
            "In the figure above, AF, BE, and CD are parallel. Points B and E lie on AC and FD, "
            "respectively. If AB = 9, BC = 18.5, and FE = 8.5, what is the length of ED, to the "
            "nearest tenth?"
        ),
    },
    "902dc959": {
        "prompt": "In the figure above, what is the value of tan(A)?",
        "choices": [
            {"text": "20/29"},
            {"text": "21/29"},
            {"text": "20/21"},
            {"text": "21/20"},
        ],
        "answer": 2,
    },
    "4c95c7d4": {
        "prompt": (
            "A graphic designer is creating a logo for a company. The logo is shown in the figure above. "
            "The logo is in the shape of a trapezoid and consists of three congruent equilateral "
            "triangles. If the perimeter of the logo is 20 centimeters, what is the combined area of "
            "the shaded regions, in square centimeters, of the logo?"
        ),
        "choices": [
            {"text": "2sqrt(3)"},
            {"text": "4sqrt(3)"},
            {"text": "8sqrt(3)"},
            {"text": "16"},
        ],
        "answer": 2,
    },
    "740bf79f": {
        "prompt": "In the figure above, what is the length of NQ?",
    },
    "e0874bc2": {
        "prompt": (
            "The table gives the perimeters of similar triangles TUV and XYZ, where TU corresponds "
            "to XY. The length of TU is 18. What is the length of XY?"
        ),
        "choices": [
            {"text": "2"},
            {"text": "18"},
            {"text": "55"},
            {"text": "162"},
        ],
        "answer": 3,
    },
    "fc5ef8d3": {
        "prompt": (
            "The table gives the perimeters of similar triangles TUV and XYZ, where TU corresponds "
            "to XY. The length of TU is 6. What is the length of XY?"
        ),
        "choices": [
            {"text": "2"},
            {"text": "6"},
            {"text": "18"},
            {"text": "56"},
        ],
        "answer": 2,
    },
    "ebbf23ae": {
        "prompt": (
            "A circle in the xy-plane has a diameter with endpoints (2, 4) and (2, 14). An equation "
            "of this circle is (x - 2)^2 + (y - 9)^2 = r^2, where r is a positive constant. What is "
            "the value of r?"
        ),
    },
    "b0a72bdc": {
        "prompt": (
            "What is the diameter of the circle in the xy-plane with equation "
            "(x - 5)^2 + (y - 3)^2 = 16?"
        ),
    },
    "5252e606": {
        "prompt": (
            "The side length of a square is 55 centimeters (cm). What is the area, in cm², "
            "of the square?"
        ),
    },
    "bb560789": {
        "prompt": (
            "Triangle R has an area of 80 square centimeters (cm²). Square S has side lengths "
            "of 4 cm. What is the total area of triangle R and square S, in cm²?"
        ),
    },
    "96467fea": {
        "prompt": (
            "Circle N has a radius of 7 millimeters (mm). Circle M has an area of 64π mm². "
            "What is the total area, in mm², of circles N and M?"
        ),
        "choices": [
            {"text": "113π"},
            {"text": "92π"},
            {"text": "78π"},
            {"text": "15π"},
        ],
        "answer": 0,
    },
    "858fd1cf": {
        "prompt": (
            "A circle in the xy-plane has its center at (-1, 1). Line t is tangent to this circle "
            "at the point (5, -4). Which of the following points also lies on line t?"
        ),
    },
    "9adb86ed": {
        "prompt": (
            "Points Q and R lie on a circle with center P. The radius of this circle is 9 inches. "
            "Triangle PQR has a perimeter of 31 inches. What is the length, in inches, of QR?"
        ),
    },
    "a0369739": {
        "prompt": (
            "In triangle ABC, the measure of angle B is 90° and BD is an altitude of the triangle. "
            "The length of AB is 15 and the length of AC is 23 greater than the length of AB. "
            "What is the value of BC/BD?"
        ),
    },
    "a07ed090": {
        "prompt": (
            "The figure shown is a right circular cylinder with a radius of r and height of h. "
            "A second right circular cylinder (not shown) has a volume that is 392 times as large "
            "as the volume of the cylinder shown. Which of the following could represent the radius "
            "R, in terms of r, and the height H, in terms of h, of the second cylinder?"
        ),
        "choices": [
            {"text": "R = 8r and H = 7h"},
            {"text": "R = 8r and H = 49h"},
            {"text": "R = 7r and H = 8h"},
            {"text": "R = 49r and H = 8h"},
        ],
        "answer": 2,
    },
    "3b931fb0": {
        "prompt": (
            "A right circular cylinder has a volume of 377 cubic centimeters. The area of the base "
            "of the cylinder is 13 square centimeters. What is the height, in centimeters, of the "
            "cylinder?"
        ),
    },
    "51f26ce8": {
        "prompt": (
            "△QPR is similar to △STR. The lengths represented by ST, QP, PR, and QR in the figure "
            "are 14, 15, 20, and 25, respectively. What is the length of SR?"
        ),
    },
    "c8345903": {
        "prompt": (
            "The circle above has center O, the length of arc ADC is 5π, and x = 100. "
            "What is the length of arc ABC?"
        ),
        "choices": [
            {"text": "9π"},
            {"text": "13π"},
            {"text": "18π"},
            {"text": "(13/2)π"},
        ],
        "answer": 1,
    },
    "2266984b": {
        "prompt": (
            "The equation x^2 + 20x + y^2 + 16y = -20 defines a circle in the xy-plane. "
            "What are the coordinates of the center of the circle?"
        ),
    },
    "933fee1a": {
        "prompt": (
            "Triangles ABC and DEF are shown above. Which of the following is equal to the ratio "
            "BC/AB?"
        ),
        "choices": [
            {"text": "DE/DF"},
            {"text": "DF/DE"},
            {"text": "DF/EF"},
            {"text": "EF/DE"},
        ],
        "answer": 1,
    },
}


def fix_geo_ocr(text: str) -> str:
    """Normalize hollow-glyph OCR for Geometry bank stems/explanations."""
    if not text:
        return text
    t = text

    # Triangle symbol OCR'd as leading A before 3-letter names: In AABC, In AXYZ
    t = re.sub(r"\bIn A([A-Z]{3})\b", r"In △\1", t)
    t = re.sub(r"\bin A([A-Z]{3})\b", r"in △\1", t)
    t = re.sub(r"\btriangle A([A-Z]{3})\b", r"triangle \1", t, flags=re.I)
    # "In AXY Z" / "In AXYZ," spacing variants
    t = re.sub(r"\bIn A([A-Z]{2})\s+([A-Z])\b", r"In △\1\2", t)

    # Angle symbol OCR'd as Z before 2–4 letter angle names
    # Avoid turning ZZ alone when it's angle Z: "measure of ZZ" → "measure of ∠Z"
    t = re.sub(r"\bmeasure of Z([A-Z]{2,4})\b", r"measure of ∠\1", t)
    t = re.sub(r"\bmeasures of Z([A-Z]{2,4})\b", r"measures of ∠\1", t)
    t = re.sub(r"\bof Z([A-Z]{2,4})\b", r"of ∠\1", t)
    t = re.sub(r"(?<![A-Za-z])Z([A-Z]{2,4})(?![A-Za-z])", r"∠\1", t)
    # Single-letter angles: ZX, ZY, ZZ when preceded by "of " / "angle "
    t = re.sub(r"\bmeasure of Z([A-Z])\b", r"measure of ∠\1", t)
    t = re.sub(r"\bZ([A-Z])\s+is a right angle", r"∠\1 is a right angle", t)
    t = re.sub(r"\bZB\s*is\b", "∠B is", t)
    t = re.sub(r"\bZBis\b", "∠B is", t)

    # Common hollow / OCR junk in geo stems
    t = re.sub(r"\bS_X\b", "SX", t)
    t = re.sub(r"\bZS\._XQ\b", "∠SXQ", t)
    t = re.sub(r"\bZTU\s+R\b", "∠TUR", t)
    t = re.sub(r"AC = C['’]?D\b", "AC = CD", t)
    t = re.sub(r"\bJ&L\b", "JKL", t)
    t = re.sub(r"\bEF['’]G\b", "EFG", t)
    t = re.sub(r"\bangle Fis\b", "angle F is", t)
    t = re.sub(r"\bsin\(\s*f\s*\)", "sin(R)", t, flags=re.I)
    t = re.sub(r"\bis\s*~~\.?", "is sqrt(15)/4.", t)
    t = re.sub(r"\bcos A = \*\b", "cos A = 3/5", t)
    t = re.sub(r"\bRST’\b", "RST", t)
    t = re.sub(r"\band 7’\b", "and T", t)
    t = re.sub(r"\b2XY =\b", "2XY =", t)

    # Common OCR spacing / prime junk on triangle and angle names
    t = re.sub(r"\bJ\s+KL\b", "JKL", t)
    t = re.sub(r"\bJK\s+L\b", "JKL", t)
    t = re.sub(r"\bFG-\b", "FGH", t)
    t = re.sub(r"\bABis\b", "AB is", t)
    t = re.sub(r"\bangle Bis\b", "angle B is", t)
    t = re.sub(r"\bC['’]\b", "C", t)
    t = re.sub(r"\bF['’]\b", "F", t)
    t = re.sub(r"\bT['’]\b", "T", t)
    t = re.sub(r"\bBC['’]\b", "BC", t)
    t = re.sub(r"\bABC['’]\b", "ABC", t)
    t = re.sub(r"\bC['’]AF\b", "CAE", t)
    t = re.sub(r"\bRT['’]\b", "RT", t)
    t = re.sub(r"\bangle V\s+ST\b", "angle VST", t)
    t = re.sub(r"\bangle RV['’]S\b", "angle RVS", t)
    t = re.sub(r"\b10V\s*37\b", "10sqrt(37)", t)
    t = re.sub(r"\b24-?V\s*37\b", "24sqrt(37)", t)
    t = re.sub(r"\btanl,4\}\b", "tan(A)", t)
    t = re.sub(r"\(x\s*—\s*", "(x - ", t)
    t = re.sub(r"\(y\s*—\s*", "(y - ", t)
    t = re.sub(r"=\s*r°\b", "= r^2", t)
    t = re.sub(r"\bwhere ris\b", "where r is", t)
    t = t.replace("cm?", "cm²")

    # Cleanup doubled angle words
    t = re.sub(r"\bangle\s+∠", "∠", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


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
    (ROOT / "src/data/mathSkillCounts.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    qs = json.loads(DATA.read_text(encoding="utf-8"))
    by = {q["id"]: q for q in qs}

    # Optional batch choice conversions from sidecar file
    choice_map: dict[str, list[str]] = {}
    side = ROOT / ".tmp_geo_choice_text.py"
    if side.exists():
        ns: dict = {}
        exec(side.read_text(encoding="utf-8"), ns)
        choice_map = ns.get("CHOICE_TEXT") or {}

    stem_n = 0
    choice_n = 0
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        before = q.get("prompt") or ""
        after = fix_geo_ocr(before)
        expl = q.get("explanation") or ""
        expl2 = fix_geo_ocr(expl)
        if after != before:
            q["prompt"] = after
            stem_n += 1
        if expl2 != expl:
            q["explanation"] = expl2

        # Apply choice text map
        qid = q["id"]
        if qid in choice_map and q.get("type") == "mc":
            texts = choice_map[qid]
            if len(texts) == 4 and all(str(t).strip() for t in texts):
                q["choices"] = [{"text": fix_geo_ocr(str(t).strip())} for t in texts]
                choice_n += 1

    for qid, patch in HAND_FIXES.items():
        if qid not in by:
            print("missing", qid)
            continue
        by[qid].update(patch)
        print("hand-fixed", qid)

    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_skill_counts(qs)

    # Report remaining image-only
    rem = []
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        ch = q.get("choices") or []
        if any(isinstance(c, dict) and c.get("image") and not (c.get("text") or "").strip() for c in ch):
            rem.append(q["id"])
    print(f"stems patched: {stem_n}; choices from map: {choice_n}; remaining image-only: {len(rem)}")
    print("remaining:", rem)


if __name__ == "__main__":
    main()
