#!/usr/bin/env python3
"""Repair R&W questions where passage body and question stem are swapped/merged.

Common failure modes from PDF extraction:
1. Only the first sentence lands in `passage`; the rest of the passage + stem
   sit in `prompt` (shows as mixed text in the question pane).
2. The stem is glued onto the end of `passage` while `prompt` is a placeholder.
3. Rhetorical Synthesis: "The student wants…" was moved into `passage`
   (it belongs in `prompt` with "Which choice most effectively…").
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data" / "readingQuestions.json"

# Stem that should start the question pane (not the passage).
STEM_RE = re.compile(
    r"(?:"
    r"Which (?:finding|choice|quotation|statement|detail|of the following)|"
    r"Based on (?:the )?(?:texts?|passage|table|graph|figure)|"
    r"According to (?:the )?(?:text|passage|table|graph|author|writer)|"
    r"As used in the text|"
    r"Taken together|"
    r"Assuming |"
    r"Information in the text|"
    r"What (?:does|is|can|would|choice)|"
    r"How (?:does|would|mainly|can)|"
    r"Why (?:does|is|might)|"
    r"The (?:writer|author) |"
    r"The student wants"
    r")",
    re.I,
)

SENTENCE_END_RE = re.compile(r'(?:[.!?…"”\'\)\]]|</u>)\s*$')
PLACEHOLDER_PROMPTS = {"", "select the best answer."}


def is_placeholder_prompt(prompt: str) -> bool:
    return (prompt or "").strip().lower() in PLACEHOLDER_PROMPTS


def repair_rhetorical(passage: str, prompt: str) -> tuple[str, str] | None:
    """Keep notes in passage; keep 'The student wants… Which choice…' in prompt."""
    m = re.search(r"(?P<want>The student wants[\s\S]*?)\s*$", passage)
    if m and re.match(r"^Which choice most effectively\b", prompt or "", re.I):
        return passage[: m.start("want")].rstrip(), (m.group("want").strip() + " " + prompt).strip()

    m = re.search(
        r"(?P<stem>The student wants[\s\S]*?Which choice most effectively[\s\S]*?\?)\s*$",
        passage,
        re.I,
    )
    if m and is_placeholder_prompt(prompt):
        return passage[: m.start("stem")].rstrip(), m.group("stem").strip()
    return None


def repair_stem_glued_to_passage(passage: str, prompt: str) -> tuple[str, str] | None:
    """Move a stem glued to the end of the passage into prompt (placeholder only)."""
    if not is_placeholder_prompt(prompt):
        return None
    m = STEM_RE.search(passage)
    if not m:
        return None
    # Prefer the last stem-like match near the end
    last = None
    for match in STEM_RE.finditer(passage):
        last = match
    if not last or last.start() < 40:
        return None
    prefix = passage[: last.start()].rstrip()
    stem = passage[last.start() :].strip()
    if not SENTENCE_END_RE.search(prefix):
        return None
    if "?" not in stem and not re.search(r"\bwhich\b", stem, re.I):
        return None
    return prefix, stem


def repair_passage_body_in_prompt(passage: str, prompt: str, skill: str) -> tuple[str, str] | None:
    """Move passage prose that was left in `prompt` back into `passage`."""
    prompt = prompt or ""
    passage = passage or ""
    m = STEM_RE.search(prompt)
    if not m or m.start() < 60:
        return None

    prefix = prompt[: m.start()].rstrip()
    stem = prompt[m.start() :].strip()
    if not prefix or not stem:
        return None
    if not SENTENCE_END_RE.search(prefix):
        return None

    # Avoid swallowing short clarifiers that belong with the stem.
    if len(prefix) < 60:
        return None

    # Don't append if passage already ends with the same text.
    if passage and prefix in passage:
        return passage, stem

    # Prefer joining when passage looks truncated (short) or clearly continues.
    joined = f"{passage} {prefix}".strip() if passage else prefix
    # Deduplicate accidental overlap at the join boundary.
    if passage:
        overlap = 0
        max_o = min(len(passage), len(prefix), 120)
        for n in range(max_o, 19, -1):
            if passage[-n:] == prefix[:n]:
                overlap = n
                break
        if overlap:
            joined = (passage + prefix[overlap:]).strip()

    return joined, stem


def repair_question(q: dict) -> bool:
    passage = q.get("passage") or ""
    prompt = q.get("prompt") or ""
    skill = q.get("skill") or ""
    before = (passage, prompt)

    if skill == "Rhetorical Synthesis":
        fixed = repair_rhetorical(passage, prompt)
        if fixed:
            passage, prompt = fixed

    fixed = repair_stem_glued_to_passage(passage, prompt)
    if fixed:
        passage, prompt = fixed

    fixed = repair_passage_body_in_prompt(passage, prompt, skill)
    if fixed:
        passage, prompt = fixed

    # Underlined claim should live in the passage pane, not the stem.
    if "<u>" in prompt and skill != "Words in Context" and "underlined" in (prompt + passage).lower():
        fixed = repair_passage_body_in_prompt(passage, prompt, skill)
        if fixed:
            passage, prompt = fixed

    if (passage, prompt) == before:
        return False
    q["passage"] = passage
    q["prompt"] = prompt
    return True


def main() -> None:
    questions = json.loads(DATA.read_text())
    changed = []
    for q in questions:
        if repair_question(q):
            changed.append(q["id"])
    DATA.write_text(json.dumps(questions, indent=2, ensure_ascii=False) + "\n")
    print(f"Repaired {len(changed)} questions")
    if changed:
        print(", ".join(changed[:40]) + ("…" if len(changed) > 40 else ""))


if __name__ == "__main__":
    main()
