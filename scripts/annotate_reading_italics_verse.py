#!/usr/bin/env python3
"""Mark SAT Reading italics (<em>) and poem/play line breaks from official PDFs."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data" / "readingQuestions.json"

SUMMER_PDF = Path("/Users/vedsingh/Downloads/English 150 questions.pdf")
EDUCATOR_ROOT = Path("/Users/vedsingh/Downloads/SAT Bank 1/English")
STUDENT_ROOT = Path("/Users/vedsingh/Downloads/Student Bank 1")
PUBLIC_READING = ROOT / "public" / "qbank" / "reading"

TAG_RE = re.compile(r"</?(?:em|u|i)>", re.I)
HTML_RE = re.compile(r"<[^>]+>")
STEM_RE = re.compile(
    r"^(Which choice|Which quotation|Which statement|Which finding|Which detail|"
    r"Based on the texts?|Taken together|What choice|What is the|As used in|"
    r"How does|Why does)\b",
    re.I,
)
FOLLOWING_RE = re.compile(
    r'^(The following text is (?:adapted from|from) .+?[.”"\'»])\s+',
    re.S,
)


def letterish(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]{2,}", text or ""))


def extract_body_lines(page: fitz.Page):
    qid = None
    lines = []
    in_q = False
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = []
            for span in line.get("spans", []):
                text = span.get("text") or ""
                if not text:
                    continue
                spans.append({
                    "text": text,
                    "font": span.get("font") or "",
                    "x": span["bbox"][0],
                })
            if not spans:
                continue
            text = "".join(sp["text"] for sp in spans)
            stripped = text.strip()
            match = re.search(r"Question ID[:\s]+([0-9a-f]+)", stripped, re.I)
            if match:
                qid = match.group(1).lower()
            if stripped == "Question":
                in_q = True
                continue
            # Student Bank PDFs have no lone "Question" header; body starts after ID.
            if not in_q and qid and re.match(rf"ID:\s*{re.escape(qid)}$", stripped, re.I):
                in_q = True
                continue
            if in_q and (
                stripped == "Answer"
                or stripped.startswith("Correct Answer")
                or re.match(r"ID:\s*[0-9a-f]+\s+Answer\b", stripped, re.I)
            ):
                return qid, lines
            if in_q:
                lines.append({
                    "text": text,
                    "x": min(sp["x"] for sp in spans),
                    "spans": spans,
                })
    return qid, lines


def italic_fonts_for(lines) -> set[str]:
    counts = Counter()
    for line in lines:
        for span in line["spans"]:
            if letterish(span["text"]):
                counts[span["font"]] += len(re.findall(r"[A-Za-z]", span["text"]))
    if not counts:
        return set()
    dominant = counts.most_common(1)[0][0]
    italic = set()
    for line in lines:
        fonts = {sp["font"] for sp in line["spans"] if letterish(sp["text"])}
        if dominant in fonts and len(fonts) > 1:
            italic |= fonts - {dominant}
    return italic


def italic_phrases(lines, italic_fonts: set[str]) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []

    def flush():
        if not buf:
            return
        phrase = re.sub(r"\s+", " ", "".join(buf)).strip(" \t,;:")
        phrase = re.sub(r"\s+", " ", phrase).strip()
        letters = re.sub(r"[^A-Za-z]", "", phrase)
        if len(letters) >= 2 and phrase.lower() not in {"a", "an", "the", "of", "to", "in", "on", "or", "and"}:
            chunks.append(phrase)
        buf.clear()

    in_italic = False
    for line in lines:
        for span in line["spans"]:
            text = span["text"]
            font = span["font"]
            if font in italic_fonts and re.search(r"[A-Za-z]", text):
                in_italic = True
                buf.append(text)
                continue
            if in_italic and not letterish(text):
                buf.append(text)
                continue
            flush()
            in_italic = False
        # titles often wrap; keep the run going
    flush()

    seen = set()
    unique = []
    for phrase in chunks:
        key = re.sub(r"\s+", " ", phrase).strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(phrase)
    return unique


def verse_lines(lines) -> list[str]:
    if not lines:
        return []
    full = " ".join(ln["text"].strip() for ln in lines)
    if full.startswith("While researching a topic"):
        return []
    lefts = [ln["x"] for ln in lines if len(ln["text"].strip()) >= 20 and not STEM_RE.match(ln["text"].strip())]
    if not lefts:
        return []
    margin = min(lefts)
    run: list[str] = []
    best: list[str] = []
    for line in lines:
        text = re.sub(r"\s+", " ", line["text"]).strip()
        if not text or STEM_RE.match(text) or re.match(r"^[A-D]\.", text):
            if len(run) > len(best):
                best = run
            run = []
            continue
        if line["x"] >= margin + 18 and 8 <= len(text) <= 100:
            run.append(text)
        else:
            if len(run) > len(best):
                best = run
            run = []
    if len(run) > len(best):
        best = run
    if len(best) < 3:
        return []
    if best[0].lstrip().startswith(('"', "”", "'", "“")):
        return []
    literary = bool(re.search(r"\b(poem|play|sonnet|stanza|verse)\b", full, re.I))
    speaker = bool(re.match(r"^[A-Z][A-Z .'-]{0,24}:", best[0]))
    if not literary and not speaker:
        return []
    return best


def phrase_regex(phrase: str) -> re.Pattern:
    parts = []
    for ch in phrase:
        if ch.isspace():
            parts.append(r"\s*")
        elif ch.isalnum():
            parts.append(re.escape(ch) + r"\s*")
        else:
            parts.append(r"\s*" + re.escape(ch) + r"\s*")
    return re.compile("".join(parts))


def protected_ranges(text: str) -> list[tuple[int, int]]:
    ranges = []
    for match in re.finditer(r"<em>[\s\S]*?</em>|<u>[\s\S]*?</u>|<[^>]+>", text, re.I):
        ranges.append((match.start(), match.end()))
    return ranges


def overlaps(start: int, end: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start < hi and end > lo for lo, hi in ranges)


def apply_em(text: str, phrases: list[str]) -> str:
    if not text or not phrases:
        return text
    out = text
    for phrase in sorted(phrases, key=lambda p: len(re.sub(r"\s+", "", p)), reverse=True):
        try:
            rx = phrase_regex(phrase)
        except re.error:
            continue
        protected = protected_ranges(out)
        matches = []
        for match in rx.finditer(out):
            if overlaps(match.start(), match.end(), protected):
                continue
            inner = match.group(0)
            if re.search(r"</?(?:em|u)>", inner, re.I):
                continue
            lead = re.match(r"^\s*", inner).group(0)
            trail = re.search(r"\s*$", inner).group(0)
            core = inner.strip()
            if len(re.sub(r"[^A-Za-z]", "", core)) < 2:
                continue
            matches.append((match.start(), match.end(), f"{lead}<em>{core}</em>{trail}"))
        for start, end, wrapped in reversed(matches):
            out = out[:start] + wrapped + out[end:]
            protected = protected_ranges(out)
    return out


def compact_index(text: str):
    compact = []
    idxs = []
    for i, ch in enumerate(text):
        if ch.isalnum():
            compact.append(ch.lower())
            idxs.append(i)
    return "".join(compact), idxs


def inject_verse_newlines(text: str, lines: list[str]) -> str | None:
    if not text or len(lines) < 3:
        return None
    tagged = bool(TAG_RE.search(text))
    working = TAG_RE.sub("", text) if tagged else text
    compact, idxs = compact_index(working)
    cursor = 0
    cuts = []
    for line in lines:
        needle = re.sub(r"[^a-z0-9]+", "", line.lower())
        if len(needle) < 8:
            continue
        pos = compact.find(needle[: min(24, len(needle))], cursor)
        if pos < 0:
            pos = compact.find(needle[:12], cursor)
        if pos < 0:
            return None
        if pos > 0:
            cuts.append(idxs[pos] if pos < len(idxs) else idxs[-1])
        cursor = pos + max(4, min(len(needle), 12))
    if len(cuts) < 2:
        return None
    chars = list(working)
    for cut in sorted(set(cuts), reverse=True):
        # insert newline at the start of this line's first letter
        while cut > 0 and chars[cut - 1].isspace():
            cut -= 1
        chars.insert(cut, "\n")
    lined = re.sub(r"[ \t]+\n", "\n", "".join(chars))
    lined = re.sub(r"\n[ \t]+", "\n", lined)
    lined = re.sub(r"\n{3,}", "\n\n", lined).strip()
    return lined


def apply_em_fields(obj, phrases: list[str]):
    if isinstance(obj, str):
        return apply_em(obj, phrases)
    if isinstance(obj, list):
        return [apply_em_fields(item, phrases) for item in obj]
    if isinstance(obj, dict):
        skip = {"id", "pdf", "pdfPage", "pool", "topic", "domain", "skill", "difficulty", "type", "answer", "figure"}
        return {k: (v if k in skip else apply_em_fields(v, phrases)) for k, v in obj.items()}
    return obj


def index_pdfs() -> dict[str, tuple[Path, int, list]]:
    files = []
    if EDUCATOR_ROOT.exists():
        files.extend(sorted(p for p in EDUCATOR_ROOT.rglob("*.pdf") if "Extract" not in p.name and "Exract" not in p.name))
    if STUDENT_ROOT.exists():
        files.extend(sorted(STUDENT_ROOT.glob("*.pdf")))
    if PUBLIC_READING.exists():
        files.extend(sorted(PUBLIC_READING.glob("Student-Bank-1-*.pdf")))
    if SUMMER_PDF.exists():
        files.append(SUMMER_PDF)
    by_id: dict[str, tuple[Path, int, list]] = {}
    summer_ids: dict[str, tuple[Path, int, list]] = {}
    for path in files:
        doc = fitz.open(path)
        is_summer = path == SUMMER_PDF
        for i, page in enumerate(doc):
            qid, lines = extract_body_lines(page)
            if not qid or not lines:
                continue
            payload = (path, i, lines)
            if is_summer:
                summer_ids[qid] = payload
            else:
                by_id.setdefault(qid, payload)
    by_id.update(summer_ids)
    return by_id


def maybe_split_source(question: dict) -> None:
    passage = question.get("passage") or ""
    if question.get("source") or "\n" not in passage:
        return
    first, rest = passage.split("\n", 1)
    if re.match(r"^The following text is (?:adapted from|from)\b", first.strip(), re.I):
        question["source"] = first.strip()
        question["passage"] = rest.strip()


def main() -> int:
    questions = json.loads(DATA.read_text())
    index = index_pdfs()
    verse_n = 0
    italic_n = 0
    missing = 0
    for question in questions:
        qid = str(question.get("id") or "").lower()
        payload = index.get(qid)
        if not payload:
            missing += 1
            continue
        _path, _i, lines = payload
        fonts = italic_fonts_for(lines)
        phrases = italic_phrases(lines, fonts)
        verse = verse_lines(lines)
        if verse:
            passage = question.get("passage") or ""
            updated = inject_verse_newlines(passage, verse)
            if updated and updated != passage:
                question["passage"] = updated
                verse_n += 1
            maybe_split_source(question)
            if question.get("source") and "\n" in (question.get("passage") or ""):
                pass
            elif verse and not question.get("source"):
                maybe_split_source(question)
        if phrases:
            before = json.dumps(question, ensure_ascii=False)
            updated_q = apply_em_fields(question, phrases)
            question.clear()
            question.update(updated_q)
            if json.dumps(question, ensure_ascii=False) != before:
                italic_n += 1

    DATA.write_text(json.dumps(questions, indent=2, ensure_ascii=False) + "\n")
    print(f"indexed={len(index)} missing={missing} verse={verse_n} italicized={italic_n}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / ".pdf_tools"))
    raise SystemExit(main())
