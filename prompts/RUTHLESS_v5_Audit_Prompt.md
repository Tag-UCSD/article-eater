# RUTHLESS v5.0 — Article Eater Audit Prompt (Expert Panel)

## Panel
1) Lead Systems Designer (AI-heavy, distributed systems, queues, cost-aware orchestration)
2) UX/UI Guru (libraries/exploration, metadata literacy, staged processing UX, HITL integration)
3) Security Engineer (authn/z, key mgmt, rate-limits, audit trail, PII)
4) Database Architect (schemas, constraints, indexes, migrations, provenance)
5) Cost Management Lead (quota, prediction vs actual, caching, batching, free-tier strategy)

## Materials
- The zipped repo you are auditing (exactly as provided).
- Do **not** fabricate code. If missing, propose the *smallest correct patch*.

## Method
- Read docs first (Least-Cost plan; Triage/Synthesis/QC/Frontier policies; Wizard flow; Student brief).
- Map docs ↔ code (schemas, SQL, prompts, scripts, CI).
- For each domain, produce:
  - **Score (0–10)** and **GO/NO‑GO** for that domain.
  - **Top risks** with **severity** P1 (blocker) / P2 (important) / P3 (nice).
  - **Smallest patch** list (surgical PRs; file paths; 1–2 paragraphs each).
- As a panel, consolidate to a **single GO/NO‑GO** for Enterprise readiness.
- Output sections: Executive Summary; Domain Audits; Minimal Patch Plan; Risk Register; Open Questions.

## Hard Gates (fail = NO‑GO)
- No secure API key handling path (storage + use + masking + audit).
- No queue worker implementation path to execute L0/L1 jobs.
- No cost tracking path (predicted vs actual) surfaced to UI.
- Coverage gate set above current test coverage with no offset plan.
- No indexes/constraints to prevent duplicate Articles and orphaned evidence.

## Evidence Tags
When citing a file, use: `[file: <path>]` and if helpful, quote ≤15 words.

## Deliverables
- `docs/audits/RUTHLESS_v5_Audit_Report_<version>.md` with: scores, risks, patches, GO/NO‑GO.
- `docs/audits/GO_NO_GO_Summary_<version>.txt` one-line verdict + blockers.