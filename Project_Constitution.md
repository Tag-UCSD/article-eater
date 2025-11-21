# Project Constitution — Article Eater
Purpose: Maintain a stable, contract-first, hard-modular repository that extracts evidence-backed rules from scientific articles for CNfA.

Non-negotiables:
- No deletions of kept files; obsolete files are moved under `quarantine/YYYY-MM-DD/` via PRs.
- All public-surface changes require micro‑contract updates and a signed ledger delta.
- Every release ships both: (a) ZIP repo, (b) concatenated TXT with `deconcat.py` and SHA256 manifest.
- Governance kit files are immutable “kept”: listed in `release.keep.yml` and guarded by CI.

Change control:
1) Contract-first: propose interface deltas; update `contracts/` and `public_surface_ledger.json`.
2) Open a PR; CI gates (governance, orphan sweep, ledger delta) must pass.
3) If replacing files, place old files under `quarantine/YYYY-MM-DD/` and update `release.keep.yml` notes.

Security & secrets:
- No secrets in repo. Use `.env` (template only), GitHub secrets, or KMS. CI enforces checks for leaked keys.

Release policy:
- Tag: vMAJOR.MINOR.PATCH+date-time. Include MANIFEST.sha256 with per-file hashes and repo ZIP size.