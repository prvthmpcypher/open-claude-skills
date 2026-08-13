"""Two mechanical body fixes: a missing opening H1, and unreachable references.

Some bodies open with persona prose or a mid-document heading, so the file has
no title. Others ship a `references/` file that the body never mentions - and
agents load reference files only when the SKILL.md points at them, so those
files can never be read.

    python scripts/fix_bodies.py            # report
    python scripts/fix_bodies.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from build_index import title_for  # noqa: E402
from skillary import iter_skills  # noqa: E402

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def add_h1(skill, body: str) -> tuple[str, bool]:
    first = next((line for line in body.splitlines() if line.strip()), "")
    if first.lstrip().startswith("# "):
        return body, False
    return f"# {title_for(skill.slug)}\n\n{body.lstrip()}", True


def link_references(skill, body: str) -> tuple[str, bool]:
    refs = sorted((skill.path / "references").glob("*.md")) if (skill.path / "references").is_dir() else []
    if not refs:
        return body, False

    linked = set(MD_LINK.findall(body)) | set(re.findall(r"references/[\w.-]+", body))
    missing = [r for r in refs if not any(f"references/{r.name}" in link for link in linked)]
    if not missing:
        return body, False

    # Append rather than guess a position: these are load-on-demand lookups, so
    # the end of the file is where they belong and where they read naturally.
    lines = ["## References", "", "Load these only when the task needs them:", ""]
    lines += [f"- [references/{r.name}](references/{r.name})" for r in missing]
    return body.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n", True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    h1s = refs = 0
    for skill in iter_skills():
        if skill.name is None:
            continue
        body, added_h1 = add_h1(skill, skill.body)
        body, added_refs = link_references(skill, body)
        if not (added_h1 or added_refs):
            continue

        h1s += added_h1
        refs += added_refs
        what = ", ".join(x for x in ["H1" if added_h1 else "", "references" if added_refs else ""] if x)
        print(f"  {skill.rel}: {what}")

        if args.apply:
            (skill.path / "SKILL.md").write_text(
                f"---\n{skill.frontmatter}\n---\n{body}", encoding="utf-8"
            )

    print(f"\n{h1s} titles added, {refs} reference sections added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
