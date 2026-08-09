#!/usr/bin/env python3
"""Import Algebra questions into SAT Educator Bank 1.

Content source: Algebra_1_Program_Readable_FIXED_v3_SPACING PDF
PDF button source: SAT Bank 1/Math/Algebra 1.pdf with Correct Answer / Rationale removed
Skips any question IDs already present (e.g. Collegeboard Summer 2026).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pdf_tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import fitz  # noqa: E402

from extract_questions import (  # noqa: E402
    MATH_CHOICE_IMG,
    MATH_DOMAINS,
    MATH_FIG,
    MATH_PDF_PREVIEW,
    build_math_prompt,
    clean_text,
    crop_math_figure,
    crop_math_pdf_preview,
    extract_choice_objects,
    extract_choices_text,
    ocr_looks_broken,
    ocr_math_stem,
    parse_meta,
    polish_ocr_stem,
    prompt_looks_broken as bank_prompt_broken,
    should_prefer_ocr_stem,
    strip_chart_noise,
)

READABLE_PDF = Path(
    "/Users/vedsingh/Downloads/Algebra_1_Program_Readable_FIXED_v3_SPACING.pdf"
)
BANK_PDF = Path("/Users/vedsingh/Downloads/SAT Bank 1/Math/Algebra 1.pdf")
PUBLIC_MATH = ROOT / "public" / "qbank" / "math"
UNANSWERED_NAME = "Educator-Bank-1-Algebra-Unanswered.pdf"
UNANSWERED_URL = f"/qbank/math/{UNANSWERED_NAME}"
POOL = "SAT Educator Bank 1"
DATA = ROOT / "src" / "data"

CHOICE_RE = re.compile(
    r"ANSWER_CHOICES:\s*\n(.*?)(?:\nCORRECT_ANSWER:|\nRATIONALE:|\Z)",
    re.S,
)


def fingerprint(prompt: str) -> str:
    blob = re.sub(r"[^a-z0-9]+", " ", (prompt or "").lower())
    return re.sub(r"\s+", " ", blob).strip()[:240]


STEM_START = re.compile(
    r"(?="
    r"(?:A |An |The |In |For |If |On |During |John |Ellen |Line |What |Which |How |"
    r"One of |Two |Three |Given |Using |Find |Solve |Let )"
    r")",
    re.I,
)


def scrub_leading_ocr_junk(prompt: str, *, keep_leading_equations: bool = True) -> str:
    """Remove chart-axis / table OCR prefixes without deleting the word problem."""
    p = (prompt or "").strip()
    if not p:
        return p
    # Explicit garbage prefixes from the readable dump
    p = re.sub(
        r"^(?:y\s+10 of.*?(?=\n)|TABLE:.*?(?=\n)|[\d\s.|XxOoIi]+\n)+",
        "",
        p,
        flags=re.I | re.S,
    ).strip()
    # If the stem starts with noisy OCR then a clear English sentence, drop the noise.
    # Keep a short leading equation line when it looks algebraic (e.g. "y = 2x + 1\n...").
    lines = p.split("\n")
    first = lines[0].strip() if lines else ""
    looks_like_eq = bool(re.search(r"[=+\-*/]", first)) and len(first) <= 80
    if keep_leading_equations and looks_like_eq and len(lines) > 1:
        return p
    m = STEM_START.search(p)
    if m and m.start() > 0:
        head = p[: m.start()]
        rest = p[m.start() :]
        # Keep a mangled OCR equation if the stem refers to "the given equation"
        # and otherwise wouldn't include any formula.
        if re.search(r"(?i)\bgiven equation\b", rest) and re.search(r"[=+\-]", head):
            return p
        # Only strip when the head is mostly non-words / axis crumbs
        letters = sum(ch.isalpha() for ch in head)
        if letters <= 8 or re.fullmatch(r"[\d\s.|XxOoIi_\-]+", head):
            p = rest.strip()
    return p or prompt.strip()


def readable_prompt_broken(text: str) -> bool:
    p = text or ""
    if bank_prompt_broken(p):
        return True
    if re.search(r"(?i)\b(can veil|jewee|totes|ews _|pccp|velen)\b", p):
        return True
    if re.search(r"(?i)\bof CA\b", p):
        return True
    if re.search(r"\b[fgh]\d[a-z]\b", p):
        return True
    if len(re.findall(r"[|]|ttt|TTT|PTT", p)) >= 3:
        return True
    # Missing variables / hollow stems
    if re.search(r"(?i)value of\s*\(\s*\d+\s*\)", p):
        return True
    if re.search(r"(?i)values of and their", p):
        return True
    if re.search(r"(?i)system of equations above", p) and "{{eq:" not in p and not re.search(r"[=]", p):
        return True
    if re.search(r"(?i)given system of equations", p) and "{{eq:" not in p and not re.search(r"[=]", p.split("\n")[0] if p else ""):
        # allow if later lines have equations
        if not re.search(r"[=]", p):
            return True
    return False


def choices_are_weak(choices: list) -> bool:
    if not choices or len(choices) < 4:
        return True
    texts = []
    for c in choices:
        if isinstance(c, dict):
            if c.get("image"):
                return False
            texts.append((c.get("text") or "").strip())
        else:
            texts.append(str(c).strip())
    if any(not t for t in texts):
        return True
    # Duplicate numeric OCR (e.g. 3,3,3,9 for fraction choices)
    if len(set(texts)) <= 2 and sum(t.replace(".", "").isdigit() for t in texts) >= 3:
        return True
    return choices_need_images(texts)


def clean_math_prose(text: str) -> str:
    t = clean_text((text or "").replace("\r", ""))
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # Common OCR confusions in the readable algebra dump
    t = t.replace("ChoiceC", "Choice C").replace("ChoiceA", "Choice A")
    t = t.replace("ChoiceB", "Choice B").replace("ChoiceD", "Choice D")
    t = re.sub(r"\bChoice([A-D])\b", r"Choice \1", t)
    t = re.sub(r"f\(a\)", "f(x)", t)
    t = re.sub(r"g\(a\)", "g(x)", t)
    t = re.sub(r"h\(a\)", "h(x)", t)
    # Variable x often OCR'd as a in short equations
    t = re.sub(r"\b(\d)a\b", r"\1x", t)
    t = re.sub(r"\ba\s*-\s*(\d)", r"x - \1", t)
    t = re.sub(r"\ba\s*\+\s*(\d)", r"x + \1", t)
    t = re.sub(r"\bvalue of a\b", "value of x", t, flags=re.I)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def parse_readable(doc: fitz.Document) -> list[dict]:
    blocks = []
    for i, page in enumerate(doc):
        text = page.get_text() or ""
        m = re.search(
            r"QUESTION_ID:\s*([0-9a-fA-F]+)\s*\n(.*?)(?=\nEND_QUESTION\b|\Z)",
            text,
            re.S,
        )
        if not m:
            continue
        qid = m.group(1)
        body = m.group(2)
        source_page = int((re.search(r"^SOURCE_PAGE:\s*(\d+)", body, re.M) or [None, "0"])[1])
        qm = re.search(
            r"QUESTION:\s*\n(.*?)(?:\nANSWER_CHOICES:|\nCORRECT_ANSWER:)",
            body,
            re.S,
        )
        prompt = clean_math_prose(qm.group(1) if qm else "")
        prompt = scrub_leading_ocr_junk(prompt)

        cm = CHOICE_RE.search(body)
        choices_raw = (cm.group(1) if cm else "").strip()
        is_spr = bool(re.search(r"\[FREE_RESPONSE\]", choices_raw))
        choices: list[str] = []
        if not is_spr and choices_raw:
            # Normalize glued labels like "B. $13,000 Cc. $15,400"
            normalized = re.sub(r"(?<![A-Za-z])([A-D])\s*\.\s*", r"\n\1. ", choices_raw)
            normalized = re.sub(r"(?<![A-Za-z])([A-D])(?=[A-Za-z])", r"\n\1. ", normalized)
            found: dict[str, str] = {}
            for line in normalized.splitlines():
                lm = re.match(r"^([A-D])\.\s*(.*)$", line.strip(), re.I)
                if not lm:
                    continue
                letter = lm.group(1).upper()
                found[letter] = clean_math_prose(lm.group(2))
            choices = [found.get(L, "") for L in "ABCD"]
            if sum(1 for c in choices if c) < 2:
                choices = []

        ca = re.search(r"^CORRECT_ANSWER:\s*(.+)$", body, re.M)
        answer_raw = (ca.group(1).strip() if ca else "")
        if re.match(r"(?i)^RATIONALE", answer_raw or ""):
            answer_raw = ""
        rm = re.search(r"RATIONALE:\s*\n(.*)$", body, re.S)
        rationale = clean_math_prose((rm.group(1) if rm else "").strip())

        kind = "spr"
        answer: int | list[str] | str | None = None
        if re.fullmatch(r"[A-D]", answer_raw, re.I):
            kind = "mc"
            answer = ord(answer_raw.upper()) - ord("A")
        else:
            parts: list[str] = []
            if answer_raw:
                parts = [a.strip() for a in re.split(r"\s+or\s+|,\s*", answer_raw) if a.strip()]
            if not parts:
                # Fallback: "Note that 3/2 and 1.5 are examples of ways to enter"
                note = re.search(
                    r"Note that\s+(.+?)\s+are examples of ways to enter",
                    rationale,
                    re.I,
                )
                if note:
                    parts = [
                        a.strip()
                        for a in re.split(r"\s+and\s+|,\s*|\s+or\s+", note.group(1))
                        if a.strip() and not re.fullmatch(r"(?i)and|or", a.strip())
                    ]
            if not parts:
                m = re.search(r"(?i)correct answer is\s*([0-9./\-]+)", rationale)
                if m:
                    parts = [m.group(1)]
            if parts:
                kind = "spr"
                answer = parts
            elif is_spr:
                kind = "spr"
                answer = None
            elif not is_spr and len(choices) == 4:
                # MC with missing letter — try rationale "Choice C is correct"
                cm_ans = re.search(r"(?i)Choice\s*([A-D])\s+is correct", rationale)
                if cm_ans:
                    kind = "mc"
                    answer = ord(cm_ans.group(1).upper()) - ord("A")

        blocks.append(
            {
                "id": qid,
                "source_page": source_page or (i + 1),
                "readable_page": i + 1,
                "prompt": prompt,
                "choices": choices,
                "kind": kind,
                "answer": answer,
                "rationale": rationale,
                "needs_figure": bool(
                    re.search(r"\b(graph|table|figure|chart|scatterplot|lines shown)\b", prompt + "\n" + body, re.I)
                ),
            }
        )
    return blocks


def index_bank_pages(doc: fitz.Document) -> dict[str, int]:
    out: dict[str, int] = {}
    for i, page in enumerate(doc):
        m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", page.get_text() or "", re.I)
        if m:
            out[m.group(1)] = i
    return out


def make_unanswered_pdf(src: Path, dest: Path) -> None:
    """Copy Algebra PDF and white out Correct Answer + Rationale on every page."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(src)
    for page in doc:
        starts = []
        for label in ("Correct Answer", "Rationale"):
            for hit in page.search_for(label):
                # Prefer left-column section labels
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


def choices_need_images(choices: list[str]) -> bool:
    if not choices:
        return False
    joined = " ".join(choices)
    if re.search(r"[|]{2,}|[□■]|TABLE", joined):
        return True
    # Very short / empty / heavily symbolic OCR
    bad = 0
    for c in choices:
        if len(c) <= 1:
            bad += 1
        elif re.search(r"[^\x00-\x7F]", c) and len(c) < 24:
            bad += 1
        elif re.fullmatch(r"[\d\s+\-*/=().xXyYa-z]+", c) and ("=" in c or "/" in c):
            # Keep plain text for simple numeric / algebraic choices
            continue
    return bad >= 2


def force_equation_crops(page: fitz.Page, qid: str) -> list[str]:
    """Crop drawing/image equation bands between Question and Answer/Rationale."""
    from extract_questions import find_label_rect, drawing_rects, merge_rects, render_clip

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

    # Prefer vector equation strokes
    band = [
        r for r in merge_rects(drawing_rects(page, y0, y1), x_gap=28, y_gap=12)
        if 6 <= r.height <= 48 and 18 <= r.width <= 520
    ]
    # Keep top-most compact equation rows (skip huge graph frames)
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

    # Fallback: embedded images in the stem band (common for function notation).
    # Always page-render (white bg) — raw xrefs are often black/fringed embeds.
    if not out:
        for info in page.get_image_info(xrefs=True):
            r = fitz.Rect(info["bbox"])
            if r.y0 < y0 - 2 or r.y1 > y1 + 2:
                continue
            if r.width < 12 or r.height < 8 or r.width > 420:
                continue
            rel = render_clip(
                page,
                eq_dir / f"{qid}_{len(out)}.jpg",
                fitz.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 2, r.y1 + 2),
                scale=4.2,
            )
            if rel:
                out.append(f"/{rel}")
            if len(out) >= 4:
                break
    return out


def force_choice_images(page: fitz.Page, qid: str) -> list[dict]:
    """Rasterize A–D choice rows; prefer plain text for simple numbers."""
    from extract_questions import find_answer_choice_hits, render_clip

    hits = find_answer_choice_hits(page)
    end = page.rect.height
    ca = page.search_for("Correct Answer") or page.search_for("Rationale")
    if ca:
        end = min(end, ca[0].y0)

    row_imgs: list[fitz.Rect] = []
    for info in page.get_image_info(xrefs=True):
        r = fitz.Rect(info["bbox"])
        if hits and hits[0] is not None and r.y0 >= hits[0].y0 - 45 and r.y1 <= end + 5 and r.x0 < 220:
            row_imgs.append(r)

    objs: list[dict] = []
    for i, hit in enumerate(hits):
        if hit is None:
            objs.append({"text": "ABCD"[i]})
            continue
        y1 = end
        for j in range(i + 1, 4):
            if hits[j] is not None and hits[j].y0 > hit.y0 + 2:
                y1 = hits[j].y0
                break

        imgs = [r for r in row_imgs if r.y0 < y1 + 2 and r.y1 > hit.y0 - 8]
        txt = page.get_textbox(fitz.Rect(hit.x0, hit.y0 - 2, hit.x1 + 90, min(y1, hit.y0 + 30))).replace("\n", " ").strip()
        m = re.match(r"^[A-D]\.?\s*(-?\d+(?:\.\d+)?)\s*$", txt)
        # Prefer plain numeric text even if the PDF also embeds a digit glyph as an image.
        if m:
            objs.append({"text": m.group(1)})
            continue
        # Also accept "B. 4" with trailing junk / soft spaces
        m2 = re.search(r"^[A-D]\.?\s*(-?\d+(?:\.\d+)?)\b", txt)
        if m2 and (not imgs or max(r.height for r in imgs) < 22):
            objs.append({"text": m2.group(1)})
            continue

        if imgs:
            r0 = imgs[0]
            for r in imgs[1:]:
                r0 |= r
            clip = fitz.Rect(r0.x0 - 3, r0.y0 - 3, r0.x1 + 8, r0.y1 + 3)
        else:
            clip = fitz.Rect(
                hit.x1 + 1,
                hit.y0 - 4,
                min(page.rect.x1 - 20, hit.x1 + 360),
                min(y1 - 2, hit.y0 + 48),
            )
            if clip.height < 10:
                clip.y1 = clip.y0 + 28

        rel = render_clip(page, MATH_CHOICE_IMG / f"{qid}_{i}.jpg", clip, scale=4.2)
        objs.append({"image": f"/{rel}"} if rel else {"text": "ABCD"[i]})
    return objs


def assemble_bank_stem(page: fitz.Page, text: str, qid: str, want_figure: bool):
    """Mirror extract_math stem assembly: OCR + equation crops + figure."""
    figure = None
    fig_rect = None
    if want_figure or re.search(r"(?i)\b(graph|table|figure|chart|scatterplot|shaded|lines shown)\b", text):
        fig, fig_rect = crop_math_figure(page, MATH_FIG / f"{qid}.jpg", text)
        if fig:
            figure = f"/{fig}" if not str(fig).startswith("/") else fig

    prompt, equation_images = build_math_prompt(page, text, figure_rect=fig_rect, qid=qid)
    built_prompt_snapshot = prompt
    ocr_prompt = polish_ocr_stem(ocr_math_stem(page, figure_rect=fig_rect))
    kept_eqs = list(equation_images)

    if should_prefer_ocr_stem(prompt, ocr_prompt, bool(figure)):
        prompt = ocr_prompt
        equation_images = []
    elif bank_prompt_broken(prompt) and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        prompt = ocr_prompt
        equation_images = []
    elif figure and ocr_prompt and not ocr_looks_broken(ocr_prompt):
        bare = re.sub(r"\{\{eq:\d+\}\}", "", prompt or "")
        if bank_prompt_broken(prompt) or len(ocr_prompt) > len(bare):
            prompt = ocr_prompt
            equation_images = []

    if (
        kept_eqs
        and not equation_images
        and re.search(r"(?i)\b(given (system|equation)|equations above|system of equations)\b", prompt or "")
        and "{{eq:" not in (prompt or "")
    ):
        equation_images = kept_eqs
        prefix_parts = [f"{{{{eq:{i}}}}}" for i in range(len(equation_images))]
        prompt = "\n".join(prefix_parts + [prompt])

    # If OCR/readable prose is hollow but we still have equation crops, keep crops.
    if kept_eqs and not equation_images and ("{{eq:" in (built_prompt_snapshot or "")):
        if bank_prompt_broken(prompt) or readable_prompt_broken(prompt):
            prompt = built_prompt_snapshot
            equation_images = kept_eqs

    prompt = polish_ocr_stem(prompt or "")
    if figure or re.search(r"(?i)\b(scatterplot|table|graph|figure|shaded)\b", prompt or ""):
        prompt = strip_chart_noise(prompt)
        prompt = polish_ocr_stem(prompt)

    needs_eq = bool(
        re.search(
            r"(?i)\b(given (system|equation)|equations above|function defined by|linear function f,|value of f\()\b",
            prompt or "",
        )
        or readable_prompt_broken(prompt or "")
    )
    if (not equation_images or "{{eq:" not in (prompt or "")) and needs_eq:
        forced = force_equation_crops(page, qid)
        if forced:
            equation_images = forced
            prose = scrub_leading_ocr_junk(prompt or "", keep_leading_equations=False)
            prose = re.sub(r"\{\{eq:\d+\}\}", "", prose).strip()
            # Drop OCR equation crumbs before the English stem
            prose = re.sub(
                r"^.*?(?=(?:In the given|The solution|The system|If |For the given|What |Which ))",
                "",
                prose,
                count=1,
                flags=re.S,
            ).strip() or prose
            prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(equation_images)))
            prompt = f"{prefix}\n{prose}".strip()
    elif equation_images and "{{eq:" not in (prompt or ""):
        if re.search(r"(?i)\b(given (system|equation)|equations above|function defined by)\b", prompt or ""):
            prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(equation_images)))
            prompt = f"{prefix}\n{prompt}".strip()
        else:
            equation_images = []

    return prompt, equation_images, figure


def build_item(block: dict, bank_doc: fitz.Document, bank_index: dict[str, int], unanswered_index: dict[str, int]) -> dict | None:
    qid = block["id"]
    if block["answer"] is None:
        print(f"skip {qid}: missing answer")
        return None

    bank_i = bank_index.get(qid)
    skill = "Linear equations in one variable"
    difficulty = "Medium"
    figure = None
    equations = []
    choice_objs = None
    preview = None
    pdf_page = unanswered_index.get(qid, bank_i if bank_i is not None else 0) + 1
    page = None
    text = ""
    prompt = scrub_leading_ocr_junk(block.get("prompt") or "")

    if bank_i is not None:
        page = bank_doc[bank_i]
        text = page.get_text() or ""
        domain, sk, diff = parse_meta(text, "Math", MATH_DOMAINS)
        if sk:
            skill = sk
        if diff:
            difficulty = diff
        if domain and domain != "Algebra":
            print(f"warn {qid}: domain {domain!r} (expected Algebra)")

        want_figure = block["needs_figure"] or bool(
            re.search(r"(?i)\b(graph|table|shown|shaded|figure|chart)\b", prompt + "\n" + text)
        )
        bank_prompt, bank_eqs, figure = assemble_bank_stem(page, text, qid, want_figure)

        # Prefer bank/OCR assembly whenever readable is missing math or is junk.
        if bank_prompt and (
            readable_prompt_broken(prompt)
            or (bank_eqs and "{{eq:" in bank_prompt)
            or (figure and (readable_prompt_broken(prompt) or len(prompt) < 50))
            or (
                re.search(r"(?i)\b(given (system|equation)|equations above)\b", prompt)
                and bank_eqs
            )
        ):
            # If readable has a solid word-problem and bank only adds equations, merge.
            if (
                bank_eqs
                and not readable_prompt_broken(re.sub(r"^.*?(?=(?:A |An |The |In |For |If |John |During ))", "", prompt, flags=re.S) or prompt)
                and re.search(r"(?i)\b(given (system|equation)|equations above)\b", prompt)
                and "{{eq:" not in prompt
            ):
                prose = scrub_leading_ocr_junk(prompt, keep_leading_equations=False)
                # Fix common (a, y) -> (x, y)
                prose = re.sub(r"\(a,\s*y\)", "(x, y)", prose)
                prose = re.sub(r"\(a, y\)", "(x, y)", prose)
                prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(bank_eqs)))
                prompt = f"{prefix}\n{prose}".strip()
                equations = bank_eqs
            else:
                prompt = bank_prompt
                equations = bank_eqs
                prompt = re.sub(r"\(a,\s*y\)", "(x, y)", prompt)
        elif figure:
            prompt = scrub_leading_ocr_junk(prompt, keep_leading_equations=False)

        # Final safety: still hollow "above/given system" → force equation prefix if available
        if bank_eqs and re.search(r"(?i)\b(equations above|given system)\b", prompt) and "{{eq:" not in prompt:
            prefix = "\n".join(f"{{{{eq:{i}}}}}" for i in range(len(bank_eqs)))
            prompt = f"{prefix}\n{prompt}".strip()
            equations = bank_eqs

        prev = crop_math_pdf_preview(page, MATH_PDF_PREVIEW / f"{qid}.jpg")
        if prev:
            preview = f"/{prev}" if not str(prev).startswith("/") else f"/{prev.lstrip('/')}"

    if not prompt or not prompt.strip():
        print(f"skip {qid}: empty prompt")
        return None

    # Light cleanup on final prompt
    prompt = re.sub(r"\(a,\s*y\)", "(x, y)", prompt)
    prompt = re.sub(r"(?i)value of \(5\)", "value of f(5)", prompt)
    prompt = re.sub(r"(?i)values of and their", "values of x and their", prompt)
    prompt = re.sub(r"(?i)value of 8a \+ T[yY]", "value of 8x + 7y", prompt)
    prompt = re.sub(r"(?i)value of 8a \+ 7y", "value of 8x + 7y", prompt)
    prompt = re.sub(r"(?i)\bRationale\b.*$", "", prompt).strip()
    # Drop axis OCR leftovers that survived figure questions
    if figure:
        prompt = scrub_leading_ocr_junk(prompt, keep_leading_equations=False)

    if block["kind"] == "mc":
        readable_choices = [{"text": c} for c in block["choices"]] if len(block["choices"]) == 4 else []
        pdf_choices = extract_choices_text(text) if page is not None else None
        if page is not None and (choices_are_weak(readable_choices) or choices_are_weak(pdf_choices or [])):
            choice_objs = extract_choice_objects(page, qid, None)
            if choices_are_weak(choice_objs):
                choice_objs = force_choice_images(page, qid)
        else:
            choice_objs = readable_choices
        if choices_are_weak(choice_objs or []):
            print(f"warn {qid}: weak choices")

    item = {
        "id": qid,
        "topic": skill,
        "domain": "Algebra",
        "skill": skill,
        "difficulty": difficulty,
        "pool": POOL,
        "prompt": prompt,
        "type": block["kind"],
        "explanation": block["rationale"],
        "pdf": UNANSWERED_URL,
        "pdfPage": pdf_page,
    }
    if preview:
        item["pdfPreview"] = preview if preview.startswith("/") else "/" + preview
    if figure:
        item["figure"] = figure if figure.startswith("/") else "/" + figure
    # Policy: equation images are not used — Summer-style ASCII/KaTeX text only.
    # Keep {{eq:N}} out of prompts; figures/graphs/tables may still be images.
    prompt = re.sub(r"\{\{eq:\d+\}\}\n?", "", prompt).strip()
    prompt = re.sub(r"\n{3,}", "\n\n", prompt)
    item["prompt"] = prompt
    # Intentionally omit item["equations"] (text equations live in the prompt).

    if block["kind"] == "mc":
        item["choices"] = choice_objs or [{"text": c} for c in block["choices"]]
        item["answer"] = block["answer"]
    else:
        accepted = block["answer"] if isinstance(block["answer"], list) else [str(block["answer"])]
        item["choices"] = []
        item["acceptedAnswers"] = accepted
        item["answer"] = accepted[0] if accepted else ""
    return item


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
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    if not READABLE_PDF.exists():
        raise SystemExit(f"Missing readable PDF: {READABLE_PDF}")
    if not BANK_PDF.exists():
        raise SystemExit(f"Missing bank PDF: {BANK_PDF}")

    for folder in (MATH_FIG, MATH_CHOICE_IMG, MATH_PDF_PREVIEW, PUBLIC_MATH):
        folder.mkdir(parents=True, exist_ok=True)

    unanswered_path = PUBLIC_MATH / UNANSWERED_NAME
    print("Building unanswered Algebra PDF...")
    make_unanswered_pdf(BANK_PDF, unanswered_path)
    # Also keep a local answered copy for reference (not wired into the app)
    answered_copy = PUBLIC_MATH / "Educator-Bank-1-Algebra.pdf"
    if not answered_copy.exists():
        shutil.copy2(BANK_PDF, answered_copy)

    readable = fitz.open(READABLE_PDF)
    bank = fitz.open(BANK_PDF)
    unanswered = fitz.open(unanswered_path)
    bank_index = index_bank_pages(bank)
    unanswered_index = index_bank_pages(unanswered)
    blocks = parse_readable(readable)
    print(f"Parsed {len(blocks)} readable questions")

    existing = json.loads((DATA / "mathQuestions.json").read_text(encoding="utf-8"))
    # Re-import replaces prior Educator Bank Algebra rows from this script.
    kept = [
        q for q in existing
        if not (
            q.get("pool") == POOL
            and q.get("domain") == "Algebra"
            and str(q.get("pdf") or "").endswith(UNANSWERED_NAME)
        )
    ]
    summer = [q for q in kept if q.get("pool") == "Collegeboard Summer 2026"]
    summer_ids = {str(q.get("id")) for q in summer}
    # Fingerprint only against Summer Algebra prompts (not intra-batch).
    summer_fps = {
        fingerprint(q.get("prompt") or "")
        for q in summer
        if q.get("domain") == "Algebra" and fingerprint(q.get("prompt") or "")
    }

    added = []
    skipped_dup = 0
    seen_ids: set[str] = set()
    for block in blocks:
        qid = block["id"]
        if qid in summer_ids or qid in seen_ids:
            skipped_dup += 1
            continue
        fp = fingerprint(block["prompt"])
        if fp and fp in summer_fps:
            # Confirm substantial overlap, not a short-stem collision.
            if len(fp) >= 80:
                print(f"skip {qid}: prompt fingerprint matches Summer Algebra item")
                skipped_dup += 1
                continue
        item = build_item(block, bank, bank_index, unanswered_index)
        if not item:
            continue
        added.append(item)
        seen_ids.add(qid)

    merged = kept + added
    (DATA / "mathQuestions.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    update_skill_counts(merged)

    by_skill = Counter(q["skill"] for q in added)
    print(f"Added {len(added)} Educator Bank Algebra questions (skipped {skipped_dup} duplicates)")
    for skill, n in by_skill.most_common():
        print(f"  {n:3d}  {skill}")
    print(f"Unanswered PDF: {unanswered_path}")
    print(f"Total math questions now: {len(merged)}")

    # Bank embeds / table slots need a deterministic post-pass.
    try:
        from repair_educator_algebra_media import repair as repair_media

        byid = {q["id"]: q for q in merged}
        touched = repair_media(byid, bank)
        (DATA / "mathQuestions.json").write_text(
            json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Media repair pass: {len(set(touched))} questions")
    except Exception as exc:  # noqa: BLE001
        print(f"warn: media repair pass failed: {exc}")


if __name__ == "__main__":
    main()
