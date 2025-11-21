# RUTHLESS Self‑Audit — v18.3 — 2025-11-14 18:42

## Scope
Static audit of the repository content (no external calls). Checks: governance, security posture, cost mgmt, data model, queue, prompts, UX specs, tests/CI.

## Snapshot
- Files: 148
- Schemas: 6
- SQL files: 3
- Tests: 3
- CI present: True
- CodeQL present: False

## Findings

### P1 (Blockers)
1. **Execution layer not wired**: No job runner connects `processing_queue` to actual workers (Celery/Redis or in‑proc). Queue exists only on paper.
2. **API key handling not implemented**: DB schemas for keys/usage exist but no endpoints, encryption-at-rest, or key-scoped permissions.
3. **Cost tracking not enforced**: `api_usage_events` table exists but no middleware to compute tokens/cost and persist events; Cost HUD not fed from backend.
4. **Coverage gate vs tests**: CI gate likely ≥80% while tests are minimal; this will fail CI and block merges.

### P2 (Important)
1. **Security baselines**: No rate limiting, no audit log, no RBAC/role enforcement shown; endpoints not inspected (FastAPI skeleton minimal).
2. **PDF pipeline**: 7‑panel prompts exist, but PDF ingestion/segmentation is not implemented; no OCR/parse path.
3. **Triage scorer**: `triage_score.py` is placeholder; needs TF‑IDF/embeddings and recall sampler hook.
4. **Rule frontier**: Triggers documented; no watcher job to compute similarity deltas and enqueue re‑synthesis.
5. **DB indexes & constraints**: Minimal indices; consider unique constraints on DOI/CorpusID and foreign key ON DELETE behaviors.

### P3 (Nice‑to‑have)
1. **UX prototypes**: Screens specced but not prototyped; no static HTML/React stubs to validate layout and HITL flow.
2. **Pedagogical “explain‑why”**: Mentioned in docs; needs copy blocks and UI components.
3. **Logging & observability**: JSON logging present in `app/main.py` but no request IDs, correlation IDs, or structured error taxonomy.

## Strengths
- Strong governance: `release.keep.yml`, `MANIFEST.sha256`, additive-only discipline, detailed docs.
- Clear L0→L5 least‑cost plan; multi‑pass extraction/QC/synthesis policy (Claude‑aligned) added.
- Schemas well‑scaffolded for BN handoff and SoS/evidence stance.

## GO / NO‑GO
- **Governance GO**: yes (repo hygiene, docs, audit trail).
- **Enterprise GO**: **NO‑GO** until P1 items are implemented.

## Minimal GO Patch (Recommended Δ)
1) Implement a simple in‑proc **worker loop** (poll `processing_queue`, run L0/L1 triage over abstracts, write results).  
2) Add **/profile/api-keys** endpoints with encryption-at-rest (e.g., Fernet + env master key) and per‑user scoping; redact in logs.  
3) Add **usage middleware** that accepts model+token usage estimates from the caller and persists to `api_usage_events`; wire HUD to this.  
4) Lower CI coverage gate to 60% until tests expand; add 3–5 integration tests around `/openapi.json`, `/queue`, `/rules/:id`.  
5) Add unique indexes on `articles(doi)`, `articles(corpus_id)` and stance constraints.
