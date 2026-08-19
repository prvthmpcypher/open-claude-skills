# Contributing to skillary

This hub only indexes category repositories. Add or edit skills in the matching `skills-*` repo — not here.

Maintainer: **Poorvith M P** · v0.9 · August 2026

See each category repo's `CONTRIBUTING.md` for skill-creator rules.

## Adding a new skill

1. Go to the matching category repo (e.g. [skills-developer](https://github.com/poorvith-mp/skills-developer))
2. Follow that repo's `CONTRIBUTING.md`
3. Run the validator before opening a PR — CI runs the same checks:

   ```bash
   python scripts/validate.py --repo <category>
   ```

4. Do **not** edit the index in `README.md` by hand. It is generated:

   ```bash
   python scripts/build_index.py --write
   ```

## What the validator enforces

The rule that matters most: **descriptions must be under 250 characters with the trigger clause inside them.** Claude truncates the description at roughly that point when deciding whether to load a skill, so a trigger sitting at the end of a 400-character description does nothing.

It also checks that `name` matches the folder, that no description triggers on the skill's own name, that reference files are linked from the body, and that the verification checklist matches the skill's domain (`taxonomy/checklists.yaml`).

If a new skill overlaps an existing one, its description must name the sibling. `python scripts/overlap.py` finds the collisions and prints the phrases they collide on.

## Repo links

| Repo | URL |
|------|-----|
| skills-developer | https://github.com/poorvith-mp/skills-developer |
| skills-marketing | https://github.com/poorvith-mp/skills-marketing |
| skills-specialized | https://github.com/poorvith-mp/skills-specialized |
| skills-design | https://github.com/poorvith-mp/skills-design |
| skills-business | https://github.com/poorvith-mp/skills-business |
| skills-gamedev | https://github.com/poorvith-mp/skills-gamedev |
| skills-education | https://github.com/poorvith-mp/skills-education |
| skills-personal | https://github.com/poorvith-mp/skills-personal |
| skills-writing | https://github.com/poorvith-mp/skills-writing |
| skills-sales-support | https://github.com/poorvith-mp/skills-sales-support |
| skills-finance | https://github.com/poorvith-mp/skills-finance |
| skills-meta | https://github.com/poorvith-mp/skills-meta |
