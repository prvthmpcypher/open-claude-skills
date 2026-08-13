# Changelog

Versioning note: earlier releases used two conflicting schemes (`v0.1`/`v0.2`/`v0.3` in changelogs and commits, `v2.0` in the README). Everything published so far is treated as pre-1.0. The current state is **v0.9**; the library will move to semver `v1.0.0` when remediation and plugin packaging are complete.

## v1.0.0 — August 2026

First release where the quality claim is true, and the first that is installable.

- **All 315 skills remediated.** 30 import stubs authored, 281 wrong-domain QA checklists replaced with domain-appropriate ones from `taxonomy/checklists.yaml`, all 315 descriptions rewritten to fit inside the ~250-character listing limit with the trigger clause visible, 13 unreachable reference files linked, 11 missing titles added. `scripts/validate.py` reports zero findings.
- **Overlapping skills now name each other.** `financial-analyst` points at `fp-and-a-analyst` and vice versa, so routing between similar skills is deliberate. Enforced by `scripts/overlap.py --regress`.
- **Installable as a plugin marketplace.** `.claude-plugin/marketplace.json` here lists all 12 category repos as separate plugins, each with its own `plugin.json`. `npx skills` reads the same manifests, so Codex, Cursor, Gemini CLI and 70+ other agents work without a custom installer.
- **Hub renamed** from `open-claude-skills` to `skillary`.
- **Generated, not hand-maintained**: the README index, `skill-router`'s reference index, all 13 manifests and all 315 `.skill` bundles are built by scripts in `scripts/`.
- Version scheme reset. Everything before this was pre-1.0 regardless of what it was labelled.

## v0.9 — August 2026

Corrections to the release previously labelled "v2.0: Full audit modernization — 315 production-grade skills". A file-level audit of all 315 `SKILL.md` files found that label was not accurate.

- The README no longer claims v2.0 quality standards that were never enforced. It now carries a **Status — known issues** section listing the real state.
- Removed `AUDIT.md`. It was a pre-remediation snapshot committed as if current: it reported 303 skills against the README's 315, flagged 23 skills that no longer exist, listed 12 of its 14 "missing" gap skills as absent when they had already been built, and included a "13 Hardcoded Paths / Secret Patterns" table that re-checking showed to be a false positive (the one flagged path, `/home/node/.n8n`, is a legitimate Docker volume). No credentials, tokens or personal paths exist in any of the 315 files.
- Fixed the install instructions. They previously read `cp -R skills/<skill-id> …` from a repo that has no `skills/` directory, so they failed verbatim for anyone who cloned the hub. They now start from the category repo and cover Claude Code, Codex CLI, Gemini CLI and Cursor paths.
- Added `skills-meta` to the `CONTRIBUTING.md` repo table (it listed 11 of 12 repos).
- Added `.gitattributes` across the hub and all 12 category repos. All 315 files were CRLF with no normalisation, so any non-Windows contributor produced whole-file diffs.

Still open, tracked for v1.0.0: 30 import-stub skills, 281 wrong-domain QA checklists, 228 over-length descriptions, `skill-router`'s stale index, `skill-linter`'s unmet `NOTE.md` convention, plugin manifests, and CI validation. One skill from the old gap analysis remains unbuilt: `cost-finops-engineer`.

## v0.2 — July 2026

- Total skill count corrected: 319 -> 342 (index had drifted from what the category repos actually contained)
- Developer count corrected: 82 -> 88
- Business count corrected: 26 -> 29
- Marketing, Specialized, Design, Game Dev, Sales & Support, Finance counts synced to their repos' actual skill folders
- Added 29 previously-undocumented or newly-added skills to the full skill index across 11 category tables:
  `ci-cd-pipeline-builder`, `iac-provisioner`, `citation-formatter`, `budget-expense-auditor`,
  `cap-table-fundraising-modeler`, `meta-ads-copywriter`, `fitness-nutrition-planner`, `screenplay-writer`,
  `android-developer`, `ios-developer`, `graphql-api-designer`, `load-testing-engineer`,
  `dependency-upgrade-auditor`, `board-deck-builder`, `vendor-procurement-manager`, `churn-analyst`,
  `renewal-strategist`, `conversion-rate-optimizer`, `influencer-outreach-strategist`, `pinterest-strategist`,
  `crypto-tax-specialist`, `insurance-actuary-analyst`, `game-monetization-designer`, `playtest-feedback-analyzer`,
  `hiring-plan-org-chart-builder`, `regulatory-compliance-officer`, `logo-brand-mark-designer`,
  `motion-graphics-producer`, `print-packaging-designer`
- Added `skills-meta` to the category table with a proper repo link (was listed without one)
- Added CHANGELOG.md and CODE_OF_CONDUCT.md to this repo (were missing)

## v0.1 — July 2026

- Initial public hub linking all category repositories
- MIT License
