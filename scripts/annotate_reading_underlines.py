#!/usr/bin/env python3
"""Annotate Reading & Writing passages with <u>...</u> from PDF underline drawings.

College Board PDFs mark referenced spans with thin filled rectangles. Extraction
historically dropped those decorations; this script recovers them for every
question that mentions \"underlined\" and writes markup into readingQuestions.json.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from repair_passage_prompt_mix import repair_question as repair_passage_prompt_fields

DATA = ROOT / "src" / "data" / "readingQuestions.json"
PUBLIC = ROOT / "public"

STEM_INLINE_RE = re.compile(
    r"(?P<stem>"
    r"(?:Which choice|Which statement|Which detail|Which finding|Which quotation|"
    r"Taken together|Based on the texts?|Based on the text|"
    r"What choice|What is the|As used in|"
    r"How does|Why does)\b[\s\S]*)$",
    re.I,
)

U_TAG_RE = re.compile(r"</?u>", re.I)


def strip_u_tags(text: str) -> str:
    return U_TAG_RE.sub("", text or "")


def content_underline_rects(page: fitz.Page) -> list[fitz.Rect]:
    thin: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        fill = drawing.get("fill")
        if not isinstance(fill, (tuple, list)) or max(fill) > 0.15:
            continue
        for item in drawing.get("items", []):
            if item[0] != "re":
                continue
            rect = item[1]
            height = abs(rect.y1 - rect.y0)
            width = abs(rect.x1 - rect.x0)
            if 0.2 <= height <= 2.5 and width >= 15:
                thin.append(fitz.Rect(rect))
    thin.sort(key=lambda r: (round(r.y0, 1), r.x0))
    return thin


def words_over_underline(page: fitz.Page, urect: fitz.Rect) -> list:
    hits = []
    for word in page.get_text("words"):
        wr = fitz.Rect(word[:4])
        if wr.y1 < urect.y0 - 12 or wr.y0 > urect.y1 + 2:
            continue
        if wr.x1 < urect.x0 - 1 or wr.x0 > urect.x1 + 1:
            continue
        overlap = min(wr.x1, urect.x1) - max(wr.x0, urect.x0)
        if overlap < min(3, wr.width * 0.15):
            continue
        clipped = clip_word_to_underline(word[4], wr, urect)
        if not clipped:
            continue
        # Preserve position metadata; replace text with clipped fragment.
        hits.append((word[0], word[1], word[2], word[3], clipped, *word[5:]))
    hits.sort(key=lambda w: (round(w[1], 1), w[0]))
    return hits


def clip_word_to_underline(text: str, wr: fitz.Rect, urect: fitz.Rect) -> str | None:
    """Keep only the part of a PDF word that sits under the underline.

    College Board often underlines the middle of an em-dash parenthetical, but MuPDF
    returns glued tokens like ``rock—a`` / ``rock—marched``. Using the full token
    over-underlines into neighboring words.
    """
    text = str(text or "")
    if not text:
        return None
    overlap_x0 = max(wr.x0, urect.x0)
    overlap_x1 = min(wr.x1, urect.x1)
    overlap = overlap_x1 - overlap_x0
    if overlap <= 0:
        return None
    frac = overlap / max(wr.width, 1e-6)
    # Intact words / ASCII hyphen compounds (dare-devil, grid-cell).
    if frac >= 0.75 or not re.search(r"[—–]", text):
        return text if frac >= 0.15 else None

    # Estimate which characters lie under the underline and keep that span.
    n = len(text)
    keep_idx = [
        i
        for i in range(n)
        if min(wr.x0 + wr.width * (i + 1) / n, overlap_x1)
        - max(wr.x0 + wr.width * i / n, overlap_x0)
        > 0.25 * (wr.width / n)
    ]
    if not keep_idx:
        return None
    clipped = text[keep_idx[0] : keep_idx[-1] + 1].strip("—–-")
    # Drop a dangling comma/punctuation-only clip.
    if not re.search(r"[\w]", clipped):
        return None
    return clipped


def group_underline_rects(rects: list[fitz.Rect], page: fitz.Page) -> list[list[fitz.Rect]]:
    """Group contiguous / line-wrapped underline segments; keep separate portions apart."""
    if not rects:
        return []
    groups: list[list[fitz.Rect]] = [[rects[0]]]
    for rect in rects[1:]:
        prev = groups[-1][-1]
        same_line = abs(rect.y0 - prev.y0) < 2.5
        contiguous = same_line and rect.x0 <= prev.x1 + 12
        wrapped = (
            not same_line
            and 2.5 < (rect.y0 - prev.y0) <= 18
            and rect.x0 < 90
        )
        if contiguous:
            groups[-1].append(rect)
            continue
        if wrapped:
            prev_words = words_over_underline(page, prev)
            if prev_words and not re.search(r'[.!?]"?$', prev_words[-1][4]):
                groups[-1].append(rect)
                continue
        groups.append([rect])
    return groups


def phrase_from_rects(page: fitz.Page, rects: list[fitz.Rect]) -> str:
    words = []
    for rect in rects:
        words.extend(words_over_underline(page, rect))
    # de-dupe while preserving reading order
    seen = set()
    ordered = []
    for word in sorted(words, key=lambda w: (round(w[1], 1), w[0])):
        key = (round(word[0], 1), round(word[1], 1), word[4])
        if key in seen:
            continue
        seen.add(key)
        ordered.append(word[4])
    phrase = " ".join(ordered).strip()
    return trim_dash_parenthetical_phrase(phrase)


def trim_dash_parenthetical_phrase(phrase: str) -> str:
    """If extraction still has ``rock—a soft…rock—marched``, keep the middle."""
    phrase = (phrase or "").strip()
    m = re.match(r"^(\S+?)[—–](.+)[—–](\S+)$", phrase)
    if not m:
        return phrase
    left, mid, right = m.group(1), m.group(2).strip("—–- "), m.group(3)
    # Only trim when sides look like single host words, not a full clause.
    if " " not in left and " " not in right and len(mid) >= 5:
        return mid
    return phrase


def alnum_map(text: str) -> tuple[str, list[int]]:
    norm: list[str] = []
    idx: list[int] = []
    for i, ch in enumerate(text):
        for c in unicodedata.normalize("NFKC", ch):
            if c.isalnum():
                norm.append(c.lower())
                idx.append(i)
    return "".join(norm), idx


def find_alnum_span(haystack: str, needle: str) -> tuple[int, int] | None:
    h_norm, h_idx = alnum_map(haystack)
    n_norm, _ = alnum_map(needle)
    if not h_norm or not n_norm:
        return None

    def span_from_norm(start_pos: int, end_pos: int) -> tuple[int, int]:
        end_pos = min(end_pos, len(h_idx) - 1)
        start_i = h_idx[start_pos]
        end_i = h_idx[end_pos] + 1
        while end_i < len(haystack) and haystack[end_i] in ",.;:!?\"'”’":
            end_i += 1
        while start_i > 0 and haystack[start_i - 1] in "\"“‘'":
            start_i -= 1
        return start_i, end_i

    pos = h_norm.find(n_norm)
    if pos >= 0:
        return span_from_norm(pos, pos + len(n_norm) - 1)

    # PDF OCR often inserts spaces ("ar t") or bank typos drift ("throughut").
    # Anchor on a solid head + tail of the underlined phrase.
    if len(n_norm) >= 28:
        head_len = min(40, max(24, len(n_norm) // 2))
        tail_len = min(32, max(16, len(n_norm) // 4))
        for shrink in range(0, 12, 2):
            head = n_norm[: max(20, head_len - shrink)]
            hpos = h_norm.find(head)
            if hpos < 0:
                continue
            tail = n_norm[-max(12, tail_len - shrink) :]
            tpos = h_norm.find(tail, hpos + len(head))
            if tpos >= 0:
                return span_from_norm(hpos, tpos + len(tail) - 1)
            # Fall back to approximate length from the head match.
            return span_from_norm(hpos, hpos + len(n_norm) - 1)

    if len(n_norm) > 48:
        pos = h_norm.find(n_norm[: len(n_norm) - 12])
        if pos >= 0:
            return span_from_norm(pos, pos + len(n_norm) - 1)
    return None



def apply_spans(text: str, spans: list[tuple[int, int]]) -> str:
    if not text or not spans:
        return text
    # merge overlaps
    spans = sorted(spans)
    merged: list[list[int]] = []
    for start, end in spans:
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    out = text
    for start, end in reversed(merged):
        out = f"{out[:start]}<u>{out[start:end]}</u>{out[end:]}"
    return out


def repair_stem_in_passage(passage: str, prompt: str, skill: str = "") -> tuple[str, str]:
    """Unmix passage body vs question stem (both directions)."""
    tmp = {"passage": passage or "", "prompt": prompt or "", "skill": skill or ""}
    repair_passage_prompt_fields(tmp)
    passage, prompt = tmp["passage"], tmp["prompt"]

    # Prefer copyright / attribution boundary then stem (placeholder prompts).
    if (prompt or "").strip() and (prompt or "").strip() != "Select the best answer.":
        return passage, prompt
    m = re.search(
        r"(©\d{4} by [^.]+?\.)\s*(?P<stem>(?:Taken together|Which detail|Which choice)\b[\s\S]+)$",
        passage,
    )
    if m:
        stem = m.group("stem").strip()
        cleaned = passage[: m.start("stem")].rstrip()
        return cleaned, stem
    m = STEM_INLINE_RE.search(passage)
    if not m:
        return passage, prompt
    stem = m.group("stem").strip()
    if "?" not in stem and not re.search(r"\bwhich\b", stem, re.I):
        return passage, prompt
    cleaned = passage[: m.start("stem")].rstrip()
    if len(cleaned) < 40:
        return passage, prompt
    return cleaned, stem


def mentions_underlined(question: dict) -> bool:
    blob = " ".join(
        str(question.get(k) or "")
        for k in ("passage", "prompt", "explanation")
    )
    return "underlined" in blob.lower()


VOCAB_WORD_RE = re.compile(
    r'As used in the text,\s+what does the (?:word|phrase)\s+["“]([^"”]+)["”]',
    re.I,
)


def vocab_target_from_prompt(prompt: str) -> str | None:
    m = VOCAB_WORD_RE.search(prompt or "")
    return m.group(1).strip() if m else None


def underline_first_occurrence(text: str, target: str) -> str:
    """Wrap the first case-sensitive (then case-insensitive) occurrence of target."""
    if not text or not target or "<u>" in text:
        # Still allow adding another underline if target isn't already wrapped
        pass
    plain = strip_u_tags(text)
    # Prefer exact case match
    idx = plain.find(target)
    if idx < 0:
        m = re.search(re.escape(target), plain, re.I)
        if not m:
            return text if "<u>" in (text or "") else plain
        idx, end = m.start(), m.end()
        target = plain[idx:end]
    else:
        end = idx + len(target)
    if f"<u>{target}</u>" in text:
        return text
    # Re-apply on stripped text so we don't nest inside existing tags wrongly
    return apply_spans(plain, [(idx, end)])


def should_drop_redundant_figure(question: dict) -> bool:
    """PDF text-crops of the stem are not real figures — hide them in the passage pane."""
    if not question.get("figure"):
        return False
    skill = question.get("skill") or ""
    # Command of Evidence usually has real tables/graphs.
    if skill == "Command of Evidence":
        return False
    blob = f"{question.get('passage') or ''} {question.get('prompt') or ''}"
    if re.search(r"\b(graph|table|figure|chart|scatterplot|diagram)\b", blob, re.I):
        return False
    return True


def annotate_question(question: dict, doc_cache: dict) -> dict:
    q = dict(question)
    passage = strip_u_tags(q.get("passage") or "")
    prompt = strip_u_tags(q.get("prompt") or "")
    passage, prompt = repair_stem_in_passage(passage, prompt, q.get("skill") or "")

    # Words-in-Context vocabulary targets (quoted in the stem).
    vocab = vocab_target_from_prompt(prompt)
    if vocab:
        passage = underline_first_occurrence(passage, vocab)

    if should_drop_redundant_figure(q):
        q["figure"] = None

    pdf_rel = (q.get("pdf") or "").lstrip("/")
    page_num = q.get("pdfPage")
    if not pdf_rel or not page_num:
        q["passage"] = passage
        q["prompt"] = prompt
        return q

    # If vocab underline already applied and this isn't an "underlined portion" item, done.
    if vocab and not mentions_underlined(q):
        q["passage"] = passage
        q["prompt"] = prompt
        return q

    pdf_path = PUBLIC / pdf_rel
    key = str(pdf_path)
    if key not in doc_cache:
        doc_cache[key] = fitz.open(pdf_path)
    page = doc_cache[key][int(page_num) - 1]

    phrases = [
        phrase_from_rects(page, group)
        for group in group_underline_rects(content_underline_rects(page), page)
    ]
    phrases = [p for p in phrases if p]

    passage_spans: list[tuple[int, int]] = []
    prompt_spans: list[tuple[int, int]] = []
    # Start from any vocab span already applied via tags
    if "<u>" in passage:
        q["passage"] = passage
        q["prompt"] = prompt
        # Still try PDF underlines for multi-span items; merge carefully
        base_passage = strip_u_tags(passage)
    else:
        base_passage = passage
    base_prompt = prompt

    for phrase in phrases:
        span = find_alnum_span(base_passage, phrase)
        if span:
            passage_spans.append(span)
            continue
        span = find_alnum_span(base_prompt, phrase)
        if span:
            prompt_spans.append(span)

    q["passage"] = apply_spans(base_passage, passage_spans)
    q["prompt"] = apply_spans(base_prompt, prompt_spans)
    return q


def main() -> None:
    questions = json.loads(DATA.read_text())
    doc_cache: dict = {}
    updated = 0
    missing = []
    fig_cleared = 0
    for i, question in enumerate(questions):
        if should_drop_redundant_figure(question):
            questions[i] = {**question, "figure": None}
            question = questions[i]
            fig_cleared += 1
            updated += 1
        needs = mentions_underlined(question) or bool(vocab_target_from_prompt(question.get("prompt") or ""))
        if not needs:
            continue
        before_p = question.get("passage")
        before_pr = question.get("prompt")
        before_fig = question.get("figure")
        annotated = annotate_question(question, doc_cache)
        questions[i] = annotated
        if "<u>" not in (annotated.get("passage") or "") and "<u>" not in (annotated.get("prompt") or ""):
            missing.append(annotated["id"])
        if (
            annotated.get("passage") != before_p
            or annotated.get("prompt") != before_pr
            or annotated.get("figure") != before_fig
        ):
            updated += 1

    DATA.write_text(json.dumps(questions, indent=2, ensure_ascii=False) + "\n")
    print(f"Updated {updated} questions")
    if fig_cleared:
        print(f"Cleared {fig_cleared} redundant text-crop figures")
    if missing:
        print("Missing underline markup for:", ", ".join(missing))
    else:
        print("All underline/vocab-target questions now have <u> markup")


if __name__ == "__main__":
    main()
