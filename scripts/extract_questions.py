#!/usr/bin/env python3
"""Extract SAT questions as readable text. Images only for figures/tables/graphs."""

from __future__ import annotations

import io
import json
import re
from collections import defaultdict
from pathlib import Path

import fitz
import pytesseract
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data"
MATH_FIG = ROOT / "public" / "qbank" / "math" / "figures"
READING_FIG = ROOT / "public" / "qbank" / "reading" / "figures"
MATH_CHOICE_IMG = ROOT / "public" / "qbank" / "math" / "choices"
READING_CHOICE_IMG = ROOT / "public" / "qbank" / "reading" / "choices"
MATH_PDF_PREVIEW = ROOT / "public" / "qbank" / "math" / "previews"

ENG_ANSWERED = Path("/Users/vedsingh/Downloads/English 150 questions.pdf")
ENG_UNANSWERED = Path("/Users/vedsingh/Downloads/English question (Unanswered).pdf")
MATH_ANSWERED = Path("/Users/vedsingh/Downloads/Math questions.pdf")
MATH_UNANSWERED = Path("/Users/vedsingh/Downloads/Math Questions (Unanswered).pdf")
MATH_PDF_PUBLIC = ROOT / "public" / "qbank" / "math"
MATH_PDF_UNANSWERED_URL = "/qbank/math/Math-Questions-Unanswered.pdf"
MATH_PDF_ANSWERED_URL = "/qbank/math/Math-Questions-Answered.pdf"
READING_PDF_PUBLIC = ROOT / "public" / "qbank" / "reading"
READING_PDF_UNANSWERED_URL = "/qbank/reading/English-Questions-Unanswered.pdf"
READING_PDF_ANSWERED_URL = "/qbank/reading/English-Questions-Answered.pdf"

RW_DOMAINS = [
    "Information and Ideas",
    "Craft and Structure",
    "Expression of Ideas",
    "Standard English Conventions",
]
MATH_DOMAINS = [
    "Algebra",
    "Advanced Math",
    "Problem-Solving and Data Analysis",
    "Geometry and Trigonometry",
]
SKILL_FIXES = {
    "One-variable data: Distributions and measures of center and spread":
        "One-variable data: distributions and measures of center and spread",
    "Two-variable data: Models and scatterplots":
        "Two-variable data: models and scatterplots",
    "Ratios, rates, propor tional relationships, and units":
        "Ratios, rates, proportional relationships, and units",
}


def clean_text(s: str) -> str:
    s = (s or "").replace("\xa0", " ")
    replacements = [
        ("Ear th", "Earth"), ("cer tain", "certain"), ("par ticles", "particles"),
        ("proper ty", "property"), ("mor tar", "mortar"), ("propor tions", "proportions"),
        ("propor tional", "proportional"), ("suppor t", "support"),
        ("par ticipants", "participants"), ("par ticular", "particular"),
        ("char ts", "charts"), ("througho", "through"),
        ("repor t", "report"), ("repor ted", "reported"), ("repor ting", "reporting"),
        ("impor tant", "important"), ("impor tance", "importance"),
        ("star ting", "starting"), ("conver ting", "converting"),
        ("ver tical", "vertical"), ("ver tex", "vertex"),
    ]
    for a, b in replacements:
        s = s.replace(a, b)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def clean_math_snippet(s: str) -> str:
    s = (s or "").replace("\n", " ")
    s = s.replace("—", "-").replace("–", "-").replace("−", "-")
    s = s.replace("¢", "x").replace("£", "E")
    s = s.replace("≥", ">=").replace("≤", "<=")
    s = s.replace("◦", "°").replace("º", "°")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*=\s*", " = ", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    s = re.sub(r"(?<=\d)a(?=\d)", "x", s)
    s = s.replace("g(a)", "g(x)").replace("14a", "14x").replace("g9(x)", "g(x)").replace("14z", "14x")
    s = re.sub(r"\bg\(\s*a\s*\)", "g(x)", s)
    s = re.sub(r"\b9\(z\)", "g(x)", s)
    s = re.sub(r"\by\s*=\s*9\(", "y = g(", s)
    s = re.sub(r"y\s*=\s*g9\(", "y = g(", s)
    s = re.sub(r"^\(x\)\s*=\s*3\s*\(14x", "g(x) = 3(14x", s)
    s = re.sub(r"g\(x\)\s*=\s*3\(?14x\s*-\s*$", "g(x) = 3(14x - 15)", s)
    s = re.sub(r"g\(x\)\s*=\s*3\(?14x?\s*$", "g(x) = 3(14x - 15)", s)
    s = re.sub(r"y\s*=\s*g\s*\(\s*x\s*\)\s*-\s*2", "y = g(x) - 2", s)
    s = re.sub(r"(?i)y\s*=\s*m[xz7]\s*\+\s*[b4h]\b", "y = mx + b", s)
    s = re.sub(r"(?i)y\s*=\s*mz\s*\+\s*4\b", "y = mx + b", s)
    # Exponential decay OCR: y = 7,400(0.87)" → y = 7,400(0.87)^x
    s = re.sub(
        r"(?i)(y\s*=\s*\d{1,3}(?:,\d{3})*\(\d*\.\d+\))\"?\s*$",
        lambda m: m.group(1).replace(" ", "") + "^x",
        s,
    )
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def extract_simple_math_token(snip: str) -> str | None:
    """Pull a clean text token (money, inequality, short number) out of OCR noise."""
    s = clean_math_snippet(snip)
    if not s:
        return None

    money = re.search(r"\$\s*\d{1,4}(?:,\d{3})*(?:\.\d{1,2})?", s)
    if money and len(s) <= 48:
        return re.sub(r"\s+", "", money.group(0))

    # x >= 2, x > 2, n ≤ 10, etc. — only when the whole snip is that inequality
    ineq = re.fullmatch(
        r"([a-zA-Z])\s*(>=|<=|>|<|=)\s*(-?\d+(?:,\d{3})*(?:\.\d+)?)",
        s.strip(" ,.;:"),
    )
    if ineq:
        return f"{ineq.group(1)} {ineq.group(2)} {ineq.group(3)}"

    # bare decimals / integers / percents / comma thousands
    num = re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?", s.strip(" ,.;:"))
    if num:
        return num.group(0)
    num = re.fullmatch(r"-?\d+(?:\.\d+)?%?", s.strip(" ,.;:"))
    if num:
        return num.group(0)

    # Exponential / decay models — keep as text only if clean; else let caller image
    exp = re.fullmatch(
        r"y\s*=\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*\(\s*\d*\.?\d+\s*\)\s*\^\s*[a-z]",
        s.replace("−", "-"),
        re.I,
    )
    if exp:
        return re.sub(r"\s+", "", exp.group(0).replace(" ", ""))

    # short clean algebraic forms
    if len(s) <= 36 and math_ocr_ok(s):
        return s
    return None


def math_ocr_ok(snip: str) -> bool:
    if not snip or len(snip) < 1:
        return False
    if snip.count("(") != snip.count(")"):
        return False
    if re.search(r"[¢£§�]", snip):
        return False
    if re.search(r"(?i)\b(Ww|THT|P\s*_)\b", snip):
        return False
    # Allow common math punctuation: $ ° inequalities
    if re.search(r"[^\w\s=$+\-−×÷/().,^|<>°%]", snip):
        return False
    # reject obvious garbage prefixes/suffixes
    if re.search(r"(?i)\b[a-z]{4,}\s*=", snip) and not re.search(r"(?i)\b(sin|cos|tan|log|ln)\b", snip):
        # allow f(x)= ... style
        if not re.search(r"(?i)\b[fgh]\s*\(", snip):
            return False
    if re.search(r"(?i)=.*[a-z]{4,}$", snip) and not re.search(r"(?i)\b(sin|cos|tan|log|ln)\b", snip):
        return False
    # reject OCR hash of dots
    if snip.count("ee") >= 2 or snip.count("..") >= 2:
        return False
    return True


def ocr_equation_region(page: fitz.Page, rect: fitz.Rect) -> str:
    padded = fitz.Rect(rect.x0 - 4, rect.y0 - 5, rect.x1 + 4, rect.y1 + 5)
    best = ""
    for psm in (7, 6, 13):
        snip = clean_math_snippet(ocr_clip(page, padded, psm=psm))
        if len(snip) > len(best):
            best = snip
    return best


def clean_choice_ocr(s: str) -> str:
    s = (s or "").strip().replace("—", "-").replace("–", "-").replace("−", "-")
    s = re.sub(r"\s+", "", s)
    if re.fullmatch(r"-?[A-Za-z0-9./]+", s) and any(ch.isalpha() for ch in s):
        # digit-looking OCR on short numeric answers
        trans = str.maketrans({
            "A": "4", "a": "4", "O": "0", "o": "0", "l": "1", "I": "1",
            "Z": "2", "S": "5", "B": "8", "G": "6", "T": "7", "g": "9",
            "d": "5", "D": "5", "q": "9",
        })
        s = s.translate(trans)
    return s


def group_pages(doc: fitz.Document) -> list[dict]:
    pages = []
    for i in range(doc.page_count):
        text = doc[i].get_text("text")
        m = re.search(r"Question ID:\s*([0-9a-fA-F]+)", text)
        pages.append({"index": i, "id": m.group(1) if m else None, "text": text})
    groups = []
    current = None
    for p in pages:
        if p["id"]:
            if current:
                groups.append(current)
            current = {"id": p["id"], "pages": [p["index"]], "text": p["text"]}
        elif current is not None:
            current["pages"].append(p["index"])
            current["text"] += "\n" + p["text"]
    if current:
        groups.append(current)
    return groups


def parse_meta(text: str, subject: str, domains: list[str]):
    pattern = (
        rf"Assessment\s*\nTest\s*\nDomain\s*\nSkill\s*\nDifficulty\s*\nSAT\s*\n"
        rf"{re.escape(subject)}\s*\n([\s\S]*?)\nQuestion\n"
    )
    m = re.search(pattern, text)
    if not m:
        return None, None, None
    lines = [x.strip() for x in m.group(1).strip().split("\n") if x.strip()]
    if not lines:
        return None, None, None
    difficulty = lines[-1]
    words = " ".join(lines[:-1]).split()
    domain = skill = None
    for d in sorted(domains, key=lambda x: -len(x.split())):
        dw = d.split()
        if words[: len(dw)] == dw:
            domain = d
            skill = " ".join(words[len(dw) :])
            break
    if skill:
        skill = re.sub(r"\s+", " ", skill)
        skill = SKILL_FIXES.get(skill, skill)
    return domain, skill, difficulty


def extract_choices_text(block: str) -> list[str] | None:
    m = re.search(
        r"\nA\.\s*(.*?)\nB\.\s*(.*?)\nC\.\s*(.*?)\nD\.\s*(.*?)(?:\nID:\s*[0-9a-fA-F]{8}\s+Answer\b|\nCorrect Answer:|\nRationale|\Z)",
        block,
        re.S,
    )
    if not m:
        return None
    choices = [clean_text(c.replace("\n", " ")) for c in m.groups()]
    # Student Bank PDFs sometimes glue "ID: <qid> Answer" onto choice D.
    choices = [
        re.sub(r"\s*ID:\s*[0-9a-fA-F]{8}\s+Answer\b.*$", "", c, flags=re.I).strip()
        for c in choices
    ]
    if any("Correct Answer" in c for c in choices):
        return None
    if sum(1 for c in choices if len(c) > 0) < 3:
        return None
    return choices


def extract_question_body(text: str) -> str:
    m = re.search(r"\nQuestion\n([\s\S]*?)(?:\nAnswer\n|\nCorrect Answer:)", text)
    if not m:
        return ""
    body = m.group(1).strip()
    body = re.split(r"\nA\.\s", body, maxsplit=1)[0].strip()
    return body


def split_passage_and_prompt(body: str) -> tuple[str, str]:
    lines = body.split("\n")
    stem_idx = None
    stem_starts = (
        "Which choice", "As used in", "The writer", "The student", "Based on",
        "According to", "What is the", "What choice", "Which quotation",
        "Which finding", "Which statement", "Which of the following", "Which detail",
        "Taken together", "The text",
        "How does", "Why does",
    )
    for i, line in enumerate(lines):
        s = line.strip()
        if any(s.startswith(p) for p in stem_starts):
            stem_idx = i
            break
    if stem_idx is None:
        return clean_text(body), "Select the best answer."
    passage = clean_text("\n".join(lines[:stem_idx]))
    prompt = clean_text("\n".join(lines[stem_idx:]))
    if not passage:
        return clean_text(body), "Select the best answer."
    return passage, prompt


def correct_answer(text: str):
    m = re.search(r"Correct Answer:\s*([^\n]+)", text)
    if not m:
        return None, None
    raw = m.group(1).strip()
    if re.fullmatch(r"[A-D]", raw):
        return "mc", ord(raw) - ord("A")
    answers = [a.strip() for a in raw.split(",") if a.strip()]
    return "spr", answers


def extract_explanation(text: str) -> str:
    m = re.search(r"\nRationale\n([\s\S]*)$", text)
    if not m:
        return ""
    expl = m.group(1).strip()
    expl = re.split(r"\nQuestion ID:", expl, maxsplit=1)[0].strip()
    # drop empty equation holes markers left by missing drawings
    expl = re.sub(r"\s{2,}", " ", expl)
    return clean_text(expl)


def find_label_rect(page: fitz.Page, label: str) -> fitz.Rect | None:
    hits = page.search_for(label)
    if not hits:
        return None
    if label == "Question":
        # Prefer the section header, not "Question ID"
        header = [h for h in hits if h.width < 55 and h.x0 < 80]
        if header:
            return header[-1]
    if label == "Answer":
        # Prefer the choices header, not "Correct Answer"
        header = [h for h in hits if h.width < 55 and h.x0 < 80]
        if header:
            return header[0]
    return hits[0]


def find_y(page: fitz.Page, needle: str, default: float | None = None) -> float | None:
    rect = find_label_rect(page, needle)
    if rect is None:
        return default
    return rect.y0


def safe_pixmap(page: fitz.Page, clip: fitz.Rect, scale: float = 5.0):
    rect = page.rect
    clip = fitz.Rect(
        max(rect.x0, min(clip.x0, rect.x1 - 2)),
        max(rect.y0, min(clip.y0, rect.y1 - 2)),
        min(rect.x1, max(clip.x1, rect.x0 + 2)),
        min(rect.y1, max(clip.y1, rect.y0 + 2)),
    )
    if clip.width < 4 or clip.height < 4:
        return None
    try:
        return page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    except Exception:
        return None


def render_clip(page: fitz.Page, out_path: Path, clip: fitz.Rect, scale: float = 2.6) -> str:
    pix = safe_pixmap(page, clip, scale=scale)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    gray = ImageOps.grayscale(img)
    bw = gray.point(lambda p: 0 if p < 245 else 255)
    bbox = ImageOps.invert(bw).getbbox()
    if bbox:
        pad = 10
        bbox = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(img.width, bbox[2] + pad),
            min(img.height, bbox[3] + pad),
        )
        img = img.crop(bbox)
    if img.width < 4 or img.height < 4:
        return ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=92, optimize=True)
    return str(out_path.relative_to(ROOT / "public")).replace("\\", "/")


def question_preview_clip(page: fitz.Page) -> fitz.Rect | None:
    """Clip covering the Question stem + Answer choices only (no rationale)."""
    q_rect = find_label_rect(page, "Question")
    if q_rect is None:
        return None

    end_y = page.rect.height - 8
    for label in ("Correct Answer", "Rationale"):
        hits = page.search_for(label) or []
        for h in hits:
            if h.y0 > q_rect.y1 + 20:
                end_y = min(end_y, h.y0 - 4)

    # Prefer ending just below the last choice marker when present
    hits = find_answer_choice_hits(page)
    last = None
    for h in hits:
        if h is not None and h.y0 > q_rect.y0:
            last = h
    if last is not None:
        # Choice row height is typically ~18–40pt; leave room for stacked fractions
        choice_bottom = last.y1 + 36
        # Don't extend into Correct Answer / Rationale
        end_y = min(end_y, max(choice_bottom, last.y0 + 28))

    a_rect = find_label_rect(page, "Answer")
    if a_rect is not None and last is None:
        # SPR / empty choices: keep a modest band under Answer
        end_y = min(end_y, a_rect.y1 + 80)

    # If still huge (SPR with no Answer label), trim to content words below Question
    if end_y - q_rect.y0 > 520:
        words = [w for w in page.get_text("words") if w[1] >= q_rect.y0 - 2]
        if words:
            content_bottom = max(w[3] for w in words if w[1] < end_y)
            end_y = min(end_y, content_bottom + 16)

    clip = fitz.Rect(
        page.rect.x0 + 10,
        max(page.rect.y0 + 4, q_rect.y0 - 4),
        page.rect.x1 - 10,
        min(page.rect.y1 - 4, end_y),
    )
    if clip.height < 40:
        return None
    return clip


def crop_math_pdf_preview(page: fitz.Page, out_path: Path) -> str:
    """Render a cropped JPEG of the question + choices (no answer key / rationale)."""
    clip = question_preview_clip(page)
    if clip is None:
        # Fallback: most of the page but still cut Correct Answer if present
        q_rect = find_label_rect(page, "Question")
        y0 = (q_rect.y0 - 4) if q_rect else page.rect.y0 + 100
        y1 = page.rect.height - 8
        for label in ("Correct Answer", "Rationale"):
            hits = page.search_for(label) or []
            for h in hits:
                if h.y0 > y0 + 20:
                    y1 = min(y1, h.y0 - 4)
        clip = fitz.Rect(page.rect.x0 + 10, y0, page.rect.x1 - 10, y1)
    # Don't auto-trim whitespace aggressively — keep full question band
    pix = safe_pixmap(page, clip, scale=2.4)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=90, optimize=True)
    return str(out_path.relative_to(ROOT / "public")).replace("\\", "/")


def ocr_clip(page: fitz.Page, clip: fitz.Rect, psm: int = 7) -> str:
    pad = fitz.Rect(clip.x0 - 2, clip.y0 - 3, clip.x1 + 2, clip.y1 + 3)
    pix = safe_pixmap(page, pad, scale=5.0)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((max(1, img.width * 2), max(1, img.height * 2)), Image.Resampling.LANCZOS)
    img = img.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(img, config=f"--oem 3 --psm {psm}").strip()


def drawing_rects(page: fitz.Page, y0: float, y1: float, *, include_hairlines: bool = False) -> list[fitz.Rect]:
    out = []
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"])
        if include_hairlines:
            if r.width < 0.4 and r.height < 0.4:
                continue
        elif r.width < 1.2 or r.height < 1.2:
            continue
        if r.y1 < y0 - 2 or r.y0 > y1 + 2:
            continue
        out.append(r)
    return out


def merge_rects(rects: list[fitz.Rect], x_gap: float = 18, y_gap: float = 8) -> list[fitz.Rect]:
    if not rects:
        return []
    rects = sorted(rects, key=lambda r: ((r.y0 + r.y1) / 2, r.x0))
    clusters: list[list[fitz.Rect]] = []
    for r in rects:
        placed = False
        for cluster in clusters:
            u = cluster[0]
            for x in cluster[1:]:
                u |= x
            mid = (r.y0 + r.y1) / 2
            umid = (u.y0 + u.y1) / 2
            if abs(mid - umid) <= max(y_gap, 12) and r.x0 <= u.x1 + x_gap:
                cluster.append(r)
                placed = True
                break
        if not placed:
            clusters.append([r])
    merged = []
    for cluster in clusters:
        u = cluster[0]
        for r in cluster[1:]:
            u |= r
        merged.append(u)
    return merged


def is_figure_cluster(rect: fitz.Rect, page: fitz.Page, text: str) -> bool:
    keywords = bool(re.search(r"\b(graph|table|figure|chart|scatterplot|diagram)\b", text, re.I))
    wide = rect.width > 140 and rect.height > 55
    tallish = rect.height > 90 and rect.width > 90
    if rect.height < 40 or rect.width < 60:
        return False
    if keywords and (wide or tallish):
        return True
    # Geometry diagrams are often shorter than charts
    if wide and rect.height >= 55 and len(page.get_drawings()) >= 20:
        return True
    if wide and tallish and len(page.get_drawings()) >= 40:
        return True
    return False


def find_math_stem_start_y(page: fitz.Page, y0: float, y1: float) -> float | None:
    """First prose line of the stem (after an optional figure/note block)."""
    lines: dict[int, list] = defaultdict(list)
    for w in page.get_text("words"):
        if y0 <= w[1] <= y1 and w[4].strip():
            lines[line_key(w[1])].append(w)
    for key in sorted(lines):
        ws = sorted(lines[key], key=lambda w: w[0])
        text = " ".join(w[4] for w in ws)
        words = text.split()
        if len(words) < 6:
            continue
        if re.match(r"^(Note|Figure|Table|Graph|Seating|Proportion)\b", text, re.I):
            continue
        if re.match(r"^[A-Z]", text) and sum(ch.isalpha() for ch in text) >= 18:
            return min(w[1] for w in ws)
    return None


def find_math_question_cue_y(page: fitz.Page, y0: float, y1: float) -> float | None:
    """Y of the actual ask line when a figure/table sits between intro and question."""
    if y1 is None:
        y1 = page.rect.height * 0.85
    cues = (
        "Which of the following",
        "What is the value",
        "What is a possible",
        "What is the area",
        "What is this",
        "What is the frequency",
        "Which equation",
        "Which expression",
        "Which of these",
        "Based on the",
        "If a room",
        "If a student",
        "How many times",
    )
    best = None
    for cue in cues:
        for hit in page.search_for(cue):
            if y0 + 20 <= hit.y0 <= y1:
                if best is None or hit.y0 < best:
                    best = hit.y0
    return best


def crop_math_figure(page: fitz.Page, out_path: Path, text: str) -> tuple[str | None, fitz.Rect | None]:
    """
    Crop only the diagram/table/note block — not the question stem prose.

    Handles two layouts:
      A) figure above the stem
      B) intro prose → figure/table → question cue (scatterplots, tables)
    """
    q_rect = find_label_rect(page, "Question")
    if q_rect is None:
        return None, None
    qy = q_rect.y1 + 1
    ay = find_y(page, "Answer") or find_y(page, "Correct Answer") or (page.rect.height * 0.78)
    has_kw = bool(
        re.search(
            r"\b(figure shown|graph|table|diagram|scatterplot|chart|bar graph)\b",
            text,
            re.I,
        )
    )

    stem_y = find_math_stem_start_y(page, qy, ay)
    cue_y = find_math_question_cue_y(page, qy, ay)

    # Layout B: figure/table between intro paragraph and the ask line
    if (
        stem_y is not None
        and cue_y is not None
        and cue_y > stem_y + 50
        and has_kw
    ):
        # End of intro = last long prose line before the cue
        intro_bottom = stem_y + 12
        lines: dict[int, list] = defaultdict(list)
        for w in page.get_text("words"):
            if stem_y - 2 <= w[1] <= cue_y - 8 and w[4].strip():
                lines[line_key(w[1])].append(w)
        for key in sorted(lines):
            ws = sorted(lines[key], key=lambda w: w[0])
            text_ln = " ".join(w[4] for w in ws)
            if re.match(r"^(Seating|Proportion|capacity|Less than|Greater than)\b", text_ln, re.I):
                break
            if re.fullmatch(r"[\d\s.Oxy−-]+", text_ln):
                break
            # Axis / short chart labels — figure has started
            if len(text_ln.split()) <= 3 and re.fullmatch(
                r"(?i)(temperature|depth|time|year|distance|height|weight|cost|price|x|y|o|\(.*\))+",
                text_ln.replace(" ", ""),
            ):
                break
            alpha = sum(ch.isalpha() for ch in text_ln)
            words_n = len(text_ln.split())
            if words_n >= 5 and alpha >= 20:
                # Keep consuming wrapped intro lines (don't stop at first "shown")
                intro_bottom = max(w[3] for w in ws)
                continue
            if re.search(r"(?i)\b(also shown|is shown|are shown|is also shown)\b", text_ln):
                intro_bottom = max(w[3] for w in ws)
                continue
            # Short non-prose → figure content
            if words_n <= 4 and alpha < 18:
                break
        mid_top = intro_bottom + 2
        mid_bottom = cue_y - 4
        if mid_bottom > mid_top + 36:
            mid_draws = drawing_rects(page, mid_top, mid_bottom, include_hairlines=True)
            # Bar charts use tall thin filled rects — allow height-dominant shapes
            mid_solid = [
                r for r in mid_draws
                if (r.width >= 6 and r.height >= 6)
                or (r.width >= 12 and r.height >= 30)
                or (r.width >= 30 and r.height >= 2)
            ]
            if not mid_solid and has_kw:
                # Include any stroke in the band for graphs drawn as many thin lines
                mid_solid = [r for r in mid_draws if r.width * r.height >= 8 or r.height >= 20]
            if mid_solid or has_kw:
                mid_clusters = merge_rects(mid_solid, x_gap=36, y_gap=22) if mid_solid else []
                if mid_clusters or has_kw:
                    if mid_clusters:
                        core = max(mid_clusters, key=lambda r: r.width * r.height)
                        union = core
                        for r in mid_draws:
                            if r.y0 >= mid_top - 4 and r.y1 <= mid_bottom + 4:
                                union |= r
                    else:
                        union = fitz.Rect(page.rect.x0 + 40, mid_top, page.rect.x1 - 40, mid_bottom)
                    for w in page.get_text("words"):
                        if not (mid_top - 2 <= w[1] <= mid_bottom + 2):
                            continue
                        if w[1] >= cue_y - 2:
                            continue
                        token = w[4].strip()
                        # Don't pull wrapped stem prose into the figure crop
                        if len(token) > 10 and sum(ch.isalpha() for ch in token) >= 6:
                            continue
                        wr = fitz.Rect(w[0], w[1], w[2], w[3])
                        # Skip leftover intro words sitting above the drawing core
                        if mid_clusters and wr.y1 < core.y0 - 2 and sum(ch.isalpha() for ch in token) >= 3:
                            continue
                        union |= wr
                    clip = fitz.Rect(
                        max(page.rect.x0 + 12, union.x0 - 14),
                        max(page.rect.y0 + 8, max(mid_top, union.y0 - 10)),
                        min(page.rect.x1 - 12, union.x1 + 14),
                        min(page.rect.y1 - 8, mid_bottom),
                    )
                    if clip.height >= 40 and clip.width >= 60:
                        rel = render_figure_clip(page, out_path, clip, scale=3.4)
                        if rel:
                            return f"/{rel}", clip

    # Layout A: figure above stem
    fig_bottom = (stem_y - 2) if stem_y is not None else ay
    draws = drawing_rects(page, qy, fig_bottom, include_hairlines=True)
    solid = [r for r in draws if (r.width >= 8 and r.height >= 8) or (r.width >= 40 and r.height >= 3)]
    if not solid:
        # Fallback: large drawing block anywhere above Answer, still above cue if present
        top = qy
        bottom = (cue_y - 2) if cue_y else (stem_y - 2 if stem_y else ay)
        if bottom > top + 40:
            draws = drawing_rects(page, top, bottom, include_hairlines=True)
            solid = [r for r in draws if (r.width >= 8 and r.height >= 8) or (r.width >= 40 and r.height >= 3)]
            fig_bottom = bottom
    if not solid:
        return None, None

    clusters = merge_rects(solid, x_gap=28, y_gap=16)
    if not clusters:
        return None, None
    core = max(clusters, key=lambda r: r.width * r.height)
    if core.width * core.height < 3500 and not has_kw:
        return None, None
    if core.height < 45 and core.width < 120 and not has_kw:
        return None, None

    union = core
    for r in draws:
        if r.y1 < qy or r.y0 > fig_bottom:
            continue
        if r.y0 > core.y1 + 90:
            continue
        union |= r

    for w in page.get_text("words"):
        if not (max(qy, union.y0 - 24) <= w[1] <= min(fig_bottom, union.y1 + 28)):
            continue
        token = w[4].strip()
        if len(token) > 8:
            continue
        wr = fitz.Rect(w[0], w[1], w[2], w[3])
        cx = (wr.x0 + wr.x1) / 2
        if abs(cx - ((union.x0 + union.x1) / 2)) > max(union.width * 0.75, 120):
            continue
        # Don't swallow stem prose into the figure
        if stem_y is not None and wr.y0 >= stem_y - 1 and len(token) > 1:
            joined = token
            if sum(ch.isalpha() for ch in joined) >= 3 and joined.lower() not in {
                "note", "figure", "not", "drawn", "scale", "x", "y"
            }:
                # likely stem word — skip unless it's a short vertex label
                if len(joined) > 3:
                    continue
        union |= wr

    # Keep figure above stem prose when they would overlap
    y1 = union.y1 + 12
    if stem_y is not None and y1 > stem_y - 2:
        y1 = stem_y - 2
    if cue_y is not None and y1 > cue_y - 2:
        y1 = cue_y - 2

    clip = fitz.Rect(
        max(page.rect.x0 + 12, union.x0 - 12),
        max(page.rect.y0 + 8, union.y0 - 10),
        min(page.rect.x1 - 12, union.x1 + 14),
        min(page.rect.y1 - 8, y1),
    )
    if clip.height < 40 or clip.width < 60:
        return None, None
    rel = render_figure_clip(page, out_path, clip, scale=3.4)
    if not rel:
        return None, None
    return f"/{rel}", clip


def ocr_region_text(page: fitz.Page, clip: fitz.Rect, scale: float = 3.4, psm: int = 6) -> str:
    pix = safe_pixmap(page, clip, scale=scale)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    raw = pytesseract.image_to_string(img, config=f"--oem 3 --psm {psm}")
    return clean_text(raw)


def ocr_math_stem(page: fitz.Page, figure_rect: fitz.Rect | None = None) -> str:
    q_rect = find_label_rect(page, "Question")
    a_rect = find_label_rect(page, "Answer")
    if q_rect is None:
        return ""
    y0 = q_rect.y1 + 2
    if a_rect is not None:
        y1 = a_rect.y0 - 2
    else:
        # Unanswered pages often lack an Answer label; fall back to a lower band
        y1 = find_y(page, "Answer") or (page.rect.height * 0.78)
        y1 = min(y1 - 2, page.rect.height - 8)
    cue_y = find_math_question_cue_y(page, q_rect.y1 + 1, y1)

    # Mid-page figure/table: OCR intro above + ask line below, skip the figure band
    if figure_rect is not None and cue_y is not None and figure_rect.y0 > y0 + 20 and figure_rect.y1 < cue_y:
        top = ocr_region_text(
            page,
            fitz.Rect(page.rect.x0 + 16, y0, page.rect.x1 - 24, max(y0 + 8, figure_rect.y0 - 2)),
            scale=3.6,
            psm=6,
        )
        bot = ocr_region_text(
            page,
            fitz.Rect(page.rect.x0 + 16, min(y1, figure_rect.y1 + 2), page.rect.x1 - 24, y1),
            scale=3.6,
            psm=6,
        )
        text = clean_text((top + "\n" + bot).strip())
    elif figure_rect is not None:
        # Prefer stem starting at true prose line if figure crop overlapped it
        stem_y = find_math_stem_start_y(page, q_rect.y1 + 1, y1)
        start = figure_rect.y1 + 2
        if stem_y is not None and stem_y < figure_rect.y1 - 5:
            # Figure overlapped stem — OCR from stem start but we'll strip chart later
            start = stem_y - 1
        # Also try a full-band OCR when below-figure crop would be tiny
        if y1 - start < 28:
            start = q_rect.y1 + 2
        if y1 - start < 12:
            return ""
        # Short ask line below the figure: crop tightly around that line
        if stem_y is not None and stem_y >= figure_rect.y1 - 2:
            clip = fitz.Rect(
                page.rect.x0 + 12,
                stem_y - 3,
                page.rect.x1 - 12,
                min(y1, stem_y + 42),
            )
            text = ocr_region_text(page, clip, scale=4.2, psm=6)
        else:
            clip = fitz.Rect(page.rect.x0 + 16, start, page.rect.x1 - 24, y1)
            # Short post-figure stems (SPR geometry) need higher-res OCR
            scale = 4.2 if (y1 - start) < 55 else 3.6
            text = ocr_region_text(page, clip, scale=scale, psm=6)
        # If truncated, fall back to full question band OCR
        if prompt_looks_broken(text) or len(text) < 40:
            full = ocr_region_text(
                page,
                fitz.Rect(page.rect.x0 + 16, q_rect.y1 + 2, page.rect.x1 - 24, y1),
                scale=3.4,
                psm=6,
            )
            if len(full) > len(text) + 20 and not prompt_looks_broken(full):
                text = full
            elif stem_y is not None:
                line = ocr_region_text(
                    page,
                    fitz.Rect(page.rect.x0 + 12, stem_y - 3, page.rect.x1 - 12, min(y1, stem_y + 42)),
                    scale=4.5,
                    psm=6,
                )
                if line and not prompt_looks_broken(line):
                    text = line
    else:
        stem_y = find_math_stem_start_y(page, q_rect.y1 + 1, y1)
        if stem_y is not None:
            y0 = stem_y - 1
        if y1 - y0 < 12:
            return ""
        clip = fitz.Rect(page.rect.x0 + 16, y0, page.rect.x1 - 24, y1)
        text = ocr_region_text(page, clip, scale=3.6, psm=6)

    text = re.sub(r"\bNote:\s*Figure not drawn to scale\.?\s*", "", text, flags=re.I)
    text = re.sub(r"\bXY\s+Z\b", "XYZ", text)
    text = re.sub(r"\bX\s+Y\s+Z\b", "XYZ", text)
    text = re.sub(r"\b_([A-Z])\b", r"\1", text)
    text = re.sub(r"\bangie\b", "angle", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def digit_count(s: str) -> int:
    return sum(ch.isdigit() for ch in (s or ""))


def ocr_looks_broken(prompt: str) -> bool:
    p = prompt or ""
    if not p.strip():
        return True
    if re.search(r"[™¢£§�]", p):
        return True
    if re.search(r"(?i)\bVOTTINVN\b|\bet\s*\|\s*r?\d|\bL\s*=\s*[A-Z]{4,}", p):
        return True
    if re.search(r"(?i)\bassociated with th\b", p):
        return True
    # geometry letter confusions that are worse than keeping equation crops
    if re.search(r"(?i)\bline\s+[¢c]\s+intersects\s+lines\s+7\b", p):
        return True
    if re.search(r"(?i)\blines\s+7\s+and\s+[&%]\b", p):
        return True
    return False


def should_prefer_ocr_stem(built: str, ocr: str, has_figure: bool) -> bool:
    if not ocr or len(ocr) < 24:
        return False
    if ocr_looks_broken(ocr):
        return False
    if prompt_looks_broken(built) and not ocr_looks_broken(ocr):
        return True
    # Money / inequalities that OCR captured as real text beat equation images
    if "{{eq:" in (built or "") and re.search(r"\$\d+(?:\.\d+)?", ocr):
        return True
    if "{{eq:" in (built or "") and re.search(r"\b[a-zA-Z]\s*(>=|<=|>|<)\s*-?\d+", ocr):
        return True
    # Word problems: prefer OCR when it recovered more numeric values
    bare = re.sub(r"\{\{eq:\d+\}\}", "", built or "")
    if digit_count(ocr) >= digit_count(bare) + 2 and sum(ch.isalpha() for ch in ocr) >= 50:
        if not has_figure or "{{eq:" not in (built or ""):
            return True
    # Word problems without figures: full-stem OCR is usually cleaner than eq crops
    if not has_figure and "{{eq:" in (built or "") and sum(ch.isalpha() for ch in ocr) >= 80:
        return True
    if len(ocr) > len(bare) + 15 and "{{eq:" in (built or ""):
        return True
    # Prefer OCR when it recovers function names / variables the PDF build dropped
    if re.search(r"(?i)functions\s+and\s+model", built or "") and re.search(r"(?i)functions\s+f\s+and\s+g", ocr):
        return True
    if re.search(r"(?i)where\s*,\s*,\s*and", built or "") and re.search(r"(?i)where\s+a,\s*b", ocr):
        return True
    if re.search(r"(?i)^y\s*=\s*\d\s*$", built or "", re.M) and re.search(r"(?i)equipment\s+x\s+years", ocr):
        return True
    if re.search(r"(?i)JEIWEE|f9r7", built or "") and re.search(r"(?i)9x\s*\+\s*4", ocr):
        return True
    # Don't prefer mangled circle OCR over equation crops
    if "{{eq:" in (built or "") and re.search(r"\(~|\)[\"”]", ocr or ""):
        return False
    return False


def polish_ocr_stem(text: str) -> str:
    t = clean_text(text or "")
    t = re.sub(r"\bfunction\s+f\s+gives\b", "function gives", t, flags=re.I)
    t = re.sub(r"\bpurchasing\s+x\s+sessions\b", "purchasing x sessions", t, flags=re.I)
    t = re.sub(r"\bx\s*>\s*2\b", "x > 2", t)
    t = re.sub(r"\bx\s*>=\s*2\b", "x >= 2", t)
    # Common OCR failures for squared units / variables drawn as vectors
    t = re.sub(r"\(in[\*?\^²2]\)", "(in²)", t, flags=re.I)
    t = re.sub(r"(\d)\s*in[\*?\^²2?](?=\s|[.,;:]|$)", r"\1 in²", t, flags=re.I)
    t = re.sub(r"\bin[\*?\^²](?=\s|[.,;:]|$)", "in²", t, flags=re.I)
    t = re.sub(r"\bin2\b", "in²", t, flags=re.I)
    t = re.sub(r"\bon\s+[&%]\s+pieces\b", "on x pieces", t, flags=re.I)
    t = re.sub(r"\ssews on\s+[&%]\s+", " sews on x ", t, flags=re.I)
    # Truncated article at line wrap
    t = re.sub(r"\bassociated with th\s+estimate\b", "associated with the estimate", t, flags=re.I)
    t = re.sub(r"\bwith th\s+estimate\b", "with the estimate", t, flags=re.I)
    # Geometry line-label OCR confusions (vector-drawn j/k/ℓ/r)
    t = re.sub(r"\bline\s+[¢c]\s+intersects\s+lines\s+7\s+and\s+k\b", "line ℓ intersects lines j and k", t, flags=re.I)
    t = re.sub(r"\blines\s+7\s+and\s+[&%]\s+are parallel\b", "lines j and k are parallel", t, flags=re.I)
    t = re.sub(r"\blines\s+7\s+and\s+k\b", "lines j and k", t, flags=re.I)
    t = re.sub(r"\blines\s+7\s+and\s+s\b", "lines r and s", t, flags=re.I)
    t = re.sub(r"\bline\s+[¢c]\s+intersects\s+lines\s+r\s+and\s+s\b", "line ℓ intersects lines r and s", t, flags=re.I)
    # System-of-equations stems: vector m/b often OCR as ™ / 6
    if re.search(r"(?i)\bvalue of b\b", t):
        t = re.sub(r"[™]\s+and\s+6\b", "m and b", t)
        t = re.sub(r"\bmand\s+6\b", "m and b", t, flags=re.I)
    t = re.sub(r"\(—\s*5\s*,\s*y\)", "(-5, y)", t)
    # Scatterplot / variable OCR: "seeds planted, 2," → x
    t = re.sub(
        r"(?i)seeds planted,\s*2\s*,\s*and the number of seeds that germinated,\s*y\b",
        "seeds planted, x, and the number of seeds that germinated, y",
        t,
    )
    t = re.sub(r"(?i)\balen\s+chnayin\b", "also shown.", t)
    t = re.sub(r"(?i)\balso\s+chnown\b", "also shown.", t)
    t = re.sub(r"(?i)possible value of\s*[«‹<]\s*\?", "possible value of x?", t)
    t = re.sub(r"(?i)possible value of\s*[«‹]\b", "possible value of x", t)
    # Cone volume: nπ often OCR'd as na / value of n as 7
    t = re.sub(r"(?i)volume of this cone is\s*na\s*cm[\"”³3]?", "volume of this cone is nπ cm³", t)
    t = re.sub(r"(?i)volume of this cone is\s*n[a*]\s*cm[\"”³3]?", "volume of this cone is nπ cm³", t)
    t = re.sub(r"(?i)What is\s+the value of\s*7\s*\?", "What is the value of n?", t)
    t = re.sub(r"(?i)the value of\s*7\s*\?", "the value of n?", t)
    t = re.sub(r"(?i)possible value of\s*a\s*\?\s*$", "possible value of x?", t)
    # Plant growth: k OCR'd as &
    t = re.sub(r"(?i)every\s+[&%]\s+years\b", "every k years", t)
    # Participant function graphs
    t = re.sub(r"(?i)functions\s+f\s+and\s+g\b", "functions f and g", t)
    t = re.sub(r"(?i)y\s*=\s*f\s*\(\s*[zx]\s*\)", "y = f(x)", t)
    t = re.sub(r"(?i)y\s*=\s*g\s*\(\s*[ax]\s*\)", "y = g(x)", t)
    t = re.sub(r"(?i)\bandy\s*=", "and y =", t)
    t = re.sub(r"(?i)years since e\s*2010\.?", "years since 2010", t)
    t = re.sub(r"(?i)programs\s+x\s+years since", "programs x years since", t)
    # Cross x-axis constants
    t = re.sub(r"(?i)where\s*,\s*,\s*and are positive", "where a, b, and c are positive", t)
    t = re.sub(r"(?i)where\s+a,\s*b,\s*and\s*[¢c]\s+are positive", "where a, b, and c are positive", t)
    t = re.sub(r"(?i)such that\s+a\s*>\s*7\s+and\s+b\s*>\s*\?*c*", "such that a > 7 and b > c", t)
    t = re.sub(r"(?i)such that\s+a\s*>\s*7\s+and\s+b\s*>\s*c{2,}", "such that a > 7 and b > c", t)
    t = re.sub(r"(?i)\bb\s*>\s*ccc\b", "b > c", t)
    t = re.sub(r"(?i)such that\s+and\s*\?", "such that a > 7 and b > c?", t)
    t = re.sub(r"(?i)equipment\s+years after", "equipment x years after", t)
    # Similar-triangle area stems
    t = re.sub(r"(?i)\bALM\s*R\s*is\b", "△LMR is", t)
    t = re.sub(r"(?i)\barea of\s*APQR\b", "area of △PQR", t)
    t = re.sub(r"(?i)\barea of\s*A\s+PQR\b", "area of △PQR", t)
    t = re.sub(r"(?i)\bLQ intersects\s*M\s*P\b", "LQ intersects MP", t)
    t = re.sub(r"(?i)\bLM is parallel to\s*PQ\b", "LM is parallel to PQ", t)
    # Similarity / geometry label OCR (F'G → FG, Roman numerals as l/I)
    # Curly / straight / prime apostrophes all appear in PDF OCR
    apo = r"['’′‘`]"
    t = re.sub(rf"\bF{apo}+G\b", "FG", t)
    t = re.sub(rf"\bF{apo}+H\b", "FH", t)
    t = re.sub(rf"\bangle\s+F{apo}+\b", "angle F", t)
    t = re.sub(rf"\bangle\s+C{apo}+(?!\s*AD)\b", "angle C", t)
    t = re.sub(rf"\bangle\s+C{apo}*AD\b", "angle CAD", t)
    t = re.sub(r"(?i)\bangle\s+C\s*AW\b", "angle CAD", t)
    t = re.sub(r"\btriangle\s+FG\s+H\b", "triangle FGH", t)
    t = re.sub(r"\?\s*[|.]\s*", "?\n", t)
    t = re.sub(r"(?m)^\s*[|.]\s*", "I. ", t)
    t = re.sub(r"(?m)^\s*Ill\.\s*", "III. ", t)
    t = re.sub(r"(?m)^\s*ll\.\s*", "II. ", t)
    t = re.sub(r"(?m)^\s*I\.\s*", "I. ", t)
    # Algebra OCR repairs
    t = re.sub(r"(?i)If of CA JEIWEE f9r7\s*\+?\s*4\s*=\s*67,+", "If 9x + 4 = 67,", t)
    t = re.sub(r"(?i)If\s+9x\s*\+\s*4\s*=\s*67,+\s*what is the value of 902\s*\+\s*40", "If 9x + 4 = 67, what is the value of 90x + 40", t)
    t = re.sub(r"(?i)value of 902\s*\+\s*40", "value of 90x + 40", t)
    t = re.sub(r",{2,}", ",", t)
    # Circle equation OCR mangling
    t = re.sub(
        r"\([~xwe2]\s*[—\-–]\s*4\)[\"”°²2]+\s*\+\s*\(y\s*[—\-–]\s*5\)[\"”°²2]+\s*=\s*9",
        "(x - 4)² + (y - 5)² = 9",
        t,
    )
    t = re.sub(
        r"\(x\s*[—\-–]\s*3\)[²2\"”]+\s*\+\s*\(y\s*\+\s*16\)[²2\"”]+\s*=\s*(?:16\)[²2\"”]+\s*=\s*)?289",
        "(x - 3)² + (y + 16)² = 289",
        t,
    )
    t = re.sub(r"\(q,\s*[\$S]\)", "(q, y)", t)
    # Prefer a single text circle equation over a truncated {{eq}} crop
    if "{{eq:" in t and re.search(r"\(x\s*-\s*\d+\)²\s*\+\s*\(y", t):
        t = re.sub(r"\{\{eq:\d+\}\}", "", t)
        t = re.sub(r"\s{2,}", " ", t)
    # Partial fractions / constants
    t = re.sub(r"(?i)where\s+and\s+are constants", "where p and w are constants", t)
    t = re.sub(r"(?i)What is the value of\s*\?\s*$", "What is the value of w?", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    # Soften awkward spaces before punctuation from PDF extraction
    t = re.sub(r"\s+([,.;:?])", r"\1", t)
    return t


def prompt_looks_broken(prompt: str) -> bool:
    p = prompt or ""
    if not p.strip():
        return True
    if re.search(r"\b(angle|length of|measure of)\s+(is\s+)?\.", p, re.I):
        return True
    if re.search(r"\bof\s+is\s+units\b", p, re.I):
        return True
    if re.search(r"\bf\s+[A-Z]{1,3}\s+i\b", p):
        return True
    # Missing vector-drawn values mid-prose
    if re.search(
        r"(?i)\b(velocity|speed|rate)\s+of\s+(centimeters|millimeters|meters|inches|feet)\b",
        p,
    ):
        return True
    if re.search(
        r"(?i)\bof\s+(centimeters|millimeters|meters|inches|feet)\b",
        p,
    ) and not re.search(
        r"(?i)\d\s*(centimeters|millimeters|meters|inches|feet)\b",
        p,
    ):
        return True
    if re.search(r"(?i)\bwas\s+(millimeters|inches|meters|centimeters)\b", p):
        return True
    if re.search(r"(?i)\bbetween\s+and\b", p):
        return True
    if re.search(r"(?i)\bbetween\s+[A-Z=]{3,}", p):
        return True
    if re.search(r"(?i)\beither\s+.+\s+or\s+participants\b", p) and digit_count(p) < 3:
        return True
    if re.search(r"(?i)\bmargin of error is (between|greater than|less than)\s+(and\s+)?\.", p):
        return True
    if re.search(r"(?i)equations,\s+and\s+are\s+negative", p):
        return True
    if re.search(r"(?i)\bvalue of\s*\?", p):
        return True
    if re.search(r"(?i)\bwhere\s*\.", p):
        return True
    if re.search(r"(?i)\bincrease by\s+seeds\b", p):
        return True
    if re.search(r"(?i)\bSeatin\.|wort tt|P _ Ww|na cm|value of 7\b", p):
        return True
    if re.search(r"(?i)\barea of is square\b", p):
        return True
    if re.search(r"(?i)\band units, respectively\b", p) and not re.search(r"\d+\s+and\s+\d+", p):
        return True
    if re.search(r"(?i)where\s*,\s*,\s*and are", p):
        return True
    if re.search(r"(?i)every\s+[&%]\s+years\b", p):
        return True
    if re.search(r"(?i)^y\s*=\s*\d\s*$", p, re.M) and re.search(r"(?i)equipment", p):
        return True
    if re.search(r"(?i)functions\s+and\s+model\b", p):
        return True
    if re.search(r"(?i)bar graph shows[\s\S]*Data value\s*$", p) and not re.search(r"(?i)What is the frequency", p):
        return True
    if re.search(r"(?i)JEIWEE|f9r7|of CA ", p):
        return True
    if re.search(r"(?i)^In the figure,\s*$", p.strip()):
        return True
    if re.search(r"\(~|\)[\"”]", p) and re.search(r"(?i)circle", p):
        return True
    if re.search(r"[™¢£§�«]", p) or re.search(r"(?i)\bVOTTINVN\b", p):
        return True
    # equation placeholders left for money-sized gaps look broken in UI
    if re.search(r"is\s+\{\{eq:\d+\}\}", p):
        return True
    if re.search(r"where\s+\{\{eq:\d+\}\}", p):
        return True
    bare = re.sub(r"\{\{eq:\d+\}\}", "", p)
    if p.count("{{eq:") >= 2 and sum(ch.isdigit() for ch in bare) < 2 and len(bare) < 80:
        return True
    return False


def is_prose_line(text: str) -> bool:
    t = clean_text(text or "")
    if not t:
        return False
    words = t.split()
    if re.match(
        r"^(Percent|Percentage|Percentages|Year of|Respondents|Table|Figure|Location|"
        r"Study population|Number of|Adapted from|The following text)",
        t,
        re.I,
    ):
        return False
    # Table body rows (instrument / observatory / year) are not passage prose.
    if looks_like_table_data_row(t):
        return False
    if "..." in t and len(words) < 18:
        return False
    if not re.match(r'^[A-Z“\"\[\()]', t):
        return False
    if len(words) >= 12 and len(t) >= 70:
        return True
    if len(words) >= 10 and len(t) >= 55 and re.search(
        r"\b(the|a|an|of|in|to|and|that|which|who|from|with|for|are|is|was|were)\b",
        t,
        re.I,
    ):
        return True
    return False


def looks_like_table_data_row(text: str) -> bool:
    t = clean_text(text or "")
    if not t or re.search(r"[.!?]", t):
        return False
    has_year = bool(re.search(r"\b(?:19|20)\d{2}\b", t))
    if has_year and re.search(
        r"\b(?:observatory|spectroscopy|infrared imaging|data type|instrument|"
        r"telescope|spectrometer|camera)\b",
        t,
        re.I,
    ):
        return True
    # Dense row ending in year(s), typical of SAT data tables.
    if has_year and re.search(r"\b(?:19|20)\d{2}(?:,\s*(?:19|20)\d{2})?\s*$", t) and len(t.split()) >= 5:
        return True
    return False


def find_stem_y(page: fitz.Page) -> float:
    for needle in (
        "Which choice",
        "Which finding",
        "Which quotation",
        "Which statement",
        "Based on the",
        "According to the",
        "As used in",
        "The writer",
        "The student",
        "What is the",
        "How does",
        "Why does",
    ):
        hits = page.search_for(needle)
        if hits:
            return hits[0].y0
    return find_y(page, "Answer") or (page.rect.height * 0.58)


def find_passage_start_y(page: fitz.Page, y0: float, y1: float) -> float | None:
    lines: dict[int, list] = defaultdict(list)
    for w in page.get_text("words"):
        if y0 <= w[1] <= y1 and w[4].strip():
            lines[line_key(w[1])].append(w)
    for key in sorted(lines):
        ws = sorted(lines[key], key=lambda w: w[0])
        text = " ".join(w[4] for w in ws)
        if is_prose_line(text):
            return min(w[1] for w in ws)
    return None


def words_in_band(page: fitz.Page, y0: float, y1: float) -> list:
    return [
        w for w in page.get_text("words")
        if y0 <= w[1] < y1 and w[4].strip() and w[4] not in {"Question", "Answer"}
    ]


def join_words(words: list) -> str:
    if not words:
        return ""
    words = sorted(words, key=lambda w: (line_key(w[1]), w[0]))
    lines: dict[int, list[str]] = defaultdict(list)
    for w in words:
        lines[line_key(w[1])].append(w[4])
    return clean_text("\n".join(" ".join(lines[k]) for k in sorted(lines)))


def extract_source(passage: str) -> tuple[str, str]:
    text = passage or ""
    m = re.match(
        r"^((?:The following text is adapted from|Text \d+ is adapted from|Adapted from)[^\n]+(?:\n(?![A-Z]).+)*)",
        text,
        re.I,
    )
    if not m:
        return "", text
    source = clean_text(m.group(1))
    rest = text[m.end():].lstrip("\n")
    return source, rest


def render_figure_clip(page: fitz.Page, out_path: Path, clip: fitz.Rect, scale: float = 3.2) -> str:
    """Render a figure with light trimming so axis lines are not shaved off."""
    pix = safe_pixmap(page, clip, scale=scale)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    gray = ImageOps.grayscale(img)
    # Keep light gray chart fills; only trim near-white margins
    mask = gray.point(lambda p: 0 if p < 250 else 255)
    bbox = ImageOps.invert(mask).getbbox()
    if bbox:
        pad = 16
        bbox = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(img.width, bbox[2] + pad),
            min(img.height, bbox[3] + pad),
        )
        img = img.crop(bbox)
    if img.width < 8 or img.height < 8:
        return ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=95, optimize=True)
    return str(out_path.relative_to(ROOT / "public")).replace("\\", "/")


def crop_reading_figure(page: fitz.Page, out_path: Path, text: str) -> tuple[str | None, fitz.Rect | None, float | None]:
    """
    Crop a full chart/table including title, axes, and legend.
    Returns (public_path, clip_rect, passage_start_y).
    """
    q_rect = find_label_rect(page, "Question")
    if q_rect is None:
        return None, None, None
    qy = q_rect.y1 + 1
    stem_y = find_stem_y(page)
    has_kw = bool(re.search(r"\b(graph|table|figure|chart|scatterplot|diagram)\b", text, re.I))

    draws = drawing_rects(page, qy, stem_y, include_hairlines=True)
    solid = [r for r in draws if r.width >= 2 and r.height >= 2]
    if not solid and not has_kw:
        return None, None, None

    draw_union = None
    for r in draws:
        draw_union = r if draw_union is None else (draw_union | r)

    search_from = (draw_union.y1 + 1) if draw_union is not None else qy
    passage_y = find_passage_start_y(page, search_from, stem_y)
    if passage_y is None and draw_union is not None:
        passage_y = min(stem_y - 4, draw_union.y1 + 6)
    if passage_y is None:
        return None, None, None

    fig_bottom = passage_y - 1
    content_draws = [r for r in draws if r.y0 < fig_bottom and r.y1 > qy]
    content_words = words_in_band(page, qy, fig_bottom)

    # Require real ink for non-keyword pages
    if not has_kw:
        if not content_draws:
            return None, None, None
        area = sum(max(r.width, 1) * max(r.height, 1) for r in content_draws)
        if area < 8000:
            return None, None, None

    union = None
    for r in content_draws:
        union = r if union is None else (union | r)
    for w in content_words:
        r = fitz.Rect(w[0], w[1], w[2], w[3])
        union = r if union is None else (union | r)
    if union is None:
        return None, None, None

    # Charts often have right-edge gridlines that need extra pad
    clip = fitz.Rect(
        max(page.rect.x0 + 10, union.x0 - 14),
        max(page.rect.y0 + 8, union.y0 - 10),
        min(page.rect.x1 - 10, union.x1 + 24),
        min(page.rect.y1 - 8, union.y1 + 14),
    )
    if clip.height < 70 or clip.width < 100:
        return None, None, None

    rel = render_figure_clip(page, out_path, clip, scale=3.6)
    if not rel:
        return None, None, None
    return f"/{rel}", clip, passage_y


def crop_figure(page: fitz.Page, out_path: Path, text: str) -> str | None:
    """Legacy math figure crop — prefer crop_math_figure for diagrams."""
    path, _ = crop_math_figure(page, out_path, text)
    return path


def line_key(y: float) -> int:
    return int(round(y / 9.0))


def build_math_prompt(page: fitz.Page, text: str, figure_rect: fitz.Rect | None = None, qid: str = "q"):
    """Assemble stem text with {{eq:n}} placeholders for equation crops when needed."""
    q_rect = find_label_rect(page, "Question")
    a_rect = find_label_rect(page, "Answer")
    if q_rect is None:
        return clean_text(extract_question_body(text)), []

    y0 = q_rect.y1 + 1
    y1 = (a_rect.y0 - 2) if a_rect is not None else page.rect.height * 0.55

    words = [
        w for w in page.get_text("words")
        if y0 <= w[1] <= y1 and w[4].strip() and w[4] not in {"Question", "Answer"}
    ]
    # Drop words that sit inside a figure crop (axis labels, tick numbers, etc.)
    if figure_rect is not None:
        words = [
            w for w in words
            if not (
                w[0] >= figure_rect.x0 - 2
                and w[1] >= figure_rect.y0 - 2
                and w[2] <= figure_rect.x1 + 2
                and w[3] <= figure_rect.y1 + 2
            )
        ]
    words.sort(key=lambda w: (line_key(w[1]), w[0]))

    raw_draws = drawing_rects(page, y0, y1)
    if figure_rect is not None:
        raw_draws = [
            r for r in raw_draws
            if (r & figure_rect).get_area() < 0.35 * max(r.get_area(), 1)
        ]

    # Merge raw strokes first with a generous x-gap so "3(14x - 15)" stays one piece
    band_eqs = [
        r for r in merge_rects(raw_draws, x_gap=32, y_gap=14)
        if 6 <= r.height <= 56 and r.width >= 18 and r.width <= 520
    ]

    eq_dir = ROOT / "public" / "qbank" / "math" / "equations"
    eq_dir.mkdir(parents=True, exist_ok=True)
    equation_images: list[str] = []
    used_bands: set[int] = set()
    pieces: list[tuple[float, str]] = []

    def expand_eq_rect(rect: fitz.Rect) -> fitz.Rect:
        """Pull in trailing digits (e.g. '= 9') drawn outside the stroke band."""
        out = fitz.Rect(rect)
        for w in words:
            wy = (w[1] + w[3]) / 2
            if abs(wy - ((rect.y0 + rect.y1) / 2)) > 14:
                continue
            if w[0] >= rect.x1 - 4 and w[0] <= rect.x1 + 48:
                tok = (w[4] or "").strip()
                if re.fullmatch(r"[=+\-]?\d+(?:\.\d+)?", tok) or tok in {"=", "+", "−", "-"}:
                    out.x1 = max(out.x1, w[2] + 2)
                    out.y0 = min(out.y0, w[1] - 2)
                    out.y1 = max(out.y1, w[3] + 2)
        return out

    def add_eq_image(rect: fitz.Rect) -> str:
        idx = len(equation_images)
        rect = expand_eq_rect(rect)
        rel = render_clip(
            page,
            eq_dir / f"{qid}_{idx}.jpg",
            fitz.Rect(rect.x0 - 3, rect.y0 - 3, rect.x1 + 6, rect.y1 + 3),
            scale=3.6,
        )
        if not rel:
            return ""
        equation_images.append(f"/{rel}")
        return f"{{{{eq:{idx}}}}}"

    def resolve_eq(rect: fitz.Rect, prefer_image: bool = False) -> str:
        rect = expand_eq_rect(rect)
        snip = ocr_equation_region(page, rect)
        snip = snip.replace("14z", "14x").replace("g(a)", "g(x)")
        snip = polish_ocr_stem(snip) if snip else snip

        # Always prefer plain text for money / inequalities / short numbers
        simple = extract_simple_math_token(snip)
        if simple:
            return simple

        # Clean circle equations as text rather than truncated crops
        if re.search(r"\(x\s*-\s*\d+\)²\s*\+\s*\(y", snip or ""):
            return snip
        if re.search(r"(?i)circle.*(equation|graph)", " ".join(w[4] for w in words[:40])):
            polished = polish_ocr_stem(snip or "")
            if re.search(r"\(x\s*-\s*\d+\)²", polished):
                return polished

        # Common short inline forms that OCR mangles
        if re.search(r"(?i)y\s*=\s*g.*x.*-\s*2", snip) or re.search(r"(?i)g\s*\(\s*x\s*\)\s*-\s*2", snip):
            if "14" not in snip:
                return "y = g(x) - 2"
        if prefer_image:
            return add_eq_image(rect)
        if math_ocr_ok(snip) and not re.search(r"\b(Assessment|Difficulty|SAT|Domain|Skill)\b", snip):
            # Keep function definitions as images only when OCR is clearly garbled
            if re.search(r"(?i)\b[a-z]{3,}\s*=", snip) and not re.search(r"(?i)\b[fgh]\s*\(", snip):
                return add_eq_image(rect)
            return snip
        return add_eq_image(rect)

    for i, r in enumerate(band_eqs):
        same = [w for w in words if abs(((w[1] + w[3]) / 2) - ((r.y0 + r.y1) / 2)) < 12]
        if len(same) <= 1:
            token = resolve_eq(r, prefer_image=False)
            if token:
                pieces.append((r.y0, token))
            used_bands.add(i)

    lines: dict[int, list] = defaultdict(list)
    for w in words:
        lines[line_key((w[1] + w[3]) / 2)].append(w)

    for lk in sorted(lines):
        row = sorted(lines[lk], key=lambda w: w[0])
        y_mid = sum((w[1] + w[3]) / 2 for w in row) / len(row)
        chunks: list[str] = []
        cursor_x = None
        for w in row:
            x0, _, x1, _, token, *_ = w
            if cursor_x is not None and x0 - cursor_x > 18:
                gap = fitz.Rect(cursor_x + 0.5, y_mid - 16, x0 - 0.5, y_mid + 16)
                for i, r in enumerate(band_eqs):
                    if i in used_bands:
                        continue
                    if (r & gap).get_area() > 0 or (
                        abs(((r.y0 + r.y1) / 2) - y_mid) < 12
                        and r.x0 >= cursor_x - 8
                        and r.x1 <= x0 + 8
                    ):
                        clipped = fitz.Rect(
                            max(r.x0, cursor_x + 2.5),
                            r.y0 - 2,
                            min(r.x1, x0 - 2.5),
                            r.y1 + 2,
                        )
                        if clipped.width >= 8:
                            eq_tok = resolve_eq(clipped, prefer_image=False)
                            if eq_tok:
                                chunks.append(eq_tok)
                        used_bands.add(i)
                        break
            chunks.append(token)
            cursor_x = x1
        line_text = clean_text(" ".join(chunks))
        line_text = re.sub(r"\{\{\s*eq\s*:\s*(\d+)\s*\}\}", r"{{eq:\1}}", line_text)
        if line_text:
            pieces.append((y_mid, line_text))

    pieces.sort(key=lambda t: t[0])
    out_lines: list[str] = []
    for _, s in pieces:
        if out_lines and out_lines[-1] == s:
            continue
        if re.search(r"\b(Assessment|Difficulty|Question ID)\b", s):
            continue
        out_lines.append(s)

    prompt = "\n".join(out_lines).strip()
    if len(prompt) < 12:
        prompt = clean_text(extract_question_body(text))
    return prompt, equation_images


def strip_chart_noise(prompt: str) -> str:
    """Remove axis labels / tick numbers / vertex crumbs that leaked into the stem."""
    lines = (prompt or "").split("\n")

    def bare(ln: str) -> str:
        return re.sub(r"\{\{eq:\d+\}\}", "", ln).strip()

    def is_prose(ln: str) -> bool:
        raw = bare(ln)
        if len(raw) < 35:
            return False
        return sum(ch.isalpha() for ch in raw) >= 22

    def is_noise(ln: str) -> bool:
        raw = bare(ln)
        low = raw.lower()
        if not raw:
            return "{{eq:" not in ln
        if low in {
            "number of", "participants", "(in thousands)", "years since 2010",
            "x", "y", "o", "miles", "minutes", "dollars",
        }:
            return True
        if re.fullmatch(r"[A-Z\s]+", raw) and len(raw) <= 12:
            return True  # vertex label crumbs like "M R L Q P"
        if re.match(r"(?i)^(seatin|proportion|capacity|less than|greater than)\b", raw):
            return True
        if re.search(r"(?i)wort tt|BETTE|HUTTE|KELE|TET TT", raw):
            return True
        if re.fullmatch(r"[\d.\s%]+", raw):
            return True
        if re.fullmatch(r"(?:[OoXxYy]\s*)+", raw):
            return True
        if len(raw) <= 3 and not raw.isalpha():
            return True
        # mostly non-letters chart OCR garbage
        if len(raw) >= 8 and sum(ch.isalpha() for ch in raw) < max(3, len(raw) * 0.35):
            if not re.search(r"\{\{eq:", ln):
                return True
        return False

    # Drop leading noise until first prose (or equation) line
    first_keep = next(
        (i for i, ln in enumerate(lines) if is_prose(ln) or "{{eq:" in ln),
        None,
    )
    if first_keep is None:
        return prompt

    kept = []
    for i, ln in enumerate(lines):
        if i < first_keep:
            continue
        if is_noise(ln):
            continue
        kept.append(ln)
    cleaned = "\n".join(kept).strip()
    # Drop leftover table scraps between intro and ask
    cleaned = re.sub(
        r"(?i)(?:\n?(?:Seatin\.?|1g Proportion|Proportion|capacity|Less than\b.*?|Greater than\b.*?|seats\b|seats\s*°)\s*)+(?=\nIf a room|\nWhich of|\Z)",
        "\n",
        cleaned,
    )
    cleaned = re.sub(r"(?i)\n?1g Proportion\n?", "\n", cleaned)
    cleaned = re.sub(r"(?i)\n?seats\s*°?\n?", "\n", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    return cleaned.strip() or prompt


def choice_text_has_holes(text: str | None) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if re.fullmatch(r"[A-D]", t, re.I):
        return True
    if t in {"=", "--", "-", "–", "—"}:
        return True
    if re.search(r"(?i)\bbetween\s+and\b", t):
        return True
    if re.search(r"(?i)\b(greater|less)\s+than\s*\.?\s*$", t):
        return True
    if re.search(r"(?i)^(what is this|which of the following)", t):
        return True
    # mangled percent ranges from OCR
    if re.search(r"(?i)margin of error is between", t) and "%" not in t:
        return True
    if re.search(r"(?i)between\s+[a-z]\s+and\b", t):
        return True
    if re.search(r"(?i)\bincrease by\s+seeds\b", t):
        return True
    if re.search(r"(?i)\bevery\s+days\b", t) and digit_count(t) == 0:
        return True
    # Pythagorean / exponent garbage
    if re.search(r"(?i)12-3=c|er e=|=<\?|127-3", t):
        return True
    if re.fullmatch(r"[a-z\s=]+", t) and "=" in t and digit_count(t) == 0:
        return True
    # Mangled circle / squared OCR
    if re.search(r"[\"”°]", t) and "=" in t and len(t) <= 56:
        return True
    if re.search(r"(?i)^\([ew2~]", t) and "=" in t:
        return True
    return False


def find_answer_choice_hits(page: fitz.Page) -> list:
    """Locate A.–D. markers in the Answer block only (ignore stem false positives)."""
    labels = ["A.", "B.", "C.", "D."]
    a_rect = find_label_rect(page, "Answer")
    y_min = (a_rect.y0 - 2) if a_rect is not None else 0
    hits = []
    for lab in labels:
        found = [h for h in page.search_for(lab) if h.y0 >= y_min]
        found.sort(key=lambda r: (r.y0, r.x0))
        hits.append(found[0] if found else None)
    return hits


def choice_image_needed(text: str | None) -> bool:
    if not text:
        return True
    if re.fullmatch(r"(?i)zero|one|two|three|four|five|six|seven|eight|nine|ten", (text or "").strip()):
        return False
    # Plain integers / decimals are fine as text
    if re.fullmatch(r"-?\d+(?:\.\d+)?", (text or "").strip()):
        return False
    if choice_text_has_holes(text):
        return True
    letters = sum(ch.isalpha() for ch in text)
    if len(text) <= 28 and letters < 4:
        return True
    # radical / stacked / squared expressions OCR usually mangles
    if re.search(r"(?i)(√|sqrt|\bae\b|\bvi\b|V\s*\d|\d\^\d|\d²)", text):
        return True
    # Circle equations / long symbolic choices
    if re.search(r"(?i)\([xy].*=|\(x\s*[-—]", text) and ("²" in text or '"' in text or "”" in text):
        return True
    if re.search(r"(?i)\d\s*[-+]\s*\d\s*=\s*[a-z]\b", text) and "²" not in text:
        # likely missing squares: 12-3=c
        return True
    # Bare fractions often come from stacked typesetting — prefer image
    if re.fullmatch(r"-?\d+/\d+", (text or "").strip()):
        return True
    return False


def choice_row_has_minus(page: fitz.Page, clip: fitz.Rect) -> bool:
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"])
        if r.y1 < clip.y0 or r.y0 > clip.y1:
            continue
        if r.x1 < clip.x0 or r.x0 > clip.x1:
            continue
        # short horizontal stroke typical of a minus sign
        if r.width >= 3.5 and r.height <= 3.2 and r.width > r.height * 1.8:
            return True
    return False


def ocr_numeric_choice(page: fitz.Page, clip: fitz.Rect) -> str:
    pix = safe_pixmap(page, clip, scale=8.0)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img)
    raw = pytesseract.image_to_string(
        img,
        config="--oem 3 --psm 7 -c tessedit_char_whitelist=-0123456789./,",
    ).strip()
    raw = raw.replace("—", "-").replace("–", "-").replace("−", "-")
    raw = re.sub(r"[^0-9./,-]", "", raw)
    if raw and not raw.startswith("-") and choice_row_has_minus(page, clip):
        raw = "-" + raw
    if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?", raw):
        return raw
    if re.fullmatch(r"-?\d+(\.\d+)?", raw):
        return raw
    if re.fullmatch(r"-?\d+/\d+", raw):
        return raw
    return ""


def clean_choice_expression(s: str) -> str:
    s = (s or "").replace("—", "-").replace("–", "-").replace("−", "-")
    s = s.replace("◦", "°").replace("º", "°")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^\[?\s*[A-D][.)]\s*", "", s, flags=re.I)
    # Common OCR confusions for leading digits
    s = re.sub(r"\bA94\b", "494", s)
    s = re.sub(r"\bA494\b", "494", s)
    s = re.sub(r"\bAQA\b", "494", s)
    s = re.sub(r"\bAOA\b", "494", s)
    s = re.sub(r"\bA4\b", "44", s)
    s = re.sub(r"\bsin\s*", "sin ", s, flags=re.I)
    s = re.sub(r"\bcos\s*", "cos ", s, flags=re.I)
    s = re.sub(r"\btan\s*", "tan ", s, flags=re.I)
    s = re.sub(r"\s+°", "°", s)
    s = re.sub(r"(\d)\s*°", r"\1°", s)
    return s.strip(" .")


def ocr_choice_expression(page: fitz.Page, clip: fitz.Rect) -> str:
    """OCR choices that may include trig/units/functions, not only pure numbers."""
    pix = safe_pixmap(page, clip, scale=5.0)
    if pix is None:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    img = ImageOps.autocontrast(img)
    raw = pytesseract.image_to_string(img, config="--oem 3 --psm 7").strip()
    raw = clean_choice_expression(raw)
    if not raw:
        return ""
    # Label bleed / empty
    if re.fullmatch(r"[A-D]", raw, re.I):
        return ""
    # Accept pure numbers (with optional thousands commas)
    if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?", raw) or re.fullmatch(r"-?\d+(\.\d+)?", raw) or re.fullmatch(r"-?\d+/\d+", raw):
        return raw
    # Reject mangled radical OCR — use choice images instead
    if re.search(r"(?i)\b(ae|vi|op)\b", raw) or re.search(r"(?i)\dV\s*\d|V\s*\d", raw):
        return ""
    # Accept trig / degree expressions like 247 sin 54°
    if re.fullmatch(r"-?\d+(\.\d+)?\s*(sin|cos|tan)\s*\d+(\.\d+)?°", raw, re.I):
        return re.sub(r"\s+", " ", raw)
    if re.search(r"(?i)\b(sin|cos|tan)\b", raw) and re.search(r"\d", raw):
        if re.match(r"^[A-Za-z]", raw):
            return ""
        return raw
    # Function / algebra choices: f(x) = 25.40(x - 2) + 12.70
    fn = re.sub(r"\s+", " ", raw)
    fn = re.sub(r"\b([fgh])\s*\(\s*([ax])\s*\)", lambda m: f"{m.group(1)}(x)", fn, flags=re.I)
    fn = re.sub(r"\(([ax])\s*-", "(x -", fn, flags=re.I)
    fn = re.sub(r"\(([ax])\s*\+", "(x +", fn, flags=re.I)
    fn = fn.replace(" |", "").replace("| ", "").strip(" |")
    if "@" in fn or ":" in fn or fn.count("(") != fn.count(")"):
        return ""
    if re.search(r"(?i)\b[fgh]\(x\)\s*=", fn) and re.search(r"\d", fn) and len(fn) <= 72:
        rhs = fn.split("=", 1)[-1]
        # Require a variable on the RHS — reject OCR that turned x into 2, etc.
        if re.search(r"(?i)\bx\b", rhs):
            return fn
        return ""
    # y = 64x style — reject when OCR ate the variable into a digit (y = 642)
    if re.match(r"(?i)^y\s*=", fn):
        if re.search(r"(?i)\b[a-z]\b", fn.split("=", 1)[-1]):
            return fn
        return ""
    # x + z = 46 often OCR'd as xz = 46
    m = re.fullmatch(r"(?i)([a-z])([a-z])\s*=\s*(\d+(?:\.\d+)?)", fn)
    if m and m.group(1) != m.group(2):
        return f"{m.group(1)} + {m.group(2)} = {m.group(3)}"
    # Short algebraic snippets
    if len(raw) <= 40 and re.search(r"[0-9=+\-/(x)]", raw) and sum(ch.isalpha() for ch in raw) <= 14:
        if "@" in raw or "|" in raw:
            return ""
        if re.search(r"(?i)\b(ae|vi|op)\b", raw):
            return ""
        return raw
    # Prose choices with recovered percents / numbers
    if len(fn) <= 90 and re.search(r"(?i)margin of error", fn) and digit_count(fn) >= 1:
        if choice_text_has_holes(fn):
            return ""
        return fn
    return ""


def extract_choice_objects(page: fitz.Page, qid: str, pdf_choices: list[str] | None) -> list[dict]:
    labels = ["A.", "B.", "C.", "D."]
    hits = find_answer_choice_hits(page)
    end = page.rect.height
    ca = page.search_for("Correct Answer") or page.search_for("Rationale")
    if ca:
        end = min(end, ca[0].y0)

    objs: list[dict] = []
    for i, lab in enumerate(labels):
        pdf_text = clean_text((pdf_choices[i] if pdf_choices and i < len(pdf_choices) else "") or "")
        hit = hits[i]
        if hit is None:
            objs.append(
                {"text": pdf_text}
                if pdf_text and not choice_text_has_holes(pdf_text)
                else {"text": lab[0]}
            )
            continue

        # Next choice below this one (ignore markers that OCR-matched above)
        y1 = end
        for j in range(i + 1, 4):
            if hits[j] is not None and hits[j].y0 > hit.y0 + 2:
                y1 = hits[j].y0
                break
        if y1 <= hit.y0 + 8:
            y1 = hit.y0 + 40

        if pdf_text and not choice_image_needed(pdf_text):
            objs.append({"text": pdf_text})
            continue

        wide = choice_text_has_holes(pdf_text) or (len(pdf_text) > 36)
        # Keep row height tight so the next choice doesn't ghost into the crop
        gap = y1 - hit.y0
        row_h = 44 if wide else 30
        if gap > 8:
            row_h = min(row_h, max(18, gap - 4))
        # Fraction / stacked choices: stay within this row only
        if re.search(r"(?i)sufficient|margin of error", pdf_text or ""):
            row_h = min(row_h, max(22, gap - 2))
        elif not pdf_text or choice_text_has_holes(pdf_text) or len(pdf_text) <= 28:
            row_h = min(row_h, max(18, gap - 5))
        # Tight vertical budget when choices are densely stacked
        if gap < 36:
            row_h = min(row_h, max(16, gap - 6))
        num_clip = fitz.Rect(
            hit.x1 + 1,
            hit.y0 - 2,
            min(page.rect.x1 - 24, hit.x1 + (520 if wide else 300)),
            hit.y0 + row_h,
        )
        if num_clip.y1 > y1 - 1:
            num_clip.y1 = y1 - 1
        if num_clip.y1 <= num_clip.y0 + 6:
            num_clip.y1 = num_clip.y0 + 28

        # Stacked fraction bars → always image (OCR often reads only one digit line)
        has_frac_bar = False
        for d in page.get_drawings():
            r = fitz.Rect(d["rect"])
            if (r & num_clip).get_area() <= 0:
                continue
            if r.width >= 8 and r.height <= 2.8 and r.width > r.height * 3:
                has_frac_bar = True
                break
        if has_frac_bar:
            # Shrink bottom further for fraction rows to avoid ghosting next numerator
            frac_clip = fitz.Rect(num_clip)
            if gap > 8:
                frac_clip.y1 = min(frac_clip.y1, hit.y0 + min(row_h, gap - 5))
            rel = render_clip(
                page,
                MATH_CHOICE_IMG / f"{qid}_{i}.jpg",
                frac_clip,
                scale=3.8,
            )
            if rel:
                objs.append({"image": f"/{rel}"})
                continue

        expr = ocr_choice_expression(page, num_clip)
        if expr and not choice_text_has_holes(expr) and not choice_image_needed(expr):
            objs.append({"text": expr})
            continue

        peek = ocr_region_text(page, num_clip, scale=4.5, psm=7)
        symbolic = bool(
            re.search(r"(?i)\b[yfgh]\s*=|=.*[x×]|\d\s*[x×]|√|sqrt|\bae\b|\bvi\b", peek or "")
        )
        if symbolic or choice_text_has_holes(pdf_text) or choice_text_has_holes(peek):
            rel = render_clip(
                page,
                MATH_CHOICE_IMG / f"{qid}_{i}.jpg",
                num_clip,
                scale=3.6,
            )
            if rel:
                objs.append({"image": f"/{rel}"})
                continue

        numeric = ocr_numeric_choice(page, num_clip)
        if numeric and not re.fullmatch(r"-?\d+/\d+", numeric):
            objs.append({"text": numeric})
            continue

        rel = render_clip(
            page,
            MATH_CHOICE_IMG / f"{qid}_{i}.jpg",
            num_clip,
            scale=3.4,
        )
        if rel:
            objs.append({"image": f"/{rel}"})
        elif pdf_text and not choice_text_has_holes(pdf_text):
            objs.append({"text": pdf_text})
        else:
            objs.append({"text": lab[0]})
    return objs


def sync_reading_pdfs_to_public() -> None:
    import shutil

    READING_PDF_PUBLIC.mkdir(parents=True, exist_ok=True)
    mapping = [
        (ENG_UNANSWERED, READING_PDF_PUBLIC / "English-Questions-Unanswered.pdf"),
        (ENG_ANSWERED, READING_PDF_PUBLIC / "English-Questions-Answered.pdf"),
    ]
    for src, dest in mapping:
        if not src.exists():
            print(f"warn: missing source PDF {src}")
            continue
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            continue
        shutil.copy2(src, dest)
        print(f"copied {src.name} -> {dest.relative_to(ROOT)}")


def extract_reading():
    answered = fitz.open(ENG_ANSWERED)
    unanswered = fitz.open(ENG_UNANSWERED) if ENG_UNANSWERED.exists() else None
    unanswered_by_id = {g["id"]: g["pages"][0] for g in group_pages(unanswered)} if unanswered else {}
    answered_by_id = {g["id"]: g["pages"][0] for g in group_pages(answered)}
    sync_reading_pdfs_to_public()
    READING_FIG.mkdir(parents=True, exist_ok=True)
    for p in READING_FIG.glob("*.jpg"):
        p.unlink()
    items = []
    for g in group_pages(answered):
        qid = g["id"]
        text = g["text"]
        domain, skill, difficulty = parse_meta(text, "Reading and Writing", RW_DOMAINS)
        body = extract_question_body(text)
        passage, prompt = split_passage_and_prompt(body)
        choices = extract_choices_text(text)
        kind, ans = correct_answer(text)
        explanation = extract_explanation(text)
        if not choices or kind != "mc" or domain is None:
            print(f"skip reading {qid}")
            continue

        page = answered[g["pages"][0]]
        figure, _clip, passage_y = crop_reading_figure(page, READING_FIG / f"{qid}.jpg", text)

        source = ""
        if figure and passage_y is not None:
            # Rebuild passage from page text below the figure so chart labels don't leak in
            stem_y = find_stem_y(page)
            passage = join_words(words_in_band(page, passage_y - 0.5, stem_y)) or passage
            # Rebuild prompt from stem downward until Answer when possible
            a_y = find_y(page, "Answer") or page.rect.height
            rebuilt_prompt = join_words(words_in_band(page, stem_y - 0.5, a_y))
            if rebuilt_prompt:
                prompt = rebuilt_prompt

        source, passage = extract_source(passage)

        item = {
            "id": qid,
            "topic": domain,
            "domain": domain,
            "skill": skill,
            "difficulty": difficulty,
            "pool": "Summer 2026 Bank",
            "passageTitle": "Passage",
            "passage": passage,
            "prompt": prompt,
            "choices": [{"text": c} for c in choices],
            "answer": ans,
            "type": "mc",
            "explanation": explanation,
        }
        if qid in unanswered_by_id:
            item["pdf"] = READING_PDF_UNANSWERED_URL
            item["pdfPage"] = unanswered_by_id[qid] + 1
        elif qid in answered_by_id:
            item["pdf"] = READING_PDF_ANSWERED_URL
            item["pdfPage"] = answered_by_id[qid] + 1
        if source:
            item["source"] = source
        if figure:
            item["figure"] = figure
        items.append(item)

    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / "readingQuestions.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} reading questions")
    fig_n = sum(1 for it in items if it.get("figure"))
    print(f"  with figures: {fig_n}")
    return items


def sync_math_pdfs_to_public() -> None:
    """Ship source PDFs under public/ so the practice UI can open original pages."""
    import shutil

    MATH_PDF_PUBLIC.mkdir(parents=True, exist_ok=True)
    mapping = [
        (MATH_UNANSWERED, MATH_PDF_PUBLIC / "Math-Questions-Unanswered.pdf"),
        (MATH_ANSWERED, MATH_PDF_PUBLIC / "Math-Questions-Answered.pdf"),
    ]
    for src, dest in mapping:
        if not src.exists():
            print(f"warn: missing source PDF {src}")
            continue
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            continue
        shutil.copy2(src, dest)
        print(f"copied {src.name} -> {dest.relative_to(ROOT)}")


def extract_math():
    answered = fitz.open(MATH_ANSWERED)
    unanswered = fitz.open(MATH_UNANSWERED)
    unanswered_by_id = {g["id"]: g["pages"][0] for g in group_pages(unanswered)}
    answered_by_id = {g["id"]: g["pages"][0] for g in group_pages(answered)}
    sync_math_pdfs_to_public()
    MATH_FIG.mkdir(parents=True, exist_ok=True)
    MATH_CHOICE_IMG.mkdir(parents=True, exist_ok=True)
    MATH_PDF_PREVIEW.mkdir(parents=True, exist_ok=True)
    for folder in (MATH_FIG, MATH_CHOICE_IMG, MATH_PDF_PREVIEW, ROOT / "public" / "qbank" / "math" / "equations"):
        folder.mkdir(parents=True, exist_ok=True)
        for p in folder.glob("*.jpg"):
            p.unlink()
    # also clear any leftover full-page screenshots
    math_root = ROOT / "public" / "qbank" / "math"
    for p in math_root.glob("*.jpg"):
        p.unlink()

    items = []
    groups = group_pages(answered)
    for n, g in enumerate(groups, 1):
        qid = g["id"]
        text = g["text"]
        domain, skill, difficulty = parse_meta(text, "Math", MATH_DOMAINS)
        kind, ans = correct_answer(text)
        explanation = extract_explanation(text)
        if domain is None or kind is None:
            print(f"skip math {qid}")
            continue

        src_idx = unanswered_by_id.get(qid, g["pages"][0])
        src_doc = unanswered if qid in unanswered_by_id else answered
        page = src_doc[src_idx]
        # Prefer unanswered for stem (no rationale clutter); answered for explanation text

        figure, figure_rect = crop_math_figure(page, MATH_FIG / f"{qid}.jpg", text)

        prompt, equation_images = build_math_prompt(page, text, figure_rect=figure_rect, qid=qid)
        built_prompt_snapshot = prompt

        # Prefer full-stem OCR as real text whenever equation crops would show
        # money / inequalities / mangled word-problem holes as tiny images.
        ocr_prompt = polish_ocr_stem(ocr_math_stem(page, figure_rect=figure_rect))
        kept_eqs = list(equation_images)
        if should_prefer_ocr_stem(prompt, ocr_prompt, bool(figure)):
            prompt = ocr_prompt
            equation_images = []
        elif prompt_looks_broken(prompt) and ocr_prompt and not ocr_looks_broken(ocr_prompt):
            prompt = ocr_prompt
            equation_images = []
        elif figure and ocr_prompt and not ocr_looks_broken(ocr_prompt):
            bare = re.sub(r"\{\{eq:\d+\}\}", "", prompt)
            if prompt_looks_broken(prompt) or len(ocr_prompt) > len(bare):
                prompt = ocr_prompt
                equation_images = []
        # Word problems that say "given system/equation" still need the equation crops
        if (
            kept_eqs
            and not equation_images
            and re.search(r"(?i)\bgiven (system|equation)", prompt or "")
            and "{{eq:" not in (prompt or "")
        ):
            equation_images = kept_eqs
            prefix_parts = [f"{{{{eq:{i}}}}}" for i in range(len(equation_images))]
            for ln in built_prompt_snapshot.split("\n"):
                polished = clean_math_snippet(ln)
                if re.fullmatch(r"(?i)y\s*=\s*mx\s*\+\s*b", polished):
                    prefix_parts.append("y = mx + b")
                elif re.match(r"(?i)^y\s*=\s*m", polished) and "y = mx + b" not in prefix_parts:
                    prefix_parts.append("y = mx + b")
            prompt = "\n".join(prefix_parts + [prompt])
        # Equipment / display equations that were truncated to "y = 7"
        if re.search(r"(?i)^y\s*=\s*\d\s*$", prompt or "", re.M) and re.search(r"(?i)equipment", prompt or ""):
            # Prefer rebuilt equation token from snapshot / OCR band
            for ln in built_prompt_snapshot.split("\n"):
                polished = clean_math_snippet(ln)
                if re.match(r"(?i)^y\s*=\s*\d{1,3},\d{3}", polished) or "^x" in polished:
                    prompt = re.sub(r"(?i)^y\s*=\s*\d\s*$", polished, prompt, count=1, flags=re.M)
                    break
            if kept_eqs and re.search(r"(?i)^y\s*=\s*\d\s*$", prompt or "", re.M):
                equation_images = kept_eqs
                prompt = re.sub(r"(?i)^y\s*=\s*\d\s*\n?", "", prompt)
                prompt = "\n".join([f"{{{{eq:{i}}}}}" for i in range(len(equation_images))] + [prompt.strip()])
        # Keep equation crops when OCR mangled an "expression {{eq}} is equivalent..." stem
        if (
            kept_eqs
            and re.search(r"(?i)expression \{\{eq:", built_prompt_snapshot or "")
            and (
                not equation_images
                or ocr_looks_broken(ocr_prompt)
                or prompt_looks_broken(prompt)
            )
        ):
            if "{{eq:" not in (prompt or "") or prompt_looks_broken(prompt):
                prompt = built_prompt_snapshot
                equation_images = kept_eqs
        # Apply text polish even on hybrid stems (safe for {{eq:n}} placeholders)
        prompt = polish_ocr_stem(prompt)
        if figure or re.search(r"(?i)\b(scatterplot|table|graph|figure)\b", prompt or ""):
            prompt = strip_chart_noise(prompt)
            prompt = polish_ocr_stem(prompt)
        # Drop equation crops that polish replaced with plain text (or left unused)
        if equation_images and "{{eq:" not in (prompt or ""):
            equation_images = []
        # Circle equations: prefer clean text over a truncated {{eq}} crop
        if "{{eq:" in (prompt or "") and re.search(r"(?i)circle M is the graph", prompt or ""):
            if not re.search(r"\(x\s*-\s*4\)²", prompt or ""):
                prompt = re.sub(
                    r"\{\{eq:\d+\}\}",
                    "(x - 4)² + (y - 5)² = 9",
                    prompt,
                    count=1,
                )
            else:
                prompt = re.sub(r"\{\{eq:\d+\}\}", "", prompt)
                prompt = re.sub(r"\s{2,}", " ", prompt).strip()
            equation_images = []

        pdf_choices = extract_choices_text(text) if kind == "mc" else None
        choice_objs = extract_choice_objects(page, qid, pdf_choices) if kind == "mc" else []

        # SPR answer values are already in correct_answer; stem still via build_math_prompt
        if kind == "spr" and not prompt:
            prompt = clean_text(extract_question_body(text)) or "Enter your answer."

        item = {
            "id": qid,
            "topic": skill or domain,
            "domain": domain,
            "skill": skill,
            "difficulty": difficulty,
            "pool": "Summer 2026 Bank",
            "prompt": prompt,
            "type": kind,
            "explanation": explanation,
        }
        if qid in unanswered_by_id:
            item["pdf"] = MATH_PDF_UNANSWERED_URL
            item["pdfPage"] = unanswered_by_id[qid] + 1
        elif qid in answered_by_id:
            item["pdf"] = MATH_PDF_ANSWERED_URL
            item["pdfPage"] = answered_by_id[qid] + 1
        preview = crop_math_pdf_preview(page, MATH_PDF_PREVIEW / f"{qid}.jpg")
        if preview:
            item["pdfPreview"] = f"/{preview}"
        if figure:
            item["figure"] = figure
        if equation_images:
            item["equations"] = equation_images
        if figure:
            item["prompt"] = strip_chart_noise(item["prompt"])
            item["prompt"] = polish_ocr_stem(item["prompt"])
        if kind == "mc":
            item["choices"] = choice_objs
            item["answer"] = ans
        else:
            item["choices"] = []
            item["acceptedAnswers"] = ans
            item["answer"] = ans[0] if ans else ""

        items.append(item)
        if n % 10 == 0 or n == 1 or qid in {"fc4a0d2a", "6c67dd47"}:
            preview = prompt.replace("\n", " | ")[:90]
            ch_prev = [c.get("text") or ("[img]" if c.get("image") else "?") for c in choice_objs[:4]]
            print(f"math {n}/{len(groups)} {qid}: {preview} :: {ch_prev if kind == 'mc' else 'SPR'}")

    path = DATA / "mathQuestions.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} math questions")

    counts = defaultdict(lambda: {"total": 0, "bySkill": defaultdict(int)})
    for q in items:
        counts[q["domain"]]["total"] += 1
        counts[q["domain"]]["bySkill"][q["skill"]] += 1
    (DATA / "mathSkillCounts.json").write_text(
        json.dumps({d: {"total": v["total"], "skills": dict(v["bySkill"])} for d, v in counts.items()}, indent=2),
        encoding="utf-8",
    )
    return items


def main():
    reading = extract_reading()
    extract_math()
    rcounts = defaultdict(lambda: {"total": 0, "bySkill": defaultdict(int)})
    for q in reading:
        rcounts[q["domain"]]["total"] += 1
        rcounts[q["domain"]]["bySkill"][q["skill"]] += 1
    (DATA / "readingSkillCounts.json").write_text(
        json.dumps({d: {"total": v["total"], "skills": dict(v["bySkill"])} for d, v in rcounts.items()}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
