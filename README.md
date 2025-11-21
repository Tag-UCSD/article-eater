# 🧠 Article Eater v18.4.3

Article Eater is an **evidence synthesis and rule-construction engine** for environmental / architectural interventions and their effects on human outcomes (stress, anxiety, mood, cognition, etc.).

It is designed to:

- Ingest and triage large sets of papers with **high recall**.
- Extract structured **findings** and **mechanisms** using multi-pass LLM prompts.
- Build a **hierarchical rule system** (micro → meso → macro).
- Produce **BN-ready handoff artifacts** for downstream Bayesian / causal modeling.
- Operate under a **governance kit** that enforces transparency, auditability, and human-in-the-loop (HITL) control.

Current codebase version: **v18.4.3**  
Status: **v18 core architecture and GUI assets are present; backend–GUI wiring and some routes are still being completed.**

---

## 📂 Project Structure (High Level)

```text
article_eater_v18_4_3/
  app/                  # FastAPI app, worker, middleware, security
  frontend/             # Static dashboard HTML/CSS/JS
  migrations/           # Database migrations (SQL files)
  db/                   # DB-related helpers / seed files (if present)
  specs/                # Canonical v18 specification docs (core + GUI)
  contracts/            # JSON / artifact contracts (findings, rules, links, etc.)
  prompts/              # LLM prompt templates (7-panel extraction, etc.)
  governance_kit/       # Governance helpers and audit/checklist tooling
  scripts/              # Utility scripts (migrations, helpers, etc.)
  static/               # CSS/assets for hierarchical views
  templates/            # Jinja2 templates for hierarchical rule / finding views
  tests/                # Test suite (unit/integration tests)
  docs/                 # Additional design / analysis docs (v18-era, archived v16/v17)
  .github/              # CI workflows (if present)
  README.md             # You are here
````

> **Important:** v18.4.3 is the canonical baseline.
> v16/v17 docs and earlier handoff prompts are archived for history and **must not** be treated as current implementation instructions.

---

## 📘 Specification Files (`specs/`)

The **`specs/`** folder contains the authoritative, implementation-relevant specifications for Article Eater v18.x (current version: **v18.4.3**).
These files replace earlier scattered specification documents and should be treated as the single source of truth whenever modifying or extending the system.

### ✔️ `specs/V18_CORE_REQUIREMENTS.md`

Defines the **core architecture and invariants** of Article Eater v18, including:

* Required database semantics.
* `finding_links` schema contract:

  * `link_type VARCHAR(20) NOT NULL CHECK(link_type IN ('CAUSAL', 'TAXONOMIC'))`
* Confidence formulas (RCT, meta-analysis, theoretical), which must match exactly:

  * RCT:

    ```python
    conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
    ```
  * Meta-analysis:

    ```python
    conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
    ```
  * Theoretical:

    ```python
    return -1.0  # MANUAL_REVIEW_REQUIRED
    ```
* Extraction pipeline logic (multi-pass “7-panel” architecture).
* High-recall triage policy and queue policy.
* Hierarchical rule structure (micro → meso → macro).
* BN handoff requirements.
* Governance and QC constraints.

**Any backend change must comply with this document.**

---

### ✔️ `specs/V18_GUI_REQUIREMENTS.md`

Defines the expected **frontend behavior and API contract**, including:

* All required GUI screens and their purposes:

  * Ingestion interface (`/ingest`)
  * Jobs index (`/jobs`)
  * Shortlist / triage view
  * Library (`/library`)
  * Paper analysis view (`/papers/{paper_id}`)
  * Evidence view (`/jobs/{job_id}/evidence`)
  * Rules and Rule Inspector (`/rules`, `/rules/{rule_id}`)
  * Hierarchical rule tree view
  * Queue / Monitor
  * Settings & API key help modal
* Routing structure and navigation requirements.
* Wizard-like workflow:

  * Topic → Triage → Approval → Results → Rule Inspector.
* UX requirements:

  * Recall Sampler.
  * Status indicators and extraction scores.
  * Clear “where am I in the pipeline?” cues.
* Expected API endpoints and response semantics used by the GUI.

**Any frontend or router change must remain faithful to this document.**

---

### 🔐 Why this matters

These two files were created by synthesizing **all relevant v18-era specifications** from the cleaned repository, including:

* GUI audits and UX specs.
* Enhancement analyses and release notes.
* CNfA / BN integration requirements.
* Triaging and queue policy docs.
* Paper analysis and extraction pipeline guides.

They consolidate every **stable requirement** while excluding outdated build-phase instructions (e.g., v17 migration guides, old handoff prompts).

---

## 🚀 Getting Started

### 1. Prerequisites

* **Python**: 3.10+ (3.11/3.12 should work; verify with your environment).
* **pip** or equivalent (pipx, Poetry, etc.).
* A **database**:

  * Default setup is generally SQLite (e.g., `./ae.db`) for local dev.
  * Some deployments may target Postgres; check any `config/` or `settings` modules for details.
* Recommended: a virtual environment (`venv`, `conda`, etc.).

### 2. Clone and set up environment

```bash
git clone <your-repo-url> article_eater_v18_4_3
cd article_eater_v18_4_3

python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

If `requirements.txt` is not present or is split, consult any setup docs under `docs/` or check `pyproject.toml` if you’re using Poetry.

---

### 3. Database initialization

The repo ships with SQL migration files under `migrations/`.
The exact setup will depend on your DB preferences:

1. **Check configuration**
   Look for DB config in:

   * `config/` (e.g., a `config.py` or `settings.py`),
   * or environment variables (`DATABASE_URL`, etc.).

2. **Apply migrations**

   * If there is a helper script under `scripts/` (e.g., `scripts/apply_migrations.py`, `scripts/db_init.sh`), use that.
   * Otherwise, apply the SQL files under `migrations/` using your preferred DB tool, in order.

> Note: v18 involves the `finding_links` table and other constraints described in `specs/V18_CORE_REQUIREMENTS.md`. Ensure migrations align with those requirements.

---

### 4. Running the worker

The worker is responsible for processing queued jobs: triaging, extraction, synthesis, and rule construction.

From the project root:

```bash
# Typical pattern:
python app/worker.py
```

Often you’ll run it in the background:

```bash
python app/worker.py &
```

Check log output to confirm:

* Successful DB connection.
* Polling loop started (e.g., “Worker starting (poll_interval=5s)”).
* No glaring import or configuration errors.

---

### 5. Running the backend API (FastAPI)

From the project root:

```bash
uvicorn app.main:app --reload
```

You should see log output similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Useful endpoints:

* `GET /healthz` – simple health check.
* `GET /metrics` – Prometheus metrics.
* `GET /docs` – auto-generated Swagger UI.
* `GET /redoc` – alternative API documentation.

> **Note:** As-of v18.4.3, only a minimal set of routes may be fully wired (health/metrics/docs).
> GUI-facing routes (e.g., `/jobs`, `/ingest`, `/library`, `/findings`, `/rules`) are being built out according to `specs/V18_GUI_REQUIREMENTS.md`.

---

### 6. Running the frontend

The `frontend/` folder contains the v18 dashboard (HTML/CSS/JS), including:

* `frontend/dashboard.html`
* `frontend/js/api.js`
* `frontend/css/main.css`
* `frontend/assets/…`

For a simple dev setup, you can serve it as static files:

```bash
cd frontend
python -m http.server 8080
```

Then open:

* `http://127.0.0.1:8080/dashboard.html`

In a more integrated setup, the goal is to mount `frontend/` via FastAPI:

* Mount as static files under `/static`.
* Serve `dashboard.html` at `/` from the backend.

See `specs/V18_GUI_REQUIREMENTS.md` for how the GUI is expected to interact with backend APIs.

---

## 🧪 Testing

If a `tests/` folder is present and configured:

```bash
pytest
```

Look in `tests/` for:

* Smoke tests (`/healthz`, `/metrics`).
* Integration tests for ingest → worker → library → rules (as they are added).

Adding tests for any new routes or pipeline steps should always follow the spec constraints in `specs/`.

---

## 🧭 Development Guidelines

### 1. Always read the specs first

Before making any change:

1. Read `specs/V18_CORE_REQUIREMENTS.md`.
2. Read `specs/V18_GUI_REQUIREMENTS.md`.

Treat these as **contracts**. If your change would violate them:

* Update the spec first.
* Clearly document why the change is necessary.

### 2. Respect the governance kit

* The `governance_kit/` directory contains:

  * Templates and renderers for handoff / checklists.
  * Scripts (e.g., conversation guard) that ensure AI-assisted changes are documented.
* Do **not** delete or drastically alter these without a good reason.

### 3. Preserve traceability

* Always maintain the ability to trace:

  * Rules → findings → papers → passages.
* Do not introduce silent transformations that hide this linkage.

### 4. Be cautious with migrations and schemas

* The DB schema must match the invariants described in `V18_CORE_REQUIREMENTS.md`, especially:

  * `finding_links.link_type` constraint.
  * Confidence computations and extraction scores.

---

## 🤖 Using AI Assistants Safely (ChatGPT / Gemini / Claude)

This repo is explicitly designed to be extended with help from LLMs, but there are guardrails:

### ✅ When using an AI assistant:

* Upload:

  * The **codebase**.
  * The **`specs/` folder**, especially:

    * `specs/V18_CORE_REQUIREMENTS.md`
    * `specs/V18_GUI_REQUIREMENTS.md`
* Make it clear:

  * v18.4.3 is the **baseline**.
  * v16/v17 docs under `docs/archive` or similar are **historical context only**.

### ❌ Do **not**:

* Upload or follow old “build v18 from v17” handoff prompts.
* Ask an AI to “regenerate v18” from scratch.
* Let an AI rewrite:

  * Migrations wholesale.
  * Agents/confidence code, without checking invariants.

### 🧪 Process suggestions:

1. Ask for **one meaningful change at a time** (e.g., “Implement `/jobs` router that matches frontend expectations”).
2. Require:

   * A short summary of what changed.
   * Code snippets/diffs.
   * A self-audit: what might this break? how to test it?
3. Run the tests and manual checks yourself before merging changes.

---

## 🧩 Roadmap (High-Level)

The following work is typical for continuing from v18.4.3:

1. **Implement GUI-facing API routes** (`/jobs`, `/ingest`, `/library`, `/findings`, `/rules`, etc.) to match `frontend/js/api.js` and `specs/V18_GUI_REQUIREMENTS.md`.
2. **Wire worker ↔ DB ↔ API** end-to-end so GUI-driven jobs truly process and populate the library/findings/rules.
3. **Mount frontend via FastAPI** to serve `dashboard.html` from `/` for a single-origin app.
4. **Finish Rule Inspector and hierarchical view routes**, binding Jinja templates to real data.
5. **Add integration tests** for ingest → triage → extraction → rules → BN handoff.

---

## AI prompt to get started

```
You are a senior full-stack engineer and AI-assisted software development expert working on the Article Eater system, version v18.4.3.
We are not migrating v17 → v18. We are not generating v18 from scratch. We are continuing from the existing, cleaned v18.4.3 codebase I will upload next.
Your job is to incrementally complete the system—one small, verifiable step at a time—strictly following the specifications in the newly standardized specs/ directory.

1. Before doing ANY work
After I upload the repo:
Read and internalize these two files FIRST
(They are the authoritative spec for all behavior.)
* specs/V18_CORE_REQUIREMENTS.md
* specs/V18_GUI_REQUIREMENTS.md
These files contain ALL required invariants, including:
* database semantics
* link_type constraints
* confidence formulas
* extraction pipeline semantics
* hierarchical rule logic
* BN handoff requirements
* API expectations for GUI
* GUI screen requirements
* triage and queue policies
* UX requirements
* governance rules
Treat these as contracts. You must not violate them.

2. Required code to inspect before making any changes
To ground yourself in the actual implementation, inspect (do NOT modify yet):
Backend (FastAPI)
* app/main.py
* app/worker.py
* All modules under app/ (routers, middleware, models, utils)
Database
* All SQL files under migrations/
* Anything under db/ (init, helpers, seeds)
Frontend
* frontend/dashboard.html
* frontend/js/api.js
* frontend/css/main.css
* Any .html or assets in frontend/
Templates
* templates/finding_view_hierarchical.html
* templates/_partials/*
* static/hierarchy_v17.css (historical name; still part of v18 hierarchy view)
Contracts, prompts, governance
* contracts/
* prompts/ (7-panel prompts, synthesis prompts)
* governance_kit/ Do NOT modify this unless I explicitly request it.
Archive folders
docs/archive and any v16/v17 materials are historical only and must never be treated as implementation instructions.

3. Critical v18 invariants to enforce
You must preserve these exactly, and reference the CORE spec before doing anything affecting them.
Schema invariant

link_type VARCHAR(20) NOT NULL CHECK(link_type IN ('CAUSAL', 'TAXONOMIC'))
Confidence formulas (must match exactly)
RCT confidence

conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
Meta-analysis confidence

conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
Theoretical support

return -1.0
Agent_Classifier
Must follow the two-pass triage specification described in core spec.
Hierarchical rule structure
* MICRO → MESO → MACRO rollups must remain intact.
* No flattening.
* Evidence traceability required.

4. Your mission (Phase-2 onward)
Your job is to extend and complete the existing v18.4.3 system.
You must not rewrite or regenerate:
* the entire backend
* the entire frontend
* migrations
* workers
* rule system
* prompts
* governance kit
Instead, your tasks are:
1. Audit the current system Determine what exists, what routes are missing, and what the GUI expects.
2. Extract the real API contract from both:
    * frontend/js/api.js
    * specs/V18_GUI_REQUIREMENTS.md
3. Implement missing backend routes matching spec + GUI expectations:
    * /jobs
    * /ingest
    * /library
    * /papers
    * /findings
    * /rules
    * /rules/{rule_id}
    * hierarchical /rules/hierarchy
    * /queue
    * /settings
4. Wire worker → DB → API so GUI-triggered jobs process end-to-end.
5. Integrate the frontend with FastAPI (serve dashboard from / or /app, mount static files, etc.)
6. Complete the hierarchical view + Rule Inspector using existing Jinja templates.
7. Add integration tests for new routes and job flows.
8. Always check spec compliance before proposing or writing code.
Everything must be done incrementally so I can test each addition.

5. Process rules (must follow)
For every step:
1. Audit → Explain → Propose next step
    * Summarize the relevant code you inspected.
    * Explain what’s missing relative to the spec.
    * Propose a single, meaningful next step.
2. Provide minimal diffs only
    * When coding, show only the specific files/changes required.
    * Keep patches small and testable.
3. Perform a RUTHLESS self-audit For each change, tell me:
    * What invariants this touches.
    * What might break.
    * How I should manually test it now.
4. Stop and wait for my approval before performing the next step.
You may NOT:
* Rewrite or replace migrations.
* Rebuild the entire rule system.
* Modify governance_kit.
* Reinvent extraction prompts.
* Use old v16/v17 docs as instructions.
* Generate a new “v19” design.
You may:
* Add small helper functions or data models needed for API routes.
* Add routers, modify main.py, integrate templates.
* Add new tests.
* Add new small modules if needed—but never replace core ones without approval.

6. Your First Task (Mandatory Step 1)
After scanning the repo and both spec files, produce:
Step 1 — Phase-2 Initialization Report
A concise report (1–2 screens) including:
(1) Backend reality
* List existing routes.
* Identify missing routes required by the GUI spec.
* Note worker behavior and how jobs are represented in DB.
(2) Frontend API expectations
* Extract all API endpoints referenced in frontend/js/api.js, with:
    * HTTP method
    * Expected request body
    * Expected response JSON
(3) Gaps blocking end-to-end flow
Example categories:
* Missing job routes
* Missing ingest pipeline wiring
* Worker-trigger integration missing
* Library/paper/finding/rule endpoints missing
* Hierarchical view route missing
* Frontend cannot reach backend due to CORS or hosting issues
(4) Propose the ONE next action
Such as:
"Implement /jobs GET endpoint (list jobs) exactly as required by GUI and core spec."
Stop after proposing the action. Wait for my approval before implementing.
```



# Article Eater v18.4 

**Evidence-Based Design Research Automation for Cognitive Science Education**

See [RELEASE_NOTES_v18_4.md](RELEASE_NOTES_v18_4.md) for complete documentation.

## Quick Start

```bash
# Install
pip install -r requirements.txt pdfminer.six==20221105 cryptography==41.0.7

# Configure
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > .env
echo "MASTER_KEY=$(cat .env)" > .env
echo "DB_URL=sqlite:///./ae.db" >> .env

# Initialize DB
sqlite3 ae.db < db/sql/010_rules_core.sql
sqlite3 ae.db < db/sql/014_security.sql

# Run
python app/worker.py &
uvicorn app.main:app
```

## What's New in v18.4

✅ Queue worker implementation  
✅ Secure API key management  
✅ PDF text extraction  
✅ Enterprise-ready security

See full documentation in [RELEASE_NOTES_v18_4.md](RELEASE_NOTES_v18_4.md)


