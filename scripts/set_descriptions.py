"""Splice rewritten descriptions into SKILL.md frontmatter.

Input is a YAML map of `skill-id: new description`. Everything else about the
file is left byte-identical - only the `description:` block is replaced.

There is no gate subcommand here: validate.py already checks length, trigger
presence, boilerplate and self-reference. Run it afterwards.

    python scripts/set_descriptions.py work/descriptions.yaml
    python scripts/validate.py --repo finance
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from skillary import iter_skills  # noqa: E402

# `description:` through the end of its indented block.
BLOCK = re.compile(r"^description:.*?(?=^\S|\Z)", re.M | re.S)


def wrap(text: str, width: int = 96) -> str:
    """Emit a `>-` folded block. Folded scalars join lines with one space, so
    every continuation line must be indented and carry no trailing space."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    body = "\n".join(f"  {line}" for line in lines)
    return f"description: >-\n{body}\n"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    new = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
    by_slug = {s.slug: s for s in iter_skills()}

    missing = sorted(set(new) - set(by_slug))
    if missing:
        print("Unknown skill ids:", ", ".join(missing), file=sys.stderr)
        return 1

    written = 0
    for slug, desc in new.items():
        skill = by_slug[slug]
        desc = " ".join(str(desc).split())
        frontmatter = BLOCK.sub(wrap(desc), skill.frontmatter + "\n").rstrip("\n")
        path = skill.path / "SKILL.md"
        path.write_text(f"---\n{frontmatter}\n---\n{skill.body}", encoding="utf-8")

        check = yaml.safe_load(frontmatter)
        assert check["description"] == desc, f"{slug}: round-trip changed the text"
        assert check["name"] == skill.name, f"{slug}: name was disturbed"
        written += 1

    print(f"wrote {written} descriptions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
