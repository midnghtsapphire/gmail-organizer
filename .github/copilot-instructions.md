# Copilot Instructions

Use `AGENTS.md` as the source of truth for repository instructions.

`AGENTS.md` must remain a standalone file for this repository. Do not replace it with, or symlink it to, `.github/copilot-instructions.md`; this file is supplemental and must stay consistent with `AGENTS.md`.

## S2M / Revvel auto-processing convention

When an issue or WR title/body contains `s2m` (case-insensitive), treat it as a ship-to-market request and run the work through revvel-standards in one iteration.

Minimum revvel-standards output for this repository:
- README updates (what the repo does + current usage)
- CHANGELOG.md
- DEPLOYMENT_GUIDE.md
- GO_TO_MARKET.md
- BRAND_GUIDELINES.md
- SECURITY.md
- baseline validation scripts/commands documented and run where applicable
