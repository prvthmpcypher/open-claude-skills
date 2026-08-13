"""Replace a stub placeholder block with authored instructions.

30 skills shipped with a fetch-failure placeholder where their instructions
should be. This swaps that block for real content, leaving the rest of the file
alone - the H1, the domain checklist and the anti-patterns are already correct.

Input is a YAML map of `skill-id: |` markdown blocks.

    python scripts/set_bodies.py work/bodies-specialized.yaml
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

# The placeholder: a blockquote, a stray `**` on its own line, and a re-import
# note. Also drop the generic `## Output format` and `## Critical rules`
# sections that came with it - authored content replaces both.
# The tail sentence has two phrasings across the 30 files - "Re-import exact
# content when GitHub..." (16) and "When GitHub connection or raw access is
# available, replace this page body..." (12). Match both, or one variant is left
# behind in the finished skill.
STUB_BLOCK = re.compile(
    r"^> Full .*?could not be fetched.*?$\n"
    r"(?:^\*\*$\n)?"
    r"(?:^(?:.*?[Rr]e-import.*?|When GitHub connection.*?)$\n)?",
    re.M | re.S,
)
STUB_TAIL = re.compile(
    r"^(?:Re-import exact content when GitHub.*?|When GitHub connection or raw access.*?)$\n?",
    re.M,
)
GENERIC = re.compile(
    r"^## (Output format|Critical rules)\b.*?(?=^## |\Z)",
    re.M | re.S,
)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    new = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
    by_slug = {s.slug: s for s in iter_skills()}

    unknown = sorted(set(new) - set(by_slug))
    if unknown:
        print("Unknown skill ids:", ", ".join(unknown), file=sys.stderr)
        return 1

    written = 0
    for slug, content in new.items():
        skill = by_slug[slug]
        body = STUB_BLOCK.sub("", skill.body)
        body = STUB_TAIL.sub("", body)
        body = GENERIC.sub("", body)

        # Insert authored content directly after the H1.
        lines = body.splitlines()
        head = next((i for i, l in enumerate(lines) if l.startswith("# ")), -1)
        if head == -1:
            print(f"{slug}: no H1 to anchor to", file=sys.stderr)
            return 1
        rest = "\n".join(lines[head + 1:]).lstrip("\n")
        body = f"{lines[head]}\n\n{content.strip()}\n\n{rest}".rstrip("\n") + "\n"

        (skill.path / "SKILL.md").write_text(
            f"---\n{skill.frontmatter}\n---\n{body}", encoding="utf-8"
        )
        written += 1

    print(f"wrote {written} bodies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
