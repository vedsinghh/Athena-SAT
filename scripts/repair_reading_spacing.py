#!/usr/bin/env python3
"""Fix missing/extra spaces in readingQuestions.json from OCR/extraction glitches."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data" / "readingQuestions.json"

# Always join these OCR-split fragments (case-insensitive).
JOIN_SPLITS = [
    (r"\bdeser\s+tification\b", "desertification"),
    (r"\bDeser\s+tification\b", "Desertification"),
    (r"\bproper\s+ties\b", "properties"),
    (r"\bProper\s+ties\b", "Properties"),
    (r"\bphysiochemical\s+proper\s+ties\b", "physiochemical properties"),
    (r"\bpar\s+ticle\b", "particle"),
    (r"\bpar\s+ticles\b", "particles"),
    (r"\bPor\s+trait\b", "Portrait"),
    (r"\bpor\s+trait\b", "portrait"),
    (r"\bpor\s+traits\b", "portraits"),
    (r"\bar\s+tist\b", "artist"),
    (r"\bAr\s+tist\b", "Artist"),
    (r"\bar\s+tists\b", "artists"),
    (r"\bar\s+tistic\b", "artistic"),
    (r"\bar\s+tistry\b", "artistry"),
    (r"\bar\s+twork\b", "artwork"),
    (r"\bar\s+tworks\b", "artworks"),
    (r"\bAr\s+twork\b", "Artwork"),
    (r"\bAr\s+tworks\b", "Artworks"),
    (r"\bhear\s+ted\b", "hearted"),
    (r"\bbrave-hear\s+ted\b", "brave-hearted"),
    (r"\bhear\s+tfelt\b", "heartfelt"),
    (r"\bimpor\s+t\b", "import"),
    (r"\bexpor\s+t\b", "export"),
    (r"\bimpor\s+t/expor\s+t\b", "import/export"),
    (r"\bimpor\s+tation\b", "importation"),
    (r"\bexpor\s+tation\b", "exportation"),
    (r"\bstate\s+ment\b", "statement"),
    (r"\binvest\s+ment\b", "investment"),
    (r"\benter\s+tainment\b", "entertainment"),
    (r"\bmove\s+ments\b", "movements"),
    (r"\badvance\s+ments\b", "advancements"),
    (r"\brhetoric\s+ally\b", "rhetorically"),
    (r"\bsubmissive\s+ness\b", "submissiveness"),
    (r"\bmicro\s+plastics\b", "microplastics"),
    (r"\bThrough\s+out\b", "Throughout"),
    (r"\bthrough\s+out\b", "throughout"),
    (r"\bwhat\s+ever\b", "whatever"),
    (r"\bunder\s+take\b", "undertake"),
    (r"\bunder\s+took\b", "undertook"),
    (r"\bover\s+throw\b", "overthrow"),
    (r"\bfour\s+teen\b", "fourteen"),
    (r"\bsemi\s+colon\b", "semicolon"),
    (r"\bnight\s+time\b", "nighttime"),
    (r"\bnot\s+hing\b", "nothing"),
    (r"\bpar\s+ts\b", "parts"),
    (r"\bar\s+t\b", "art"),
    (r"\bnever\s+theless\b", "nevertheless"),
    (r"\bstar\s+ted\b", "started"),
    (r"\bproper\s+ty\b", "property"),
    # Soft-hyphen / line-break residue
    (r"\bsmar\s+tphone\b", "smartphone"),
    (r"\bsmar\s+tphones\b", "smartphones"),
    (r"\bSmar\s+tphone\b", "Smartphone"),
    (r"\bSmar\s+tphones\b", "Smartphones"),
    (r"\bsmart\s+phones\b", "smartphones"),
    (r"\bexper\s+tise\b", "expertise"),
    (r"\bshor\s+tcuts\b", "shortcuts"),
    (r"\bCar\s+thage\b", "Carthage"),
    (r"\bcon\s+ferred\b", "conferred"),
    (r"\bconfe\s+rred\b", "conferred"),
    (r"\bprop\s+ortion\b", "proportion"),
    (r"\bme\s+gapascals\b", "megapascals"),
    (r"\bprokar\s+yotes\b", "prokaryotes"),
    (r"\bhabit\s+able\b", "habitable"),
    (r"\bCzech\s+oslovakia\b", "Czechoslovakia"),
    (r"\bTh\s+ailand\b", "Thailand"),
    (r"\bSh\s+anawdithit\b", "Shanawdithit"),
    (r"\bcar\s+tography\b", "cartography"),
    (r"\bfur\s+thermore\b", "furthermore"),
    (r"\btur\s+tle\b", "turtle"),
    (r"\bBer\s+tolt\b", "Bertolt"),
    (r"\bAr\s+teaga\b", "Arteaga"),
    (r"\bAr\s+temieva\b", "Artemieva"),
    (r"\bhither\s+to\b", "hitherto"),
    (r"\ban\s+d\b(?=\s+knowledge\b)", "and"),
    (r"\bindic\s+ates\b", "indicates"),
    (r"\bfora\s+ging\b", "foraging"),
    (r"\brec\s+ycled\b", "recycled"),
    (r"\bcons\s+umers\b", "consumers"),
    (r"\bwor\s+thless\b", "worthless"),
    (r"\bpuer\s+to\b", lambda m: "Puerto" if m.group(0)[0].isupper() else "puerto"),
    (r"\bnor\s+th\b", lambda m: "North" if m.group(0)[0].isupper() else "north"),
    (r"K'\s+iche'", "K'iche'"),
]

# Always rewrite these whole-token OCR errors.
TOKEN_FIXES = [
    (r"\binText\b", "in Text"),
    (r"\bthroughut\b", "throughout"),
    (r"\bThroughut\b", "Throughout"),
    (r"\bhowKing\b", "how King"),
    (r"\bin someway\b", "in some way"),
    (r"\binreality\b", "in reality"),
    (r"\bInreality\b", "In reality"),
    (r"\ba ll\b", "all"),
    (r"\bs uggest\b", "suggest"),
    (r"\bPhilippE\.", "Philippe E."),
    (r"\bPhilippeE\.", "Philippe E."),
    (r"\bPhilipp E\.", "Philippe E."),
    (r"\bChoice([A-D])\b", r"Choice \1"),
]


def protect_tags(text: str) -> tuple[str, list[str]]:
    """Pull out <u>...</u> inners so spacing regexes don't break markup."""
    held: list[str] = []

    def keep(m: re.Match) -> str:
        held.append(m.group(1))
        return f"@@U{len(held) - 1}@@"

    return re.sub(r"<u>([\s\S]*?)</u>", keep, text, flags=re.I), held


def restore_tags(text: str, held: list[str]) -> str:
    def put(m: re.Match) -> str:
        return f"<u>{held[int(m.group(1))]}</u>"

    return re.sub(r"@@U(\d+)@@", put, text)


def apply_spacing_fixes(t: str) -> str:
    t = undo_false_unicode_splits(t)
    for pat, rep in TOKEN_FIXES:
        t = re.sub(pat, rep, t)
    for pat, rep in JOIN_SPLITS:
        t = re.sub(pat, rep, t, flags=re.I)
    t = re.sub(r"\bregard\s+less\b", "regardless", t, flags=re.I)
    t = re.sub(r"\bth\s+is\b", "this", t)
    t = fix_missing_space_before_capital(t)
    t = fix_space_after_accented_name(t)
    t = fix_missing_space_after_sentence_punct(t)
    t = re.sub(r"[^\S\n]{2,}", " ", t)
    return t


def fix_missing_space_before_capital(text: str) -> str:
    """Insert a space in glued prose like SteveTrewick / howKing / inÇayönü / ÇayönüTepesi."""

    def repl_ascii(m: re.Match) -> str:
        start = m.start()
        # Preserve McName / MacName / DeName-style capitals.
        if start >= 1:
            prefix2 = text[start - 1 : start + 1]
            prefix3 = text[max(0, start - 2) : start + 1]
            if prefix2 in {"Mc", "mc"} or prefix3.lower() in {"mac", "de", "le", "la", "van", "von"}:
                return m.group(0)
        return f"{m.group(1)} {m.group(2)}"

    t = re.sub(r"([a-z])([A-Z][a-z]{2,})\b", repl_ascii, text)

    # ASCII lowercase glued to a non-ASCII uppercase letter: inÇayönü / ofÇayönü.
    # Do NOT match lowercase Latin-extended (ö, ü, ı) — that would split Çayönü.
    def ascii_to_unicode_upper(m: re.Match) -> str:
        ch = m.group(2)
        if ch.isalpha() and ch.isupper() and not ch.isascii():
            return f"{m.group(1)} {ch}"
        return m.group(0)

    t = re.sub(r"([a-z])(.)", ascii_to_unicode_upper, t)

    # Non-ASCII letter glued to an ASCII Titlecase word: ÇayönüTepesi.
    def unicode_to_ascii_title(m: re.Match) -> str:
        ch = m.group(1)
        if ch.isalpha() and not ch.isascii():
            return f"{ch} {m.group(2)}"
        return m.group(0)

    t = re.sub(r"(.)([A-Z][a-z]{2,})\b", unicode_to_ascii_title, t)
    # Glued middle initials: PhilippeE. / NiaS. / CharlesS.
    t = re.sub(r"([a-z])([A-Z]\.)", r"\1 \2", t)
    return t


def undo_false_unicode_splits(text: str) -> str:
    """Undo earlier over-eager splits inside names like 'Çay ön ü' / 'Alt ın ışık'."""
    # ASCII lowercase + space + lowercase Latin-extended should usually be one word.
    return re.sub(r"([a-z]) ([\u00DF-\u024F])", r"\1\2", text)


def fix_space_after_accented_name(text: str) -> str:
    """Insert a space when an accented name is glued to an English word: Achíis / Belpréoffered.

    Important: do NOT use re.IGNORECASE on a Unicode range — in Python that can make the
    range match ASCII letters and smash words like ``analysis``.
    """
    followers = (
        "is|are|was|were|been|being|has|have|had|does|did|"
        "tells?|told|offers?|offered|shows?|showed|includes?|included|"
        "villagers|people|says?|said|wrote|writes|makes?|made"
    )
    # Lowercase Latin-extended letter (typical name ending) + English follower.
    return re.sub(
        rf"([\u00DF-\u00F6\u00F8-\u00FF\u0101-\u024F])({followers})\b",
        r"\1 \2",
        text,
    )


def fix_missing_space_after_sentence_punct(text: str) -> str:
    """Fix 'end.Next' but keep e.g. / i.e. / U.S. / decimals / ellipses / .pdf paths."""

    def repl(m: re.Match) -> str:
        punct, nxt = m.group(1), m.group(2)
        i = m.start()
        if i > 0 and text[i - 1].isdigit() and nxt.isdigit():
            return m.group(0)
        # File extensions: Unanswered.pdf / figure.jpg
        rest = text[i + 1 : i + 1 + 8]
        if re.match(r"(?i)(pdf|png|jpe?g|gif|webp|svg|json|txt|csv)\b", rest):
            return m.group(0)
        window = text[max(0, i - 4) : i + 1]
        if re.search(r"(?i)\b(?:e\.g|i\.e|u\.s|a\.d|p\.m|a\.m|mr|mrs|ms|dr|prof|vs|etc|approx|fig|eq)\.$", window + punct):
            return m.group(0)
        if i > 0 and text[i - 1].isupper() and (i < 2 or not text[i - 2].islower()):
            return m.group(0)
        return f"{punct} {nxt}"

    return re.sub(r"([.!?])([A-Za-z])", repl, text)


def fix_text(text: str) -> str:
    if not text:
        return text
    t, held = protect_tags(text)
    t = apply_spacing_fixes(t)
    held = [apply_spacing_fixes(h) for h in held]
    return restore_tags(t, held)


def fix_value(value, key: str | None = None):
    # Never rewrite asset paths with sentence-spacing heuristics.
    if key in {"pdf", "pdfPreview", "figure", "image", "src"} and isinstance(value, str):
        return re.sub(r"\.\s+(pdf|png|jpe?g|gif|webp|svg)\b", r".\1", value, flags=re.I)
    if isinstance(value, str):
        return fix_text(value)
    if isinstance(value, list):
        return [fix_value(v) for v in value]
    if isinstance(value, dict):
        return {k: fix_value(v, k) for k, v in value.items()}
    return value


def main() -> None:
    questions = json.loads(DATA.read_text())
    before = json.dumps(questions, ensure_ascii=False)
    fixed = [fix_value(q) for q in questions]
    after = json.dumps(fixed, ensure_ascii=False)
    DATA.write_text(json.dumps(fixed, indent=2, ensure_ascii=False) + "\n")

    # Quick report
    def count(needle: str, blob: str) -> int:
        return len(re.findall(needle, blob))

    print("Wrote", DATA)
    print("inText remaining:", len(re.findall(r"\binText\b", after)))
    print("throughut remaining:", len(re.findall(r"throughut", after, flags=re.I)))
    print("deser tification remaining:", len(re.findall(r"deser\s+tification", after, flags=re.I)))
    print("proper ties remaining:", len(re.findall(r"proper\s+ties", after, flags=re.I)))
    print("in someway remaining:", len(re.findall(r"\bin someway\b", after)))
    print("howKing remaining:", len(re.findall(r"howKing", after)))
    print("bytes delta:", len(after.encode()) - len(before.encode()))


if __name__ == "__main__":
    main()
