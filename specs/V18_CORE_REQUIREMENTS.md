# Article Eater v18 — Core Requirements (Architecture & Semantics)

This document distills the **core, implementation-relevant specifications** for Article Eater v18.x (up to v18.4.3) from the various design, requirements, and analysis docs in the repo (CNfA requirements, hierarchy quick reference, enhancement analysis, paper analysis guide, release notes, queue/triage policies, etc.).

It is intended as the **single source of truth** for core behavior when evolving the system.  
Anything not explicitly relaxed here should be treated as a **hard constraint**.

---

## 1. Purpose & Scope

Article Eater is an **evidence synthesis and rules engine** for environmental / architectural interventions and their effects on outcomes (stress, anxiety, mood, cognition, etc.), designed to support:

- **High-recall literature triage** (don’t miss relevant papers).
- **Transparent extraction** of findings and mechanisms from primary studies.
- **Hierarchical rule construction**:
  - MICRO: specific operational measures (e.g., cortisol, HRV).
  - MESO: constructs (stress, anxiety, mood, attention, etc.).
  - MACRO: design principles / architectural-level rules.
- **Meta-review and BN handoff**:
  - Combine evidence across measures and papers.
  - Feed structured rules into downstream Bayesian / causal models.
- **Human-in-the-loop governance**:
  - Transparent Set of Support (SoS) for each rule.
  - Manual review paths for theoretical claims and contradictions.

The system must remain **explainable, auditable, and conservative about over-claiming**.

---

## 2. Core Data Model & Artifacts

### 2.1 Jobs and Pipelines

- A **job** represents a complete evidence synthesis pipeline instance.
- Each job has:
  - `job_id` (string/UUID).
  - Topic or query description.
  - Status (`NEW`, `TRIAGED`, `IN_PROGRESS`, `COMPLETE`, `FAILED`, etc.).
  - Timestamps (created, last_updated, completed).
  - Cost/usage summaries (API tokens, estimated spend).
- Job artifacts are persisted per job (often in job-specific dirs and/or DB tables):
  - `shortlist` (candidate papers).
  - `library` (accepted papers with metadata).
  - `evidence` (7-panel extraction outputs).
  - `rules` (hierarchical rules with support).
  - `bn_handoff` / rule frontier representation for downstream BN.

Jobs must be **append-only** in spirit (no silent destruction of intermediate artifacts).

---

### 2.2 Library / Papers

Each **paper** (within the library) must have at least:

- `paper_id` (internal identifier).
- Bibliographic metadata:
  - `title`, `authors`, `year`, `journal`, `doi` (when available).
  - `abstract`.
- Provenance:
  - `jobs_referenced` (list of job IDs where the paper appears).
  - `source` (e.g., Crossref, PubMed, manual upload).
- Tags / categories:
  - Topic tags, intervention type, outcome category, etc.
- Extraction-related fields:
  - `evidence_passages` (list of text snippets used in findings/rules).
  - `extraction_score` (0–1 summary of how well the paper has been processed).
  - `rules_count`, `evidence_count` or equivalent.

**Extraction score** must be computed as:

```python
# Maximum contribution capped at 1.0
# Up to 0.5 from rules
rule_score = min(rules_count / 5.0, 1.0) * 0.5

# Up to 0.3 from evidence passages
evidence_score = min(evidence_count / 8.0, 1.0) * 0.3

# Up to 0.2 from synthesis efficiency
if evidence_count > 0:
    synthesis_rate = rules_count / evidence_count
    synthesis_score = min(synthesis_rate / 0.5, 1.0) * 0.2
else:
    synthesis_score = 0.0

extraction_score = rule_score + evidence_score + synthesis_score  # in [0.0, 1.0]
2.3 Findings
A finding is a structured statement extracted from a paper, at the level of:

intervention → operational measure → direction/magnitude → population/context.

Findings include:

finding_id

paper_id (foreign key).

intervention (e.g., “curved walls”, “plants”, “natural light”).

operational_measure (e.g., cortisol, hrv_rmssd, stai_s, panas_negative).

construct (the psychological / physiological construct, e.g., stress, anxiety, mood, attention, etc.).

Outcome direction (increase/decrease/no change) and where possible effect size or standardized indication.

Study design metadata (RCT, quasi-experimental, cross-sectional, etc.).

Evidence passages (anchors back to text).

Quality flags (risk of bias, sample size adequacy, etc.) if available.

Findings are building blocks for rules and meta-analysis. They must be traceable back to specific passages in the paper.

2.4 Rules (Hierarchical)
Rules represent synthesized relationships between design factors and outcomes.

Each rule must have:

rule_id

level (micro / meso / macro)

Structure:

consequent (normalized construct/claim, e.g., “anxiety_reduction”).

antecedents (list of normalized conditions: “curved_walls”, “natural_light”, etc.).

Quantitative fields:

weight or confidence (0–1).

Possibly n_supporting_studies, n_contradictory_studies.

Context:

operational_measure (for micro rules).

population, setting (if specified).

Mechanistic information:

mechanism (e.g., “predictive_processing_fluency”, “motor_simulation”, “biophilic_response”).

Hierarchy links:

parent_rule_id (link to parent rule at a higher level).

Typing / classification:

rule_type or rule_level (micro, meso, macro).

Category tags (design principle, mechanism, outcome domain, etc.).

Hierarchy semantics:

Micro rules:

Link specific operational measures to constructs.

Example: “curved_walls → cortisol↓ (stress_reduction)” or “plants → HRV↑ (stress_reduction)”.

Meso rules:

Aggregate across micro measures to produce construct-level rules.

Example: “curved_walls → anxiety_reduction” integrating STAI-S, HR, cortisol, etc.

Macro rules:

Aggregate across meso rules and contexts to derive general design principles.

Example: “curved_architecture → positive_affect” or “biophilic_architecture → stress_reduction”.

There must be a coherent mapping from micro → meso → macro, reducing duplicate flat rules.

2.5 Links & BN Handoff
The rule system must support downstream Bayesian / causal modeling (BN).

A finding_links table (or equivalent structure) is required with:

sql
Copy code
link_type VARCHAR(20) NOT NULL CHECK(link_type IN ('CAUSAL', 'TAXONOMIC'))
Links specify relationships between nodes (rules, constructs, outcomes), including:

Causal links (design → mechanism → outcome).

Taxonomic links (micro/meso/macro roll-up, grouping into constructs).

BN handoff schemas must:

Provide variables, states, edges, and (where available) quantitative priors.

Preserve rule hierarchy and mechanism information.

3. Processing Pipelines
3.1 Guided Wizard Flow (High-Level)
The system’s conceptual pipeline follows the “Guided Wizard Flow (v18.3)”:

Define Topic

User describes topic; system suggests queries and previews cost.

Triage Scan (Abstracts)

High-recall triage over abstracts/metadata.

Present keep/drop decisions with rationales and a Recall Sampler.

Approve for Deep Processing

User sees predicted time & cost HUD; chooses which clusters/papers to send to deep extraction.

Results

Return 7-panel extraction outputs, clusters, proposed rules, contradictions.

Rule Inspector

Provide Set of Support, related rules, BN handoff, and expansion options.

Implementation does not need to follow this view exactly step-by-step, but pipeline stages and affordances must exist.

3.2 Triage Policy (High Recall)
From Triage_Policy_HighRecall_v18_3.md:

Goal: abstract-only triage recall ≥ 95%.

Minimize false negatives (discarding relevant papers).

Favor inclusion when in doubt.

Mechanics:

Use similarity scoring, topical clustering, and metadata.

Set a low threshold to keep borderline cases.

UI requirements (reflected in GUI spec):

Show keep/drop rationale: key terms, similarity evidence.

Provide a Recall Sampler:

Random 5–10% sample of discards for manual spot-check.

Exposes potential false negatives and calibrates thresholds.

Escalation:

Deeper processing (full-text extraction) is gated by:

Cluster importance.

User request.

QC failures.

System must not silently drop large swaths of papers without a path to audit.

3.3 Queue Policy
From Queue_Policy_v18_2_0.md:

Priorities:

priority=100 for user uploads / interactive jobs.

priority=10 for nightly expansions or background tasks.

Queue must:

Prefer high-priority jobs while not starving lower-priority tasks.

Support monitoring (status, progress, error states).

Jobs support pause/resume semantics conceptually (optional in initial implementation but consider in design).

3.4 Extraction & 7-Panel Prompts
From prompts in prompts/:

Extraction is organized via multi-pass “7-panel” pipelines:

Pass 1: sectioning / decomposition (identify key segments).

Pass 2: findings extraction (operational measures, effect direction, context).

Pass 3: mechanisms / limits / caveats.

Additional passes:

Clustering, contradiction detection, abstract overlap, rule synthesis, etc.

Requirements:

Each panel’s output must be machine-parseable (JSON-friendly).

Each finding/rule must reference its SoS:

Paper IDs.

Specific panel entries or passage IDs.

Prompts included in the repo are part of the spec; do not alter their semantics casually.

4. Confidence & Scoring Semantics
Even if not all implemented yet in code, v18 requires:

4.1 RCT Confidence
For RCT-based evidence:

python
Copy code
conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
score_N: normalized sample-size contribution (larger N → higher score).

score_p: strength of p-value evidence.

score_d: effect-size magnitude / stability.

Weights and formula must match exactly.

4.2 Meta-Analytic Confidence
For meta-analytic aggregates:

python
Copy code
conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
score_k: number of studies (quantity).

score_CI: confidence interval tightness (precision).

score_I2: heterogeneity penalty/inversion (consistency).

Weights and formula must match exactly.

4.3 Theoretical Support
For purely theoretical claims (no direct empirical backing):

python
Copy code
def calculate(self, finding, papers):
    return -1.0  # MANUAL_REVIEW_REQUIRED
-1.0 is a sentinel value, not a low confidence.

This signals that human review is required and the system must not treat this as regular numeric support.

5. Governance & Quality Control
From RUTHLESS prompts, QC checklists, and governance notes:

High-level requirements:

All major flows must be auditable:

Clear logs of what was run, on which data, with which prompts.

No “magical” transformations; users should see:

Intermediate artifacts (shortlist, evidence, clusters).

Rationale for triage and rules.

LLM outputs must be checked against:

QC checklists (e.g., Extraction_QC_Checklist_v18_3.md).

Governance rules in governance_kit/.

LLM usage:

Should be prompt-driven, spec-following, and non-destructive to existing artifacts unless explicitly requested.

New code must not break:

Finding-to-rule traceability.

BN handoff semantics.

link_type constraints.

6. Security & Credentials
From v18.4 release notes:

Student / client API keys are never stored in plaintext.

Architecture:

Keys are encrypted (e.g., via Fernet) before persistence.

Only decrypted in memory for outbound API calls.

Any additional external credentials must follow the same pattern:

Environment-based configuration.

No secrets in source-controlled files.

7. Non-Goals / Anti-Requirements
Do not revert to flat rule lists without hierarchy.

Do not silently drop papers or rules without:

Audit trail.

QC / recall sampling.

Do not encode “magic weights” outside the specified confidence formulas.

Do not collapse mechanisms into vague text; mechanism fields must remain structured and queryable.

8. Implementation Guidance
When implementing new features or refactoring:

Preserve invariants from this spec (schema semantics, confidence formulas, link types).

Align with triage and queue policies (high recall, priority fairness).

Expose SoS and evidence trail for every rule or synthesized claim.

Keep governance kit and prompts as constraints, not optional suggestions.

If any necessary change would violate this document, update the spec explicitly and justify the change before modifying code.


