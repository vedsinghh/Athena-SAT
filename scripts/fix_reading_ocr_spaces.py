#!/usr/bin/env python3
"""Repair OCR mid-word spaces in readingQuestions.json from English rationales PDF."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "src/data/readingQuestions.json"
PDF_PATH = Path("/Users/vedsingh/Downloads/English_Rationales_Program_Readable_FIXED.pdf")

FORBIDDEN_LEFT = {
    "a", "an", "the", "and", "or", "of", "to", "for", "is", "are", "was", "were",
    "be", "been", "being", "with", "as", "by", "from", "that", "this", "these",
    "those", "it", "its", "not", "but", "if", "so", "only", "into", "onto",
    "than", "then", "also", "just", "very", "more", "most", "such", "both",
    "each", "few", "many", "much", "own", "same", "other", "over", "after",
    "before", "between", "through", "during", "above", "below", "under",
}
FORBIDDEN_RIGHT = FORBIDDEN_LEFT | {"only", "other", "early", "later", "even"}


def build_wordset() -> set[str]:
    words = {
        w.strip().lower()
        for w in open("/usr/share/dict/words")
        if w.strip().isalpha() and len(w.strip()) >= 2
    }
    extras: set[str] = set()
    for w in list(words):
        extras.update(
            {
                w + "s",
                w + "es",
                w + "ed",
                w + "ing",
                w + "er",
                w + "ers",
                w + "ly",
                w + "ness",
                w + "ment",
                w + "ments",
                w + "tion",
                w + "ations",
                w + "ation",
            }
        )
        if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
            extras.add(w[:-1] + "ies")
            extras.add(w[:-1] + "ied")
        if w.endswith("e"):
            extras.add(w + "d")
            extras.add(w[:-1] + "ing")
        if w.endswith("f"):
            extras.add(w[:-1] + "ves")
        if w.endswith("fe"):
            extras.add(w[:-2] + "ves")
    words |= extras
    words.update(
        """
        microplastics stratigraphic anthropocene ecotypes duckweed ecological
        vertebrates paleontologist bertrand ornella mammalian dinosaurs niches
        ratios abundance intensified conversely sedimentary chronologically
        hypothesized locally adaptations pollutants vacated intelligence
        populations moderated facilitated twentieth european alberto inclination
        consideration behavior information language learning phrase either
        another problem reason bodies sizes researchers participants feathered
        humans technology sahanan saharan atmosphere although beginning
        deposited remaining diminishes unrelated inverse student conducted
        remained reached mixtures consisting processing changed supported
        primed poem snorts party like wolf-like major-party
        """.split()
    )
    return words


WORDSET = build_wordset()


def cores(tok: str):
    m = re.match(r"^([^A-Za-z]*)([A-Za-z]+(?:-[A-Za-z]+)*)([^A-Za-z]*)$", tok)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def should_join(left: str, right: str) -> bool:
    lc, rc = cores(left), cores(right)
    if not lc or not rc:
        return False
    if lc[0] or lc[2] or rc[0]:
        return False
    a, b = lc[1], rc[1]
    al, bl = a.lower(), b.lower()

    # Hyphenated tail fragment: non-wolf-li + ke → non-wolf-like
    if "-" in a:
        head, _, tail = a.rpartition("-")
        merged_tail = (tail + b).lower()
        if merged_tail in WORDSET or merged_tail in {"like", "based", "related", "party", "level"}:
            return True

    combo = al + bl
    if combo not in WORDSET:
        # Capitalized name fragments (Ber + trand)
        if (
            a[0].isupper()
            and al not in WORDSET
            and bl not in WORDSET
            and 2 <= len(al) <= 6
            and 3 <= len(bl) <= 8
        ):
            return True
        return False

    if al in FORBIDDEN_LEFT or bl in FORBIDDEN_RIGHT:
        return False

    # Avoid gluing two long standalone words ("complex brains")
    if al in WORDSET and bl in WORDSET and len(al) >= 4 and len(bl) >= 4:
        return False

    return True


def join_pair(left: str, right: str) -> str:
    lc, rc = cores(left), cores(right)
    assert lc and rc
    a, b = lc[1], rc[1]
    if "-" in a:
        head, _, tail = a.rpartition("-")
        merged_tail = tail + b
        if (merged_tail.lower() in WORDSET) or merged_tail.lower() in {
            "like",
            "based",
            "related",
            "party",
            "level",
        }:
            return lc[0] + head + "-" + merged_tail + rc[2]
    return lc[0] + a + b + rc[2]


def fix_midword_spaces(text: str) -> str:
    t = re.sub(r"\s*-\s*", "-", text)
    t = re.sub(r"(?i)\bbr\s*ain\b", "brain", t)
    t = re.sub(r"(?i)brain-tobody", "brain-to-body", t)
    tokens = t.split(" ")
    changed = True
    guard = 0
    while changed and guard < 25:
        guard += 1
        changed = False
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and should_join(tokens[i], tokens[i + 1]):
                new_tokens.append(join_pair(tokens[i], tokens[i + 1]))
                i += 2
                changed = True
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return " ".join(tokens)


FORCE = [
    (r"\btwentie\s+th\b", "twentieth"),
    (r"\bpr\s+oblem\b", "problem"),
    (r"\blearni\s+ng\b", "learning"),
    (r"\blang\s+uage\b", "language"),
    (r"\bbodi\s+es\b", "bodies"),
    (r"\banot\s+her\b", "another"),
    (r"\bEurope\s+an\b", "European"),
    (r"\bAlber\s+to\b", "Alberto"),
    (r"\bve\s+rb\b", "verb"),
    (r"\bbe\s+cause\b", "because"),
    (r"\bbeca\s+use\b", "because"),
    (r"\bbecau\s+se\b", "because"),
    (r"\bhum\s+ans\b", "humans"),
    (r"\bfeather\s+ed\b", "feathered"),
    (r"\bresear\s+chers\b", "researchers"),
    (r"\bRich\s+ard\b", "Richard"),
    (r"\bparticipa\s+nts\b", "participants"),
    (r"\bpartic\s+ipants\b", "participants"),
    (r"\bsnor\s+ts\b", "snorts"),
    (r"\bpo\s+em\b", "poem"),
    (r"\bli\s+ke\b", "like"),
    (r"\bpar\s+ty\b", "party"),
    (r"\bbeg\s+inning\b", "beginning"),
    (r"\bdeposi\s+ted\b", "deposited"),
    (r"\bde\s+pending\b", "depending"),
    (r"\ban\s+other\b", "another"),
    (r"\bsubver\s+ted\b", "subverted"),
    (r"\brema\s+ining\b", "remaining"),
    (r"\bdi\s+minishes\b", "diminishes"),
    (r"\bun\s+related\b", "unrelated"),
    (r"\bin\s+verse\b", "inverse"),
    (r"\bSah\s+aran\b", "Saharan"),
    (r"\bte\s+chnology\b", "technology"),
    (r"\bstude\s+nt\b", "student"),
    (r"\bcondu\s+cted\b", "conducted"),
    (r"\bre\s+mained\b", "remained"),
    (r"\breac\s+hed\b", "reached"),
    (r"\bmix\s+tures\b", "mixtures"),
    (r"\bre\s+lated\b", "related"),
    (r"\bstudy\s+ing\b", "studying"),
    (r"\bcon\s+sisting\b", "consisting"),
    (r"\bat\s+mosphere\b", "atmosphere"),
    (r"\bproces\s+sing\b", "processing"),
    (r"\bcha\s+nged\b", "changed"),
    (r"\bsuppor\s+ted\b", "supported"),
    (r"\bAl\s+though\b", "Although"),
    (r"\bstar\s+ted\b", "started"),
    (r"\baddress\s+ed\b", "addressed"),
    (r"\bpr\s+imed\b", "primed"),
]


def force_fix(t: str) -> str:
    for pat, rep in FORCE:
        t = re.sub(pat, rep, t, flags=re.I)
    return t


def normalize_prose(text: str) -> str:
    t = text.replace("\u00ad", "")
    # Keep scare quotes as singles so they don't nest inside wrapping "..."
    t = re.sub(r"\u2018([^\u2019]*)\u2019", lambda m: "'" + m.group(1).strip() + "'", t)
    t = (
        t.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "\u2014")
    )
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    joined = " ".join(lines)
    joined = re.sub(
        r"([A-Za-z])\s+([\u00e0-\u00ff\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff])",
        r"\1\2",
        joined,
    )
    joined = re.sub(r"([\u00e0-\u00ff])\s+([A-Za-z])", r"\1\2", joined)
    joined = re.sub(r"\s+,", ",", joined)
    joined = re.sub(r"\s+\.", ".", joined)
    joined = re.sub(r"\s+;", ";", joined)
    joined = re.sub(r"\s+:", ":", joined)
    joined = re.sub(r"\(\s+", "(", joined)
    joined = re.sub(r"\s+\)", ")", joined)
    joined = re.sub(r"\s+\u2014\s+", " \u2014 ", joined)
    joined = re.sub(r"\s+", " ", joined).strip()
    joined = fix_midword_spaces(joined)
    joined = force_fix(joined)
    joined = fix_apostrophes(joined)
    joined = fix_double_quotes(joined)
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def fix_double_quotes(text: str) -> str:
    """Pair double quotes; scare quotes stay as singles so nesting is rare."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '"':
            j = text.find('"', i + 1)
            if j < 0:
                out.append(text[i:])
                break
            inner = text[i + 1 : j].strip()
            if out:
                prev = out[-1][-1:]
                if prev.isalnum() or prev in ":,;":
                    out.append(" ")
            out.append(f'"{inner}"')
            if j + 1 < n and text[j + 1].isalnum():
                out.append(" ")
            i = j + 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def fix_apostrophes(text: str) -> str:
    """Normalize apostrophes without eating possessives or scare quotes."""
    t = re.sub(r"\b([A-Za-z]+)\s*'\s*(s|re|ve|ll|d|m)\b", r"\1'\2", text, flags=re.I)
    t = re.sub(r"\b([A-Za-z]+)n\s*'\s*t\b", r"\1n't", t, flags=re.I)
    # dinosaurs ' → dinosaurs' (not a 'quoted word')
    t = re.sub(r"([A-Za-z])\s+'(?=\s|$|[,.;:!?\)\]])", r"\1'", t)

    def repl(m: re.Match) -> str:
        left, right = m.group(1), m.group(2)
        if right.lower() in {"s", "re", "ve", "ll", "d", "m", "t"}:
            return left + "'" + right
        return left + "' " + right

    return re.sub(r"([A-Za-z])'([A-Za-z]+)", repl, t)


def format_explanation(raw: str) -> str:
    text = normalize_prose(raw)
    m = re.search(r"(?=Choice [A-D] is incorrect\b)", text)
    if m:
        return f"{text[: m.start()].strip()}\n\n{text[m.start() :].strip()}"
    return text


def load_rationale_blocks() -> dict[str, str]:
    from pypdf import PdfReader

    full = "\n".join((p.extract_text() or "") for p in PdfReader(str(PDF_PATH)).pages)
    blocks: dict[str, str] = {}
    for m in re.finditer(r"QUESTION_ID:\s*([0-9a-fA-F]+)\s*\n?RATIONALE:\s*", full):
        qid = m.group(1)
        start = m.end()
        end_m = re.search(r"\nEND_RATIONALE", full[start:])
        if end_m:
            blocks[qid] = full[start : start + end_m.start()]
    return blocks


def main() -> int:
    if not PDF_PATH.exists():
        print(f"Missing PDF: {PDF_PATH}", file=sys.stderr)
        return 1

    subprocess.check_call(["git", "checkout", "HEAD", "--", str(JSON_PATH.relative_to(ROOT))], cwd=ROOT)
    blocks = load_rationale_blocks()
    data = json.loads(JSON_PATH.read_text())

    for q in data:
        if q["id"] in blocks:
            q["explanation"] = format_explanation(blocks[q["id"]])
        if q.get("passage"):
            parts = re.split(r"\n\s*\n", q["passage"])
            q["passage"] = "\n\n".join(normalize_prose(p) for p in parts if p.strip())
        if q.get("prompt"):
            q["prompt"] = normalize_prose(q["prompt"])
        for ch in q.get("choices") or []:
            if isinstance(ch, dict) and ch.get("text"):
                ch["text"] = normalize_prose(ch["text"])

    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # Validation
    hits = []
    for q in data:
        for field in ("passage", "prompt", "explanation"):
            text = q.get(field) or ""
            for m in re.finditer(r"\b([A-Za-z]{2,8})\s+([a-z]{2,8})\b", text):
                a, b = m.group(1), m.group(2)
                combo = (a + b).lower()
                if combo not in WORDSET or len(a) + len(b) < 6:
                    continue
                if a.lower() in FORBIDDEN_LEFT or b.lower() in FORBIDDEN_RIGHT:
                    continue
                if a.lower() in WORDSET and b.lower() in WORDSET and len(a) >= 4 and len(b) >= 4:
                    continue
                hits.append((q["id"], field, m.group(0), combo))

    q = next(x for x in data if x["id"] == "45f66433")
    print("sample passage ok:", "vertebrates" in q["passage"] and "Bertrand" in q["passage"])
    print("sample expl bodies:", "bodies" in q["explanation"] and "becauseit" not in q["explanation"])
    print("remaining OCR-like hits:", len(hits))
    for h in hits[:40]:
        print(" ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
