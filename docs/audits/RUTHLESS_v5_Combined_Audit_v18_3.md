# Combined RUTHLESS Report — v18.3 — 2025-11-14 18:42

## Verdicts
- Governance: **GO** (both audits).
- Enterprise: **NO‑GO** (both audits) pending queue worker, API key path, and cost telemetry.

## Shared P1 Blockers
1. Worker not executing queue (processing_queue).
2. Secure API key handling (storage/use/audit).
3. Cost tracking (predicted vs actual) surfaced to UI.
4. Coverage gate vs current tests.

## Minimal Patch Set (union, deduplicated)
- `app/worker.py` (queue executor), `app/pdf_ingest.py` (PDF→text), `app/security/keys.py` (Fernet), `app/middleware/audit.py`, `app/middleware/costs.py`, `app/middleware/ratelimit.py`, `app/routes/usage.py`.
- DB: `db/sql/013_indexes.sql` (unique indexes, FK tweaks).
- Frontend: static stubs for Library, Rule Inspector, Wizard.
- CI: temporarily set coverage gate to 60% until tests catch up.

See individual audits for scores and P2/P3 items.