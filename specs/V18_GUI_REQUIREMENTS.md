## `specs/V18_GUI_REQUIREMENTS.md`

```markdown
# Article Eater v18 — GUI Requirements

This document consolidates GUI and workflow requirements from:

- `Article_Eater_GUI_Audit_Complete.md`
- `docs/GUI_Spec_Library_and_RuleInspector_v18_2_0.md`
- `docs/Wizard_Flow_v18_3.md`
- `docs/UX_Additions_v18_3.md`
- `docs/Student_API_Help_Modal.md`
- `docs/Wizard_Flow_v18_3.md`
- `docs/Queue_Policy_v18_2_0.md`
- `docs/Triage_Policy_HighRecall_v18_3.md`
- `Paper_Analysis_Implementation_Guide.md`
- release notes and enhancement analyses

It defines the **target front-end behavior** and **API expectations** for v18.x.

---

## 1. Global Principles

1. **Single coherent workflow**
   - Users should understand where they are in the pipeline:
     - Ingest → Jobs → Shortlist → Evidence → Rules → BN / export.
2. **Persistent navigation**
   - Global nav bar visible on all main pages:
     - `Ingest | Jobs | Library | Rule Inspector | Monitor | Settings`
     - Some labels can vary slightly, but the structure must exist.
3. **Clear next-step affordances**
   - Each major screen should present:
     - Current status.
     - Primary action(s).
     - A clear “next step” button where appropriate (“Proceed to Evidence Extraction”, etc.).
4. **Status visibility**
   - Users must be able to see job status and pipeline stage completion at a glance.
5. **Auditability & explanation**
   - GUIs surface:
     - Why items were kept or dropped (triage rationales).
     - What evidence supports each rule (Set of Support).
     - Where contradictions or gaps exist.

---

## 2. Main Screens & Routes (Conceptual)

The exact routing structure can be slightly adapted, but **these functional views and their routes must exist**.

### 2.1 Ingestion Interface (`/ingest`)

- **Purpose:** Start a new job (topic → search → triage & processing).
- **Core elements:**
  - Topic input box and/or query fields.
  - Options to:
    - Upload local candidate lists.
    - Select retrieval sources (e.g., Crossref vs local corpus).
  - Cost/time preview (rough token estimate).
- **Behavior:**
  - On successful submission:
    - Create a new `job_id`.
    - Initialize job directory and DB records.
    - Redirect to:
      - **Jobs index** (`/jobs`)  
      or
      - **Shortlist / triage view** (if immediate triage is available).
- **Acceptance criteria:**
  - AT-2.1.1: Submitting the form creates a job row.
  - AT-2.1.2: User sees confirmation that job was created.
  - AT-2.1.3: Global navigation is visible.
  - AT-2.1.4: Page provides brief explanation of next step.

Expected API calls:
- `POST /ingest` or `POST /jobs` with topic/query payload.
- Response includes new `job_id` and initial status.

---

### 2.2 Jobs Index (`/jobs`)

- **Purpose:** Overview of all jobs and their pipeline progress.
- **Presentation:**
  - Table view (not just bullets), sorted by newest jobs first.
  - Columns (minimum):
    - Job ID / name.
    - Topic / description.
    - Status (NEW/TRIAGED/IN_PROGRESS/COMPLETE/FAILED).
    - Stage indicators:
      - Shortlist present?
      - Evidence extraction complete?
      - Rules synthesized?
  - Status badges and stage icons clearly indicate:
    - Which stages are complete.
    - Which are pending.
- **Behaviors:**
  - For each job:
    - Link(s) to:
      - Shortlist / triage view.
      - Evidence view.
      - Rules / Rule Inspector.
      - Library view filtered by that job.
  - Empty state:
    - If no jobs:
      - Show friendly message.
      - Provide CTA to `/ingest`.

Expected API calls:
- `GET /jobs`: returns list of jobs with status & stage flags.
- Optional: `GET /jobs/{job_id}` for detail view.

---

### 2.3 Shortlist / Triage View (e.g., `/jobs/{job_id}/shortlist`)

- **Purpose:** High-recall triage over abstract-level candidates.
- **UI requirements:**
  - Display for each candidate:
    - Title, authors, year.
    - Abstract.
    - Source and similarity score.
  - Indicate **keep vs drop** with:
    - Buttons / toggles.
    - Rationale for both decisions (as available from triage policy).
  - Provide **Recall Sampler** view:
    - A sub-view or toggle that shows a random sample of papers that would have been dropped.
    - Allows manual override and false-negative detection.
- **Behavior:**
  - Users can:
    - Approve shortlists in batches or individually.
    - Promote items to “deep processing.”
  - Progress indicator:
    - How many candidates triaged vs total.
    - Estimated cost if all selected go to deep extraction.

Expected API calls:
- `GET /jobs/{job_id}/shortlist` or `GET /library?job_id={job_id}&stage=shortlist`.
- `POST /jobs/{job_id}/triage` to update keep/drop decisions.
- `POST /jobs/{job_id}/approve_for_deep_processing` to advance stage.

---

### 2.4 Library View (`/library` and `/jobs/{job_id}/library`)

- **Purpose:** Browse and filter the **actual working library** of accepted papers.
- **UI essentials:**
  - Table/grid of papers with:
    - Title, authors, year.
    - Key tags (intervention type, outcome domain).
    - Extraction indicators:
      - `extraction_score`.
      - Number of evidence passages.
      - Number of rules contributed.
  - Filters:
    - By job, topic, intervention, outcome domain, extraction status.
- **Behavior:**
  - Clicking a paper opens a **paper detail / analysis view** (see below).
  - For job-specific views:
    - URL includes job context.
- **Expected API:**
  - `GET /library` with filters (job_id, tags, extraction status).
  - `GET /papers/{paper_id}` for detail view.

---

### 2.5 Paper Analysis View (`/papers/{paper_id}`)

From `Paper_Analysis_Implementation_Guide.md`:

- **Purpose:** Let users inspect how a single paper contributes to the rule system.
- **Content:**
  - Bibliographic info (title, authors, DOI, journal, year).
  - Abstract and possibly introduction snippet.
  - `jobs_referenced` (which jobs this paper appears in).
  - `evidence_passages` grouped by:
    - Outcome domain.
    - Mechanism type.
    - Panel (from 7-panel extraction).
  - Summary stats:
    - `rules_count`, `evidence_count`, `extraction_score` (computed as in core spec).
- **Behavior:**
  - Optionally highlight where this paper contributes to:
    - Micro rules.
    - Meso rules.
    - Contradictions.

Expected API:
- `GET /papers/{paper_id}` returns all of the above fields in structured form.

---

### 2.6 Evidence View (`/jobs/{job_id}/evidence`)

- **Purpose:** Show extracted findings (across papers) for a given job.
- **UI:**
  - Tabular or card-based list of findings with:
    - Intervention.
    - Operational measure.
    - Construct.
    - Effect direction.
    - Study design (RCT, observational, etc.).
  - Links to:
    - Source papers.
    - Rules and contradictions that use each finding.
- **Behavior:**
  - Provide filters by:
    - Construct (stress, anxiety, mood, etc.).
    - Intervention type.
    - Study design.
- **Expected API:**
  - `GET /findings?job_id={job_id}` with optional filters.

---

### 2.7 Rules View & Rule Inspector (`/rules`, `/rules/{rule_id}`)

From GUI spec & CNfA requirements:

- **Purpose:** Let users see and interrogate hierarchical rules.
- **Rules list view:**
  - Show macro and meso rules in a list / table:
    - Rule label (e.g., “Curved walls reduce anxiety”).
    - Level (micro/meso/macro).
    - Outcome construct(s).
    - Confidence / weight.
    - Number of supporting studies.
    - Contradiction flags (if any).
- **Rule detail (Rule Inspector):**
  - Show:
    - Rule text and normalized structure (`antecedents`, `consequent`).
    - Level (micro/meso/macro).
    - Mechanism(s) (predictive processing, motor simulation, etc.).
    - Operational measures involved (for micro rules).
    - Set of Support (SoS):
      - List of findings with paper IDs, citations, and passages.
      - Aggregated metrics (e.g., total N, number of RCTs).
    - Contradictions:
      - List of rules/findings that oppose this rule.
    - BN handoff:
      - How this rule appears as a node/edge in the BN schema.
  - Actions:
    - Request expansions (new literature search).
    - Mark rule as human-verified or flagged.

Expected API:
- `GET /rules?job_id={job_id}` (list).
- `GET /rules/{rule_id}` (detail with SoS & contradictions).
- Optional `POST /rules/{rule_id}/expand` or `POST /jobs/{job_id}/rule_expansion_request`.

---

### 2.8 Hierarchical Findings / Rule Tree View (`/findings/{job_id}/view` or similar)

From `templates/finding_view_hierarchical.html`:

- **Purpose:** Present a **tree or graph view** of the rule hierarchy:
  - MACRO → MESO → MICRO.
- **UI behavior:**
  - Node labels show:
    - Rule / construct name.
    - Level (micro/meso/macro).
    - Basic metrics (confidence, support count).
  - Expand/collapse children.
  - Hover/tooltip shows:
    - Quick summary (intervention, outcome, mechanism).
  - Click transitions to Rule Inspector.

Expected API:
- `GET /findings/{job_id}/hierarchy` or `GET /rules/hierarchy?job_id={job_id}` returning a nested JSON tree.

---

### 2.9 Queue Monitor (`/monitor` or `/queue`)

From queue and UX docs:

- **Purpose:** Monitor job processing and queue health.
- **UI:**
  - Table of jobs in queue with:
    - job_id, user, priority, status.
    - Stage (triage / extraction / synthesis).
    - Estimated completion time.
  - Maybe separate sections for:
    - Active jobs.
    - Pending jobs.
    - Completed jobs.
- **Behavior:**
  - Reflects queue policy (user jobs prioritized over nightly expansions).
  - Ideally supports:
    - Cancelling jobs (where safe).
    - Viewing recent errors.

Expected API:
- `GET /queue` or `GET /jobs?status=...` with priority metadata.

---

### 2.10 Settings / Credentials & Student API Help Modal

From `Student_API_Help_Modal.md`:

- **Purpose:** Help users understand:
  - Where to put their API key.
  - How cost is estimated and displayed.
- **Requirements:**
  - **Never** show API keys in plaintext once saved.
  - Provide:
    - Short explanation of what the key is used for.
    - Link to provider docs (OpenAI, etc.).
    - A warning about not checking secrets into code.
- **UI:**
  - Simple modal or settings pane with:
    - “Enter/Update API Key” action.
    - Indicator if a key is set (without revealing it).

Expected API:
- `POST /settings/api_key` (encrypted at rest).
- `GET /settings` (returns boolean flags, NOT raw key).

---

## 3. Guided Wizard Flow (UX Scaffold)

From `Wizard_Flow_v18_3.md`, the GUI should support a **wizard-like flow**, even if the implementation is modular:

1. **Topic definition panel**
   - Topic input + suggested queries.
   - Cost preview banner.
2. **Triage scan panel**
   - Abstract cards with keep/drop.
   - Recall Sampler section.
3. **Approval panel**
   - Summary of selected clusters/papers.
   - Predicted time & cost HUD.
   - “Start processing” CTA.
4. **Results panel**
   - Cards or organized tabs showing:
     - 7-panel outputs.
     - Clusters.
     - Proposed rules.
     - Contradictions.
5. **Rule Inspector panel**
   - Dedicated space for deeper analysis and expansion.

This can be implemented as:

- one multi-step page,
- or multiple linked views with a clear step indicator and “Continue” buttons.

---

## 4. High-Re
call & QC Surfacing

Triaging and QC requirements must be visible in the GUI:

- Show **triage thresholds and rationales** (or at least labels like “kept for safety,” “borderline,” etc.).
- Expose the **Recall Sampler** for triage discards.
- For extraction:
  - Provide signals when a paper is:
    - Unprocessed.
    - Partially processed.
    - Fully processed (high extraction_score).
- For rules:
  - Indicate:
    - Human-verified vs auto-generated.
    - Rules flagged for contradiction or low evidence.
- For meta-review:
  - Summaries of:
    - Number of RCTs vs observational studies.
    - Spread across operational measures.

---

## 5. API Expectations (Frontend → Backend)

This spec doesn’t dictate exact JSON shapes, but the frontend expects at least:

- `GET /jobs`
  - Returns job summary list with statuses, stage completion flags, and creation timestamps.
- `POST /ingest` or `POST /jobs`
  - Returns a new job with `job_id` and initial status.
- `GET /jobs/{job_id}`
  - Returns detail including counts of shortlist/library/evidence/rules items.
- `GET /shortlist` or `GET /library?job_id=&stage=shortlist`
  - Returns triage candidates with keep/drop flags and rationales.
- `POST /jobs/{job_id}/triage`
  - Accepts updates to keep/drop decisions.
- `POST /jobs/{job_id}/approve_for_deep_processing`
  - Moves items into deeper extraction.
- `GET /library` (with filters)
  - Returns accepted papers and their extraction stats.
- `GET /papers/{paper_id}`
  - Returns full paper details and extraction contributions.
- `GET /findings?job_id=...`
  - Returns structured findings.
- `GET /rules?job_id=...`
  - Returns rule summaries.
- `GET /rules/{rule_id}`
  - Returns full rule details, SoS, contradictions, and BN mapping.
- `GET /rules/hierarchy?job_id=...` (or similar)
  - Returns JSON suitable for hierarchical visualization.
- `GET /queue`
  - Returns queued/active job list with priorities and statuses.
- `GET /settings`, `POST /settings/api_key`
  - Manages credential flags and encrypted key storage.

Align your actual endpoints and payloads with this conceptual contract so that UI code (e.g., `frontend/js/api.js`) can remain thin and predictable.

---

## 6. Visual / UX Consistency

From UX and design notes:

- Use **consistent styling**:
  - Tables for job/library lists.
  - Badges for statuses.
  - Charts or simple indicators for counts (optional).
- Always provide:
  - Clear headings.
  - Short helper text for complex views.
  - Empty-state messages with CTAs (e.g., “No jobs yet — create one →”).

---

## 7. Implementation Guidance

When adding or adjusting GUI elements:

1. **Map each screen to a specific route and API call set.**
2. **Keep global navigation visible and consistent.**
3. **Ensure each screen answers:**
   - “Where am I in the pipeline?”
   - “What can I do here?”
   - “What happens if I click the primary button?”
4. **Keep the UI aligned with triage/queue policies:**
   - Make high-recall behavior and priority handling visible.

If you need to diverge from any of these requirements, update this spec and annotate the rationale.
