#!/usr/bin/env python3
"""Second-pass cleanup for Geometry explanations after OCR rebuild."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data" / "mathQuestions.json"
POOL = "E. Bank"
DOMAIN = "Geometry and Trigonometry"

HAND_EXPLANATIONS: dict[str, str] = {
    "2b41a4c4": (
        "The correct answer is 880. The volume, V, of a right rectangular prism is given by the formula "
        "V = lwh, where l is the length, w is the width, and h is the height of the prism. "
        "It’s given that a right rectangular prism has a length of 11 meters, a width of 8 meters, "
        "and a height of 10 meters. Substituting 11 for l, 8 for w, and 10 for h in the formula "
        "V = lwh yields V = (11)(8)(10), or V = 880. Therefore, the volume, in cubic meters, of the prism is 880."
    ),
    "deff8a2f": (
        "Choice C is correct. The volume, V, of a right circular cylinder is given by the formula "
        "V = πr²h, where r is the radius of the base of the cylinder and h is the height of the cylinder. "
        "It’s given that a right circular cylinder has a height of 6 meters. Therefore, h = 6. "
        "It's also given that the right circular cylinder has a base with a circumference of 20π meters. "
        "The circumference, C, of a circle is given by C = 2πr, where r is the radius of the circle. "
        "Substituting 20π for C in the formula C = 2πr yields 20π = 2πr. Dividing each side of this equation "
        "by 2π yields 10 = r. Substituting 10 for r and 6 for h in the formula V = πr²h yields "
        "V = π(10)²(6), or V = 600π. Therefore, the volume, in cubic meters, of the cylinder is 600π.\n\n"
        "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice B is incorrect. This is the lateral surface area, not the volume, of the cylinder.\n\n"
        "Choice D is incorrect. This is the result of using the diameter, not the radius, for the value of r "
        "in the formula V = πr²h."
    ),
    "c0586eb5": (
        "Choice C is correct. The base of a cylinder is a circle with a diameter equal to the diameter of the cylinder. "
        "The volume, V, of a cylinder can be found by multiplying the area of the circular base, A, by the height of "
        "the cylinder, h, or V = Ah. The area of a circle can be found using the formula A = πr², where r is the "
        "radius of the circle. It’s given that the diameter of the cylinder is 8 inches. Thus, the radius of this "
        "circle is 4 inches. Therefore, the area of the circular base of the cylinder is A = π(4)², or 16π square "
        "inches. It’s given that the height h of the cylinder is 12 inches. Substituting 16π for A and 12 for h in "
        "the formula V = Ah gives V = 16π(12), or 192π cubic inches.\n\n"
        "Choice A is incorrect. This is the area of the circular base of the cylinder.\n\n"
        "Choice B is incorrect and may result from using 8, instead of 16, as the value of r² in the formula for "
        "the area of a circle.\n\n"
        "Choice D is incorrect and may result from using 8, instead of 4, for the radius of the circular base."
    ),
    "a2659088": (
        "Choice D is correct. The volume, V, of a right circular cylinder is given by V = πr²h, where r is the "
        "radius of the circular base and h is the height of the cylinder. It’s given that the cylinder has a height "
        "of 8 meters and a base with a radius of 12 meters. Substituting 12 for r and 8 for h in V = πr²h yields "
        "V = π(12)²(8), or V = 1,152π. Therefore, the volume, in m³, of the cylinder is 1,152π.\n\n"
        "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice C is incorrect. This is the volume, in m³, of a cylinder with a radius of 8 meters and a height of "
        "12 meters."
    ),
    "96467fea": (
        "Choice A is correct. It’s given that circle N has a radius of 7 mm. The area of a circle is given by the "
        "expression πr², where r is the radius of the circle. Substituting 7 for r in the expression yields π(7)², "
        "or 49π, for the area, in mm², of circle N. It’s also given that the area of circle M is 64π mm². Adding "
        "the two areas yields 49π + 64π, or 113π, mm². Therefore, the total area, in mm², of circles N and M is 113π.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "e86f0651": (
        "Choice D is correct. The area, A, of a circle is given by the formula A = πr², where r is the radius of "
        "the circle. It’s given that the circle has a radius of 43 meters. Substituting 43 for r in the formula "
        "A = πr² yields A = π(43)², or A = 1,849π. Therefore, the area, in square meters, of the circle is 1,849π.\n\n"
        "Choice A is incorrect. This is the area, in square meters, of a circle with a radius of √(43/2) meters.\n\n"
        "Choice B is incorrect. This is the area, in square meters, of a circle with a radius of √43 meters.\n\n"
        "Choice C is incorrect. This is the circumference, in meters, of the circle."
    ),
    "151eda3c": (
        "Choice B is correct. If the radius of container A is 16 centimeters and the radius of container B is 25% "
        "longer than the radius of container A, then the radius of container B is 16 + (0.25)(16) = 20 centimeters. "
        "The volume of a cylinder is πr²h, where r is the radius of the cylinder and h is its height. Substituting "
        "r = 20 and h = 50 into πr²h yields that the volume of cylinder B is π(20)²(50) = 20,000π cubic centimeters.\n\n"
        "Choice A is incorrect and may result from multiplying the radius of cylinder B by the radius of cylinder A "
        "rather than squaring the radius of cylinder B.\n\n"
        "Choice C is incorrect and may result from multiplying the radius of cylinder B by 25 rather than squaring it.\n\n"
        "Choice D is incorrect and may result from taking the radius of cylinder B to be 25 centimeters rather than "
        "20 centimeters."
    ),
    "5afbdc8e": (
        "Choice C is correct. The area A of a circle with radius r is given by the formula A = πr². Thus, a circle "
        "with radius 2 has area π(2)², which can be rewritten as 4π. The area of a square with side length s is "
        "given by the formula A = s². Thus, if a square has the same area as a circle with radius 2, then s² = 4π. "
        "Since the side length of a square must be a positive number, taking the square root of both sides of "
        "s² = 4π gives s = √(4π). Using the properties of square roots, √(4π) can be rewritten as √4 · √π, which "
        "is equivalent to 2√π. Therefore, s = 2√π.\n\n"
        "Choice A is incorrect. The side length of the square isn't equal to the radius of the circle.\n\n"
        "Choice B is incorrect and may result from incorrectly simplifying the expression √(4π).\n\n"
        "Choice D is incorrect and may result from incorrectly simplifying the expression √(4π)."
    ),
    "c8345903": (
        "Choice B is correct. The ratio of the lengths of two arcs of a circle is equal to the ratio of the measures "
        "of the central angles that subtend the arcs. It’s given that a minor arc is subtended by a central angle "
        "with measure 100° and has length 5π. Since the sum of the measures of the angles about a point is 360°, "
        "it follows that arc ABC is subtended by a central angle with measure 360° − 100° = 260°. If s is the "
        "length of arc ABC, then s must satisfy the ratio s/(5π) = 260/100. Reducing the fraction 260/100 to its "
        "simplest form gives 13/5. Therefore, s/(5π) = 13/5. Multiplying both sides of s/(5π) = 13/5 by 5π yields "
        "s = 13π.\n\n"
        "Choice A is incorrect. This is the length of an arc consisting of exactly half of the circle, but arc ABC "
        "is greater than half of the circle.\n\n"
        "Choice C is incorrect. This is the total circumference of the circle.\n\n"
        "Choice D is incorrect. This is half the length of arc ABC, not its full length."
    ),
    "35d37640": (
        "Choice D is correct. It's given that the circle is a unit circle, which means the circle has a radius of 1. "
        "It's also given that point G is the center of the circle and has coordinates (0, 0) and that point H lies on "
        "the circle and has coordinates (−1, y). Since the radius of the circle is 1, the value of y must be 0, as all "
        "other points with an x-coordinate of −1 are a distance greater than 1 away from point G. Since F and H are "
        "points on the unit circle centered at G, let side FG be the starting side of the angle and side GH be the "
        "terminal side of the angle. Since side FG is on the positive x-axis and side GH is on the negative x-axis, "
        "side FG is half of a rotation around the unit circle, or π radians, away from side GH. Therefore, the "
        "positive measure of angle FGH, in radians, is equal to π plus an integer multiple of 2π. In other words, "
        "the positive measure of angle FGH, in radians, is an odd integer multiple of π. Of the given choices, only "
        "25π is an odd integer multiple of π.\n\n"
        "Choice A is incorrect. This could be the positive measure of an angle where the starting side is FG and the "
        "terminal side contains the point (0, −1), not (−1, 0).\n\n"
        "Choice B is incorrect. This could be the positive measure of an angle where the starting side is FG and the "
        "terminal side contains the point (0, 1), not (−1, 0).\n\n"
        "Choice C is incorrect. This could be the positive measure of an angle where the starting side is FG and the "
        "terminal side contains the point (1, 0), not (−1, 0)."
    ),
    "69b0d79d": (
        "Choice B is correct. Because segments OA and OB are radii of the circle centered at point O, these segments "
        "have equal lengths. Therefore, triangle AOB is an isosceles triangle, where angles OAB and OBA are congruent "
        "base angles of the triangle. It's given that angle OAB measures 30°. Therefore, angle OBA also measures 30°. "
        "Let x° represent the measure of angle AOB. Since the sum of the measures of the three angles of any triangle "
        "is 180°, it follows that 30° + 30° + x° = 180°, or 60° + x° = 180°. Subtracting 60° from both sides of this "
        "equation yields x° = 120°, or (2π/3) radians. Therefore, the measure of angle AOB, and thus the measure of "
        "arc AB, is (2π/3) radians. Since OC is a radius of the given circle and its length is 18, the length of the "
        "radius of the circle is 18. Therefore, the length of arc AB can be calculated as (2π/3)(18), or 12π.\n\n"
        "Choice A is incorrect and may result from conceptual or computational errors.\n\n"
        "Choice C is incorrect and may result from conceptual or computational errors.\n\n"
        "Choice D is incorrect and may result from conceptual or computational errors."
    ),
    "d621cffb": (
        "Choice D is correct. The volume, V, of a sphere can be found using the formula V = (4/3)πr³, where r is the "
        "radius of the sphere. It’s given that the sphere has a radius of 17/5 feet. Substituting 17/5 for r in the "
        "formula V = (4/3)πr³ yields V = (4/3)π(17/5)³, which is equivalent to V = (4/3)π(4,913/125), or "
        "V = 19,652π/375. Therefore, the volume, in cubic feet, of the sphere is 19,652π/375.\n\n"
        "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice B is incorrect. This is the volume, in cubic feet, of a sphere with a different radius.\n\n"
        "Choice C is incorrect and may result from conceptual or calculation errors."
    ),
    "3b225698": (
        "Choice C is correct. It’s given that triangle XYZ is similar to triangle RST, such that X, Y, and Z "
        "correspond to R, S, and T, respectively. Since corresponding angles of similar triangles are congruent, "
        "it follows that the measure of ∠Z is congruent to the measure of ∠T. It’s given that the measure of ∠Z "
        "is 20°. Therefore, the measure of ∠T is 20°.\n\n"
        "Choice A is incorrect and may result from a conceptual error.\n\n"
        "Choice B is incorrect. This is half the measure of ∠Z.\n\n"
        "Choice D is incorrect. This is twice the measure of ∠Z."
    ),
    "9fec9d49": (
        "Choice A is correct. It's given that the length of each side of a scale model is 1/10 times the length of "
        "the corresponding side of the actual floor of a ballroom. Therefore, the area of the scale model is "
        "(1/10)², or 1/100, times the area of the actual floor of the ballroom. It’s given that the area of the "
        "floor of the ballroom is 600 square meters. Therefore, the area, in square meters, of the scale model is "
        "(1/100)(600), or 6.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "a07ed090": (
        "Choice C is correct. The volume of a right circular cylinder is equal to πa²b, where a is the radius of a "
        "base of the cylinder and b is the height of the cylinder. It’s given that the cylinder shown has a radius "
        "of r and a height of h. It follows that the volume of the cylinder shown is equal to πr²h. It’s given that "
        "the second right circular cylinder has a radius of R and a height of H. It follows that the volume of the "
        "second cylinder is equal to πR²H. Choice C gives R = 7r and H = 8h. Substituting 7r for R and 8h for H in "
        "the expression that represents the volume of the second cylinder yields π(7r)²(8h), or π(49r²)(8h), which "
        "is equivalent to π(392r²h), or 392(πr²h). This expression is equal to 392 times the volume of the cylinder "
        "shown, πr²h. Therefore, R = 7r and H = 8h could represent the radius R, in terms of r, and the height H, "
        "in terms of h, of the second cylinder.\n\n"
        "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "3b931fb0": (
        "The correct answer is 29. The volume, V, of a right circular cylinder is given by the formula V = πr²h, "
        "where r is the radius of the base of the cylinder and h is the height of the cylinder. Since the base of "
        "the cylinder is a circle with radius r, the area of the base of the cylinder is πr². It's given that a "
        "right circular cylinder has a volume of 37π cubic centimeters; therefore, V = 37π. It's also given that "
        "the area of the base of the cylinder is 13 square centimeters; therefore, πr² = 13. Substituting 37π for "
        "V and 13 for πr² in the formula V = πr²h yields 37π = 13h. Dividing both sides of this equation by 13 "
        "yields 29 = h. Therefore, the height of the cylinder, in centimeters, is 29."
    ),
    "e5c57163": (
        "The correct answer is 27,556. The area of a square is s², where s is the side length of the square. Let x "
        "represent the length of each side of square B. Substituting x for s in s² yields x². It follows that the "
        "area of square B is x². It’s given that square A has side lengths that are 166 times the side lengths of "
        "square B. Since x represents the length of each side of square B, the length of each side of square A can "
        "be represented by the expression 166x. It follows that the area of square A is (166x)², or 27,556x². "
        "It’s given that the area of square A is k times the area of square B. Since the area of square A is equal "
        "to 27,556x², and the area of square B is equal to x², an equation representing the given statement is "
        "27,556x² = kx². Since x represents the length of each side of square B, the value of x must be positive. "
        "Therefore, the value of x² is also positive, so it does not equal 0. Dividing both sides of the equation "
        "27,556x² = kx² by x² yields 27,556 = k. Therefore, the value of k is 27,556."
    ),
    "167aff9e": (
        "The correct answer is 1,260. Since it's given that prisms X and Y are similar, all the linear measurements "
        "of prism Y are k times the respective linear measurements of prism X, where k is a positive constant. "
        "Therefore, the surface area of prism Y is k² times the surface area of prism X and the volume of prism Y "
        "is k³ times the volume of prism X. It's given that the surface area of prism Y is 1,450 cm², and the "
        "surface area of prism X is 58 cm², which implies that 1,450 = 58k². Dividing both sides of this equation "
        "by 58 yields 25 = k², or k² = 25. Since k is a positive constant, k = 5. It's given that the volume of "
        "prism Y is 1,250 cm³. Therefore, the volume of prism X is equal to 1,250/k³ cm³, which is equivalent to "
        "1,250/125 cm³, or 10 cm³. Thus, the sum of the volumes, in cm³, of the two prisms is 1,250 + 10, or 1,260."
    ),
    "9966235e": (
        "Choice A is correct. The volume of a cube can be found by using the formula V = s³, where V is the volume "
        "and s is the edge length of the cube. Therefore, the volume of the given cube is V = 68³, or 314,432 cubic "
        "inches. The volume of a sphere can be found by using the formula V = (4/3)πr³, where V is the volume and r "
        "is the radius of the sphere. Therefore, the volume of the given sphere is V = (4/3)π(34)³, or approximately "
        "164,636 cubic inches. The volume of the space in the cube not taken up by the sphere is the difference of "
        "these two volumes, 314,432 − 164,636 = 149,796 cubic inches.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice C is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "2266984b": (
        "Choice B is correct. The standard equation of a circle in the xy-plane is of the form (x − h)² + (y − k)² = r², "
        "where (h, k) are the coordinates of the center of the circle and r is the radius. The given equation can be "
        "rewritten in standard form by completing the squares. The sum of the first two terms, x² + 20x, needs a 100 "
        "to complete the square, and the sum of the next two terms, y² + 16y, needs a 64 to complete the square. Adding "
        "100 and 64 to both sides of x² + 20x + y² + 16y = −20 yields (x + 10)² + (y + 8)² = 144. Therefore, the center "
        "of the circle is (−10, −8).\n\n"
        "Choice A is incorrect and may result from not dividing the coefficients of x and y by 2 when completing the square.\n\n"
        "Choice C is incorrect and may result from using the opposite of the correct center coordinates.\n\n"
        "Choice D is incorrect and may result from using the coefficients of x and y without completing the square."
    ),
    "5011b039": (
        "The correct answer is 13. The equation of a circle in the xy-plane can be written in the form "
        "(x − h)² + (y − k)² = r², where (h, k) is the center of the circle and r is the radius of the circle. "
        "It's given that the circle in the xy-plane is defined by (x + 2)² + (y + 5)² = 169. Therefore, r² = 169. "
        "Taking the positive square root of both sides of this equation yields r = 13. Therefore, the radius of the "
        "circle is 13."
    ),
    "b8a225ff": (
        "The correct answer is 16. An equation of a circle in the xy-plane can be written as (x − h)² + (y − k)² = r², "
        "where the center of the circle is (h, k) and the radius of the circle is r. It's given that the equation of "
        "circle A is (x + 5)² + (y − 5)² = 4, which is equivalent to (x + 5)² + (y − 5)² = 2². Therefore, the radius "
        "of circle A is 2. The radius of circle B is twice the radius of circle A, so the radius of circle B is 4. "
        "Since circle B has the same center as circle A, an equation for circle B is (x + 5)² + (y − 5)² = 16. The "
        "constant on the right side of this equation is 16."
    ),
    "b0a72bdc": (
        "Choice B is correct. The standard form of an equation of a circle in the xy-plane is (x − h)² + (y − k)² = r², "
        "where the coordinates of the center of the circle are (h, k) and the length of the radius of the circle is r. "
        "For the circle in the xy-plane with equation (x − 5)² + (y − 3)² = 16, it follows that r² = 16. Taking the "
        "square root of both sides of this equation yields r = 4. The diameter of a circle is twice the radius, so "
        "the diameter is 2 · 4 = 8.\n\n"
        "Choice A is incorrect. This is the radius, not the diameter, of the circle.\n\n"
        "Choice C is incorrect. This is the square of the radius, not the diameter.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "76c73dbf": (
        "The correct answer is 10. It's given that the graph of x² + x + y² + y = 199/2 in the xy-plane is a circle. "
        "Completing the square for x and for y: x² + x needs (1/2)² = 1/4, and y² + y needs 1/4. Adding 1/4 + 1/4 to "
        "both sides yields (x + 1/2)² + (y + 1/2)² = 199/2 + 1/2 = 100. Therefore, r² = 100, so r = 10. The length of "
        "the circle’s radius is 10."
    ),
    "f67e4efc": (
        "Choice A is correct. The volume of a right circular cylinder with a radius of r is the product of the area of "
        "the base, πr², and the height, h. The volume of the right circular cylinder described is 45π and its height "
        "is 5. If the radius is r, it follows that 45π = πr²(5). Dividing both sides of this equation by 5π yields "
        "9 = r². Taking the positive square root of both sides of this equation yields r = 3. Therefore, the radius "
        "of the cylinder is 3.\n\n"
        "Choice B is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice C is incorrect. This is the square of the radius, not the radius.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "52f7b898": (
        "Choice C is correct. In the triangle shown, the measure of angle B is 30° and angle C is a right angle "
        "(90°). Since the sum of the angles in a triangle is 180°, the measure of angle A is 60°. In a 30°-60°-90° "
        "triangle, side lengths are in the ratio 1 : √3 : 2. The value of tan A is opposite over adjacent; since "
        "angle A measures 60°, tan A = √3.\n\n"
        "Choice A is incorrect and may result from conceptual or calculation errors.\n\n"
        "Choice B is incorrect. This is the value of tan B, not tan A.\n\n"
        "Choice D is incorrect and may result from conceptual or calculation errors."
    ),
    "0d43db90": (
        "Choice B is correct. The perimeter of a triangle is the sum of the lengths of all three sides. It’s given "
        "that AB = 4 inches and AC = 7 inches. Let x represent the length of BC. Then 4 + 7 + x = 17, so x = 6. "
        "Therefore, the length of side BC is 6 inches.\n\n"
        "Choice A is incorrect. This is the length of side AB, not side BC.\n\n"
        "Choice C is incorrect. This is the length of side AC, not side BC.\n\n"
        "Choice D is incorrect. This is the sum of the lengths of sides AB and AC, not the length of side BC."
    ),
}


def choice_texts(q: dict) -> list[str]:
    out = []
    for c in q.get("choices") or []:
        if isinstance(c, dict):
            out.append(str(c.get("text") or "").strip())
        else:
            out.append(str(c).strip())
    return out


def restore_pi_from_choices(text: str, choices: list[str]) -> str:
    t = text
    pi_nums: list[str] = []
    for c in choices:
        c2 = c.replace(" ", "")
        m = re.fullmatch(r"([\d,]+)π", c2)
        if m:
            pi_nums.append(m.group(1))
    pi_nums = sorted(set(pi_nums), key=lambda s: len(s.replace(",", "")), reverse=True)
    for num in pi_nums:
        compact = num.replace(",", "")
        forms = {num, compact}
        if compact.isdigit():
            forms.add(f"{int(compact):,}")
        for form in forms:
            t = re.sub(rf"\b{re.escape(form)}7\b", f"{num}π", t)
            t = re.sub(rf"\b{re.escape(form)}n\b", f"{num}π", t, flags=re.I)
            t = re.sub(rf"\b{re.escape(form)}\s*sr\b", f"{num}π", t, flags=re.I)
    return t


def global_ocr_cleanup(text: str) -> str:
    if not text:
        return text
    t = text
    # a? + b? = c? style superscripts
    t = re.sub(r"([a-zA-Z0-9)])\?(?!\?)", r"\1²", t)
    t = re.sub(r"([a-zA-Z0-9)])”", r"\1²", t)
    t = re.sub(r"\bs\*\b", "s²", t)
    t = re.sub(r"\bV\s*=\s*mrh\b", "V = πr²h", t)
    t = re.sub(r"\bV\s*=\s*nrh\b", "V = πr²h", t)
    t = re.sub(r"\bV\s*=\s*arh\b", "V = πr²h", t)
    t = re.sub(r"\bV\s*=\s*ar2h\b", "V = πr²h", t)
    t = re.sub(r"\bA\s*=\s*nm\b", "A = πr²", t)
    t = re.sub(r"\bC\s*=\s*27\b", "C = 2πr", t)
    t = re.sub(r"\band his the\b", "and h is the", t)
    t = re.sub(r"\bfor A in the formula\b", "for h in the formula", t)
    t = re.sub(r"C,,", "C,", t)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main() -> None:
    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = 0
    hand_n = 0
    for q in qs:
        if q.get("pool") != POOL or q.get("domain") != DOMAIN:
            continue
        qid = q["id"]
        before = q.get("explanation") or ""
        if qid in HAND_EXPLANATIONS:
            after = HAND_EXPLANATIONS[qid]
            hand_n += 1
        else:
            after = global_ocr_cleanup(before)
            after = restore_pi_from_choices(after, choice_texts(q))
            after = global_ocr_cleanup(after)
        if after != before:
            q["explanation"] = after
            touched += 1
    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {touched} explanations ({hand_n} hand-written)")


if __name__ == "__main__":
    main()
