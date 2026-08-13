"""Replace the wrong-domain QA checklists and anti-patterns.

281 skills carry a software-engineering verification checklist and 255 carry
software-engineering anti-patterns, applied regardless of domain - every finance
and education skill included. This replaces those with domain-appropriate
content from taxonomy/checklists.yaml.

The safety property that matters: this keys on CONTENT, never on the section
heading. 313 skills carry the `## Verification` heading but only 281 carry the
boilerplate; the other 32 are hand-written and domain-correct, and they are the
best content in the library. Same for anti-patterns: 290 headings, 255
boilerplate, 35 hand-written. A heading-keyed rewriter would destroy 67 good
sections. Anything not matching the fingerprint is left alone and logged.

Usage:
    python scripts/fix_sections.py --scan            # decision table, no writes
    python scripts/fix_sections.py --diff            # unified diff, no writes
    python scripts/fix_sections.py --apply --repo finance
    python scripts/fix_sections.py --apply --all
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from skillary import iter_skills  # noqa: E402

CODE_CHECKLIST_FP = "Code compiles cleanly and passes all automated tests"
CODE_ANTIPATTERN_FP = "NEVER bypass automated tests or typecheckers"

VERIFICATION_TITLE = "## Verification & Quality Checklist"
ANTIPATTERN_TITLE = "## Anti-Patterns & Constraints"

TAXONOMY = Path(__file__).resolve().parent.parent / "taxonomy"


def load_taxonomy() -> tuple[dict, dict, dict]:
    checklists = yaml.safe_load((TAXONOMY / "checklists.yaml").read_text(encoding="utf-8"))
    mapping = yaml.safe_load((TAXONOMY / "domain_map.yaml").read_text(encoding="utf-8"))
    return checklists["archetypes"], mapping["defaults"], mapping.get("overrides") or {}


def archetype_for(skill, defaults: dict, overrides: dict) -> str:
    return overrides.get(skill.slug) or defaults[skill.repo]


def find_section(body: str, title_prefix: str) -> tuple[int, int] | None:
    """Span of a section, from its heading to the next H2 or EOF.

    Sub-headings travel with their parent: several design and developer skills
    put an `### Accessibility` block inside their verification section.
    """
    pattern = re.compile(rf"^##\s*(?:[^\w\s]*\s*)?{title_prefix}[^\n]*$", re.M | re.I)
    match = pattern.search(body)
    if not match:
        return None
    nxt = re.compile(r"^##\s", re.M).search(body, match.end())
    return match.start(), (nxt.start() if nxt else len(body))


def render(title: str, items: list[str], checkbox: bool) -> str:
    lines = [title, ""]
    lines += [f"- [ ] {i}" if checkbox else f"- {i}" for i in items]
    return "\n".join(lines) + "\n\n"


def plan_for(skill, archetypes: dict, defaults: dict, overrides: dict):
    """Return (new_body, list of action codes). Pure function of the input."""
    body = skill.body
    arch = archetype_for(skill, defaults, overrides)
    spec = archetypes[arch]
    actions = []

    # --- anti-patterns first: editing it does not move the verification span ---
    span = find_section(body, "Anti-Patterns")
    alt = find_section(body, "What NOT to do")
    if span and CODE_ANTIPATTERN_FP in body[span[0]:span[1]]:
        body = body[:span[0]] + render(ANTIPATTERN_TITLE, spec["anti_patterns"], False) + body[span[1]:]
        actions.append(f"antipatterns:replaced:{arch}")
    elif span:
        actions.append("antipatterns:preserved")
    elif alt:
        # Same purpose, different heading. Keep the author's content, normalise
        # the heading so the section is findable.
        head_end = body.index("\n", alt[0])
        body = body[:alt[0]] + ANTIPATTERN_TITLE + body[head_end:]
        actions.append("antipatterns:renamed")
    else:
        body = body.rstrip() + "\n\n" + render(ANTIPATTERN_TITLE, spec["anti_patterns"], False)
        actions.append(f"antipatterns:inserted:{arch}")

    span = find_section(body, "Verification")
    if span and CODE_CHECKLIST_FP in body[span[0]:span[1]]:
        body = body[:span[0]] + render(VERIFICATION_TITLE, spec["verification"], True) + body[span[1]:]
        actions.append(f"verification:replaced:{arch}")
    elif span:
        actions.append("verification:preserved")
    else:
        anti = find_section(body, "Anti-Patterns")
        block = render(VERIFICATION_TITLE, spec["verification"], True)
        at = anti[0] if anti else len(body.rstrip()) + 1
        body = body[:at].rstrip() + "\n\n" + block + body[at:].lstrip("\n")
        actions.append(f"verification:inserted:{arch}")

    # Section blocks end in a blank line so they separate cleanly mid-document;
    # at EOF that leaves a stray trailing blank. Normalise to exactly one.
    return body.rstrip("\n") + "\n", actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--repo")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--sample", type=int, default=0)
    args = parser.parse_args()

    archetypes, defaults, overrides = load_taxonomy()

    skills = list(iter_skills())
    if args.repo:
        target = args.repo if args.repo.startswith("skills-") else f"skills-{args.repo}"
        skills = [s for s in skills if s.repo == target]
    elif args.apply and not args.all:
        print("Refusing to apply across every repo without --all.", file=sys.stderr)
        return 2

    tally: Counter[str] = Counter()
    preserved: list[str] = []
    changed = 0
    shown = 0

    for skill in skills:
        if skill.name is None:
            tally["skipped:no-frontmatter"] += 1
            continue
        new_body, actions = plan_for(skill, archetypes, defaults, overrides)
        for action in actions:
            tally[action] += 1
            if action.endswith(":preserved"):
                preserved.append(f"{skill.rel}  ({action.split(':')[0]})")

        if new_body == skill.body:
            continue
        changed += 1

        if args.diff or (args.sample and shown < args.sample):
            shown += 1
            diff = difflib.unified_diff(
                skill.body.splitlines(), new_body.splitlines(),
                f"a/{skill.rel}", f"b/{skill.rel}", lineterm="",
            )
            print("\n".join(diff))
            print()

        if args.apply:
            path = skill.path / "SKILL.md"
            # Rebuild the whole file so the frontmatter block is byte-identical:
            # the `>-` folded scalars must not be reflowed.
            path.write_text(f"---\n{skill.frontmatter}\n---\n{new_body}", encoding="utf-8")

    width = max((len(k) for k in tally), default=10)
    print(f"\n{len(skills)} skills examined, {changed} would change\n")
    for action, count in sorted(tally.items()):
        print(f"  {action:<{width}}  {count}")

    # "Preserved" means "did not match the boilerplate fingerprint". Before the
    # codemod runs that is exactly the set of hand-written sections (67). After
    # it runs, replaced sections no longer match either, so everything reports
    # as preserved - which is correct for idempotency but useless as a record.
    # Only write the file when the number is still meaningful.
    if preserved and changed:
        out = Path(__file__).resolve().parent.parent / "work" / "preserved.txt"
        out.parent.mkdir(exist_ok=True)
        out.write_text("\n".join(sorted(preserved)) + "\n", encoding="utf-8")
        print(f"\n{len(preserved)} sections left untouched -> work/preserved.txt")
    elif preserved:
        print(f"\n{len(preserved)} sections already conform (nothing left to replace)")

    if args.apply:
        print(f"\nwrote {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
