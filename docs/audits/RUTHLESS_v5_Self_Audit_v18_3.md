# RUTHLESS v5 Audit — Self‑Run — v18.3 — 2025-11-14 18:42

## Executive Summary
The design scaffolding is strong (cost‑aware L0–L5, schemas/SQL, governance). Enterprise GO is blocked by missing execution paths for queues, API key handling, and cost tracking. UX is specified but not implemented. Minimal patches are small and surgical.

## Domain Audits (Scores, Risks, Patches)

### 1) Lead Systems Designer — Score **6.5/10** — **NO‑GO**
- **Risks**: (P1) no worker executing `processing_queue`; (P1) no PDF parse path; (P2) no frontier watcher; (P2) cache keys undefined.
- **Patches**:
  1. `app/worker.py`: in‑proc loop polling `processing_queue` for `abstract_cluster` → call `scripts/triage_score.py`; write results & update status.
  2. `app/pdf_ingest.py`: minimal PDF text extractor (pdfminer) + stub sectioning.
  3. `scripts/cache_keys.md`: spec for `(provider,model,prompt_hash,doc_hash)` cache keys.

### 2) UX/UI Guru — Score **7.5/10** — **CONDITIONAL GO**
- **Risks**: (P2) no screen stubs; (P2) no “why kept/dropped” drawer; (P3) no wizard prototype.
- **Patches**:
  1. `frontend/Library.html` static stub: facets + table/cards + “why kept/dropped” drawer.
  2. `frontend/RuleInspector.html` static stub: tabs (Evidence/Related/BN), contradictions & confidence widgets.
  3. `frontend/Wizard.html` static 5-step flow; reuse existing tokens only.

### 3) Security — Score **5.5/10** — **NO‑GO**
- **Risks**: (P1) no API key storage path; (P1) no audit log; (P2) no rate limit; (P2) no RBAC; (P3) logs may contain PII.
- **Patches**:
  1. `app/security/keys.py`: Fernet-encrypt per-user keys with env MASTER_KEY; mask on read.
  2. `app/middleware/audit.py`: request/actor/action audit records; redact known secrets.
  3. `app/middleware/ratelimit.py`: naive token bucket on write endpoints.

### 4) Database — Score **7.0/10** — **CONDITIONAL GO**
- **Risks**: (P2) missing unique indexes on `articles(doi, corpus_id)`; (P2) possible orphans in `rule_evidence`; (P3) migrations not defined.
- **Patches**:
  1. `db/sql/013_indexes.sql`: unique indexes; FK ON DELETE behaviors.
  2. `db/README.md`: migration procedure (psql + version stamps).

### 5) Cost Management — Score **6.0/10** — **NO‑GO**
- **Risks**: (P1) no telemetry→`api_usage_events`; (P2) HUD not fed; (P3) no provider limits monitor.
- **Patches**:
  1. `app/middleware/costs.py`: accept `x-model`, `x-tokens-in/out`, `x-cost` headers from clients; persist; compute predicted vs actual deltas.
  2. `app/routes/usage.py`: simple `/usage/me` for students; `/usage/admin` aggregate.

## Minimal Patch Plan (1–2 days of work)
1) Worker loop + PDF ingest stubs (P1).  
2) API key encrypt/store/use + audit log (P1).  
3) Cost middleware + `/usage` endpoints + wire HUD (P1/P2).  
4) Indexes + migration note (P2).  
5) Static UI stubs for Library, Rule Inspector, Wizard (P2).

## Risk Register
- **Data Quality**: abstract-only clustering may mis-group short abstracts → mitigate with fallback embeddings.
- **Cost Spikes**: student keys misconfigured → enforce per-user quotas and defaults.

## GO/NO‑GO
- **Enterprise**: **NO‑GO** until P1s above land.
- **Governance**: GO.
