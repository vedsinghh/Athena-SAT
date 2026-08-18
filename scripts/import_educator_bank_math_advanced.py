#!/usr/bin/env python3
"""Import Advanced Math questions into E. Bank.

Source: SAT Bank 1/Math/Advanced Math 1.pdf
PDF button: unanswered copy with Correct Answer / Rationale redacted.

Skips any Question ID already present in mathQuestions.json (including all
Summer 2026 Bank items) and any prompt fingerprint match against
Summer Advanced Math stems.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_questions import (  # noqa: E402
    MATH_CHOICE_IMG,
    MATH_FIG,
    MATH_PDF_PREVIEW,
    build_math_prompt,
    clean_text,
    correct_answer,
    crop_math_figure,
    crop_math_pdf_preview,
    drawing_rects,
    extract_choice_objects,
    extract_choices_text,
    extract_explanation,
    find_label_rect,
    group_pages,
    merge_rects,
    ocr_looks_broken,
    ocr_math_stem,
    parse_meta,
    polish_ocr_stem,
    prompt_looks_broken,
    render_clip,
    should_prefer_ocr_stem,
    strip_chart_noise,
)

BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Advanced Math 1.pdf")
PUBLIC_MATH = ROOT / "public" / "qbank" / "math"
UNANSWERED_NAME = "Educator-Bank-1-Advanced-Math-Unanswered.pdf"
UNANSWERED_URL = f"/qbank/math/{UNANSWERED_NAME}"
POOL = "E. Bank"
DOMAIN = "Advanced Math"
DATA = ROOT / "src" / "data"


def fingerprint(prompt: str) -> str:
    blob = re.sub(r"[^a-z0-9]+", " ", (prompt or "").lower())
    return re.sub(r"\s+", " ", blob).strip()[:240]


def make_unanswered_pdf(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(src)
    for page in doc:
        starts = []
        for label in ("Correct Answer", "Rationale"):
            for hit in page.search_for(label):
                if hit.x0 < 120:
                    starts.append(hit.y0)
        if not starts:
            continue
        y0 = min(starts) - 2
        clip = fitz.Rect(0, y0, page.rect.width, page.rect.height)
        page.add_redact_annot(clip, fill=(1, 1, 1))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    doc.save(dest, garbage=4, deflate=True)
    doc.close()


def normalize_inequalities(s: str) -> str:
    """Prefer ≤ / ≥ in stored text (app also maps ASCII forms)."""
    if not s:
        return s
    s = s.replace("<=", "≤").replace(">=", "≥")
    return s


def format_explanation(raw: str) -> str:
    """Correct-answer block, blank line, then each incorrect choice as its own paragraph."""
    text = clean_text(raw or "")
    if not text:
        return ""
    text = normalize_inequalities(text)
    # Split before each "Choice X is incorrect"
    parts = re.split(r"(?=\bChoice\s+[A-D]\s+is incorrect\b)", text, flags=re.I)
    parts = [p.strip() for p in parts if p and p.strip()]
    if len(parts) <= 1:
        return text
    return "\n\n".join(parts)


def strip_equation_slots(prompt: str) -> str:
    prompt = re.sub(r"\{\{eq:\d+\}\}\n?", "", prompt or "").strip()
    prompt = re.sub(r"\n{3,}", "\n\n", prompt)
    return prompt.strip()


def stem_needs_equation_images(prompt: str) -> bool:
    p = prompt or ""
    if "{{eq:" in p:
        return True
    if re.search(r"(?i)\b(given (system|equation)|equations above|equations in the)\b", p):
        if not re.search(r"[=]", p):
            return True
    # Hollow "If for all..." / "defined by the equation ," patterns
    if re.search(r"(?i)\b(equation|,)\s*,\s*(where|what)", p):
        return True
    if re.search(r"(?i)^If\s+for all\b", p):
        return True
    return False


def force_equation_crops(page: fitz.Page, qid: str) -> list[str]:
    """Crop drawing/image equation bands between Question and Answer/Rationale."""
    q = find_label_rect(page, "Question")
    if q is None:
        return []
    end = page.rect.height
    for lab in ("Answer", "Correct Answer", "Rationale"):
        for hit in page.search_for(lab):
            if hit.x0 < 120 and hit.y0 > q.y1:
                end = min(end, hit.y0)
    y0, y1 = q.y1 + 1, end - 2
    if y1 <= y0 + 8:
        return []

    eq_dir = ROOT / "public" / "qbank" / "math" / "equations"
    eq_dir.mkdir(parents=True, exist_ok=True)
    out: list[str] = []

    band = [
        r
        for r in merge_rects(drawing_rects(page, y0, y1), x_gap=28, y_gap=12)
        if 6 <= r.height <= 48 and 18 <= r.width <= 520
    ]
    band = sorted(band, key=lambda r: (r.y0, r.x0))
    for r in band:
        if r.width > 280 and r.height > 40:
            continue
        rel = render_clip(
            page,
            eq_dir / f"{qid}_{len(out)}.jpg",
            fitz.Rect(r.x0 - 3, r.y0 - 3, r.x1 + 6, r.y1 + 3),
            scale=3.6,
        )
        if rel:
            out.append(f"/{rel}")
        if len(out) >= 4:
            return out

    if not out:
        for info in page.get_image_info(xrefs=True):
            r = fitz.Rect(info["bbox"])
            if r.y0 < y0 - 2 or r.y1 > y1 + 2:
                continue
            if r.width < 12 or r.height < 8 or r.width > 420:
                continue
            if r.height > 60:
                continue
            rel = render_clip(
                page,
                eq_dir / f"{qid}_{len(out)}.jpg",
                fitz.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 4, r.y1 + 2),
                scale=3.6,
            )
            if rel:
                out.append(f"/{rel}")
            if len(out) >= 4:
                break
    return out


def light_ocr_fixes(prompt: str) -> str:
    p = prompt or ""
    p = re.sub(r"(?i)\bzy[\s-]*plane\b", "xy-plane", p)
    p = re.sub(r"(?i)\bxyplane\b", "xy-plane", p)
    p = re.sub(r"(?i)\bT otal\b", "Total", p)
    p = re.sub(r"\bpoint t \(x,", "point (x,", p)
    p = re.sub(r"\bi in the\b", "in the", p)
    p = re.sub(r"value of \?", "value of y?", p)
    p = re.sub(r"value of &\?", "value of k?", p)
    p = re.sub(r"value of #\s*\+", "value of x +", p)
    p = re.sub(r"value of 44\?", "value of k?", p)
    p = re.sub(r"\(a,\s*y\)", "(x, y)", p)
    return p


# Hand-fixes for pages where Correct Answer is an embedded glyph (no ASCII).
MANUAL_ITEMS: dict[str, dict] = {
    "40c09d66": {
        "prompt": (
            "If x^(7/3) / x^(1/2) = x^a for all positive values of x, "
            "what is the value of a?"
        ),
        "type": "spr",
        "answer": "7/6",
        "acceptedAnswers": ["7/6", "1.166", "1.167"],
        "skill": "Equivalent expressions",
        "difficulty": "Hard",
        "explanation": (
            "The correct answer is 7/6. The value of a can be found by first rewriting "
            "the left-hand side of the given equation as x^(7/3) / x^(1/2). Using the "
            "properties of exponents, this expression can be rewritten as x^(7/3 - 1/2). "
            "Subtracting the fractions in the exponent yields x^(7/6). Thus, a is 7/6. "
            "Note that 7/6, 1.166, and 1.167 are examples of ways to enter a correct answer."
        ),
    },
    "f2f3fa00": {
        "prompt": (
            "During a 5-second time interval, the average acceleration a, in meters per "
            "second squared, of an object with an initial velocity of 12 meters per second "
            "is defined by the equation a = (v_f - 12)/5, where v_f is the final velocity "
            "of the object in meters per second. If the equation is rewritten in the form "
            "v_f = xa + y, where x and y are constants, what is the value of x?"
        ),
        "type": "spr",
        "answer": "5",
        "acceptedAnswers": ["5"],
        "skill": "Nonlinear equations in one variable and systems of equations in two variables",
        "difficulty": "Hard",
        "explanation": (
            "The correct answer is 5. The given equation can be rewritten in the form "
            "v_f = xa + y. Multiplying both sides of a = (v_f - 12)/5 by 5 yields "
            "5a = v_f - 12. Adding 12 to both sides yields 5a + 12 = v_f, or "
            "v_f = 5a + 12. It follows that the value of x is 5 and the value of y is 12."
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


def build_item(
    g: dict,
    answered: fitz.Document,
    unanswered: fitz.Document,
    unanswered_by_id: dict[str, int],
) -> dict | None:
    qid = g["id"]
    text = g["text"]
    domain, skill, difficulty = parse_meta(text, "Math", [DOMAIN])
    if domain != DOMAIN:
        # parse_meta may still return Advanced Math; reject other domains
        if domain and domain != DOMAIN:
            return None
        # Force domain when meta OCR misses but we're in the Advanced Math bank
        domain = DOMAIN
        if not skill:
            # try a looser skill scrape
            m = re.search(
                r"Skill:\s*([^\n]+)",
                text,
            )
            skill = clean_text(m.group(1)) if m else "Advanced Math"
        if not difficulty:
            dm = re.search(r"Difficulty:\s*(\w+)", text, re.I)
            difficulty = (dm.group(1).capitalize() if dm else "Medium")

    kind, ans = correct_answer(text)
    explanation = format_explanation(extract_explanation(text))
    if kind is None:
        print(f"skip {qid}: no correct answer")
        return None

    src_idx = unanswered_by_id.get(qid, g["pages"][0])
    page = unanswered[src_idx] if qid in unanswered_by_id else answered[g["pages"][0]]

    figure, figure_rect = crop_math_figure(page, MATH_FIG / f"{qid}.jpg", text)
    prompt, equation_images = build_math_prompt(
        page, text, figure_rect=figure_rect, qid=qid
    )
    built_prompt_snapshot = prompt

    ocr_prompt = polish_ocr_stem(ocr_math_stem(page, figure_rect=figure_rect))
    probe = ocr_prompt or strip_equation_slots(prompt)
    if not equation_images and stem_needs_equation_images(probe):
        forced = force_equation_crops(page, qid)
        if forced:
            equation_images = forced
    kept_eqs = list(equation_images)

    # Prefer OCR prose when it fills holes, but restore equation image slots
    # whenever the stem still refers to a missing equation/system.
    prefer_ocr = False
    if should_prefer_ocr_stem(prompt, ocr_prompt, bool(figure)):
        prefer_ocr = True
    elif prompt_looks_broken(prompt) and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        prefer_ocr = True
    elif figure and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        bare = re.sub(r"\{\{eq:\d+\}\}", "", prompt)
        if prompt_looks_broken(prompt) or len(ocr_prompt) > len(bare):
            prefer_ocr = True

    if prefer_ocr:
        prompt = ocr_prompt
        equation_images = []

    # If OCR dropped the math but we still have equation crops, put slots back.
    if kept_eqs and stem_needs_equation_images(prompt) and "{{eq:" not in (prompt or ""):
        # Try text lines from the snapshot first (text-first).
        eq_lines = []
        for ln in built_prompt_snapshot.split("\n"):
            polished = polish_ocr_stem(ln)
            if "{{eq:" in polished:
                continue
            if re.search(r"[=]", polished) and 3 <= len(polished) <= 120:
                eq_lines.append(polished)
        if eq_lines and not stem_needs_equation_images("\n".join(eq_lines + [prompt])):
            prompt = "\n".join(eq_lines + [strip_equation_slots(prompt)])
            equation_images = []
        else:
            prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(kept_eqs)))
            # Prefer OCR prose for the word problem when available
            prose = ocr_prompt if (ocr_prompt and not ocr_looks_broken(ocr_prompt)) else strip_equation_slots(prompt)
            prose = strip_equation_slots(prose)
            prompt = f"{prefix}\n{prose}".strip()
            equation_images = kept_eqs
    elif kept_eqs and "{{eq:" in (built_prompt_snapshot or "") and stem_needs_equation_images(
        strip_equation_slots(prompt)
    ):
        # Snapshot already had slots; keep them with OCR prose if needed
        if "{{eq:" not in (prompt or ""):
            prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(kept_eqs)))
            prose = ocr_prompt if ocr_prompt else strip_equation_slots(prompt)
            prompt = f"{prefix}\n{strip_equation_slots(prose)}".strip()
            equation_images = kept_eqs

    prompt = polish_ocr_stem(prompt)
    if figure or re.search(r"(?i)\b(scatterplot|table|graph|figure)\b", prompt or ""):
        prompt = strip_chart_noise(prompt)
        prompt = polish_ocr_stem(prompt)

    # Text-first when slots are unused; keep slots only when equations are attached.
    if not equation_images:
        prompt = strip_equation_slots(prompt)
    elif "{{eq:" not in (prompt or ""):
        equation_images = []
        prompt = strip_equation_slots(prompt)

    prompt = light_ocr_fixes(normalize_inequalities(prompt))

    if kind == "spr" and not prompt:
        from extract_questions import extract_question_body

        prompt = clean_text(extract_question_body(text)) or "Enter your answer."

    if not prompt or not prompt.strip():
        print(f"skip {qid}: empty prompt")
        return None

    pdf_choices = extract_choices_text(text) if kind == "mc" else None
    choice_objs = extract_choice_objects(page, qid, pdf_choices) if kind == "mc" else []
    # Normalize inequality glyphs in choice text
    if kind == "mc":
        for c in choice_objs:
            if c.get("text"):
                c["text"] = normalize_inequalities(c["text"])

    preview = crop_math_pdf_preview(page, MATH_PDF_PREVIEW / f"{qid}.jpg")

    item = {
        "id": qid,
        "topic": skill or domain,
        "domain": DOMAIN,
        "skill": skill or DOMAIN,
        "difficulty": difficulty or "Medium",
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
        item["choices"] = choice_objs
        item["answer"] = ans
    else:
        item["choices"] = []
        item["acceptedAnswers"] = ans
        item["answer"] = ans[0] if ans else ""

    return item


def build_manual_item(
    qid: str,
    g: dict,
    unanswered: fitz.Document,
    unanswered_by_id: dict[str, int],
) -> dict:
    meta = MANUAL_ITEMS[qid]
    src_idx = unanswered_by_id.get(qid, g["pages"][0])
    page = unanswered[src_idx]
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
        "pdfPage": src_idx + 1,
        "choices": [],
        "acceptedAnswers": meta["acceptedAnswers"],
        "answer": meta["answer"],
    }
    if preview:
        item["pdfPreview"] = f"/{preview}" if not str(preview).startswith("/") else preview
    return item


def main() -> None:
    if not BANK_PDF.exists():
        raise SystemExit(f"Missing bank PDF: {BANK_PDF}")

    for folder in (MATH_FIG, MATH_CHOICE_IMG, MATH_PDF_PREVIEW, PUBLIC_MATH):
        folder.mkdir(parents=True, exist_ok=True)

    unanswered_path = PUBLIC_MATH / UNANSWERED_NAME
    print("Building unanswered Advanced Math PDF...")
    make_unanswered_pdf(BANK_PDF, unanswered_path)
    answered_copy = PUBLIC_MATH / "Educator-Bank-1-Advanced-Math.pdf"
    if not answered_copy.exists():
        shutil.copy2(BANK_PDF, answered_copy)

    answered = fitz.open(BANK_PDF)
    unanswered = fitz.open(unanswered_path)
    groups = group_pages(answered)
    unanswered_by_id = {g["id"]: g["pages"][0] for g in group_pages(unanswered)}
    print(f"Found {len(groups)} question groups in bank PDF")

    existing = json.loads((DATA / "mathQuestions.json").read_text(encoding="utf-8"))
    # Re-import replaces prior Educator Bank Advanced Math rows from this script.
    kept = [
        q
        for q in existing
        if not (
            q.get("pool") == POOL
            and q.get("domain") == DOMAIN
            and str(q.get("pdf") or "").endswith(UNANSWERED_NAME)
        )
    ]
    existing_ids = {str(q.get("id")) for q in kept}
    summer_am = [
        q
        for q in kept
        if q.get("pool") == "Summer 2026 Bank" and q.get("domain") == DOMAIN
    ]
    summer_ids = {str(q.get("id")) for q in summer_am}
    summer_fps = {
        fingerprint(q.get("prompt") or "")
        for q in summer_am
        if fingerprint(q.get("prompt") or "")
    }

    added: list[dict] = []
    skipped_dup = 0
    skipped_other = 0
    seen_ids: set[str] = set()

    for n, g in enumerate(groups, 1):
        qid = g["id"]
        # Soft domain check from page text
        domain, _skill, _diff = parse_meta(g["text"], "Math", [DOMAIN, "Algebra", "Geometry and Trigonometry", "Problem-Solving and Data Analysis"])
        if domain and domain != DOMAIN:
            skipped_other += 1
            continue

        if qid in existing_ids or qid in summer_ids or qid in seen_ids:
            print(f"skip {qid}: already in bank / Summer duplicate")
            skipped_dup += 1
            continue

        if qid in MANUAL_ITEMS:
            item = build_manual_item(qid, g, unanswered, unanswered_by_id)
            print(f"manual {qid}: {MANUAL_ITEMS[qid]['prompt'][:70]}")
        else:
            item = build_item(g, answered, unanswered, unanswered_by_id)
        if not item:
            continue

        fp = fingerprint(item.get("prompt") or "")
        if fp and fp in summer_fps and len(fp) >= 80:
            print(f"skip {qid}: prompt fingerprint matches Summer Advanced Math")
            skipped_dup += 1
            continue

        added.append(item)
        seen_ids.add(qid)
        if n % 10 == 0 or n == 1:
            preview = (item.get("prompt") or "").replace("\n", " | ")[:90]
            print(f"adv {n}/{len(groups)} {qid}: {preview}")

    merged = kept + added
    (DATA / "mathQuestions.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    update_skill_counts(merged)

    by_skill = Counter(q["skill"] for q in added)
    print(f"Added {len(added)} Educator Bank Advanced Math questions "
          f"(skipped {skipped_dup} duplicates, {skipped_other} other-domain)")
    for skill, n in by_skill.most_common():
        print(f"  {n:3d}  {skill}")
    print(f"Unanswered PDF: {unanswered_path}")
    print(f"Total math questions now: {len(merged)}")

    # Sanity: no Summer AM id in educator AM
    edu_ids = {q["id"] for q in added}
    overlap = edu_ids & summer_ids
    if overlap:
        print(f"ERROR: still overlapping Summer IDs: {sorted(overlap)}")
        raise SystemExit(1)
    print(f"Summer Advanced Math overlap check: OK (0 / {len(summer_ids)})")


if __name__ == "__main__":
    main()
