#!/usr/bin/env python3
"""Assert Educator Bank Advanced Math choice/equation policy after imports.

Content fixes live in mathQuestions.json from the PDF cross-check pass.
This helper only flags regressions and re-wires the two allowed image-choice
questions (graph / table answers).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/mathQuestions.json"
IMAGE_CHOICE_OK = {"e9aed539", "1ee962ec"}


def main() -> None:
    qs = json.loads(DATA.read_text(encoding="utf-8"))
    touched = 0
    for q in qs:
        if q.get("pool") != "E. Bank" or q.get("domain") != "Advanced Math":
            continue
        changed = False
        if q.get("equations"):
            q.pop("equations", None)
            changed = True
        prompt = q.get("prompt") or ""
        if "{{eq:" in prompt:
            print(f"warn: eq slots still in {q['id']}")
        if q.get("type") == "mc" and q["id"] not in IMAGE_CHOICE_OK:
            for c in q.get("choices") or []:
                if c.get("image") and not (c.get("text") or "").strip():
                    print(f"warn: image-only choice on {q['id']} — needs text fix")
        if q["id"] in IMAGE_CHOICE_OK:
            qid = q["id"]
            q["choices"] = [
                {"image": f"/qbank/math/choices/{qid}_{i}.jpg"} for i in range(4)
            ]
            changed = True
        if changed:
            touched += 1
    DATA.write_text(json.dumps(qs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"checked Educator Advanced Math; touched {touched}")


if __name__ == "__main__":
    main()
