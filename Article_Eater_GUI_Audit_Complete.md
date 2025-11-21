# Article Eater Workflow Clarity & GUI Upgrade Audit
## Version 15.8.x — Comprehensive UX/Systems Review

**Assessment Date**: November 8, 2025  
**System Version**: Article Eater v15.8.x  
**Auditor Role**: Senior UX/Systems Reviewer  
**Review Scope**: Complete workflow analysis, page-by-page usability audit, implementation guidance

---

## EXECUTIVE SUMMARY

### Status: GO-WITH-IMPROVEMENTS

The Article Eater system demonstrates exceptional technical architecture with a sophisticated metadata-first RAG pipeline, comprehensive budget safety mechanisms, and rigorous provenance tracking. The backend infrastructure is production-ready from functional and security perspectives.

However, critical usability gaps prevent researchers from effectively using the system without extensive training or technical expertise.

**Core Issues Identified**:

1. **Navigation Fragmentation** (CRITICAL): No consistent global navigation across pages; users get lost
2. **Workflow Opacity** (CRITICAL): Pipeline stages unclear; no progress indicators showing where user is in 5-stage process
3. **State Visibility** (HIGH): Cannot determine job completion status without clicking through each view
4. **Guidance Deficiency** (HIGH): Minimal help text; unclear next steps after completing each stage
5. **Error Messaging** (MEDIUM): Technical errors lack user-friendly remediation guidance

**Verdict**: Proceed with deployment to early adopters (expert users, co-developers) while implementing Priority 1 improvements (estimated 13 hours). System is functional for guided use but not ready for self-service adoption without GUI enhancements.

**Recommended Path**: 
1. Implement critical navigation and state visibility fixes within 1-2 weeks
2. Gather user feedback from initial deployment
3. Proceed with high-value enhancements based on actual usage patterns
4. Iterate based on researcher needs rather than assumptions

**Key Strength**: The theoretical foundation connecting architectural properties to human cognitive states through empirically-grounded mechanisms deserves an interface that matches its intellectual rigor. The technical work is sound; the UI needs surgical improvements to communicate that sophistication.

---

## 1. USER-FLOW MAP & ARCHITECTURE

### 1.1 Intended Five-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│               ARTICLE EATER PIPELINE ARCHITECTURE                │
│       Evidence Synthesis for Architecture Research               │
└─────────────────────────────────────────────────────────────────┘

STAGE 1: INGEST
• Purpose: Acquire candidate papers for analysis
• Options: PDF upload | Single DOI | Batch DOI list
• Enhancement: Semantic Scholar metadata enrichment (optional)
• Output: Job ID + initial metadata collection
• Route: /ingest (GET/POST)

         ↓

STAGE 2: TRIAGE (Metadata-Based Shortlisting)
• Purpose: Reduce corpus to most relevant papers before expensive RAG
• Input: Research query + metadata items (titles, abstracts, keywords)
• Algorithm: Keyword overlap scoring + recency weighting
• Output: Ranked topK list (default k=20)
• Cost: Zero (local computation)
• Routes: POST /shortlist/<job_id>, GET /shortlist/<job_id>/view

         ↓

STAGE 3: LINK (RAG Evidence Extraction)
• Purpose: Extract specific evidence passages with provenance
• Input: Shortlisted papers only (not full corpus)
• Providers: Anthropic (Claude) | OpenAI (GPT-4) | Local (offline)
• Constraint: Budget guard checks before upload (OpenAI)
• Output: Evidence array with passage + title + DOI/URL + method
• Routes: POST /evidence/<job_id>, GET /evidence/<job_id>/view

         ↓

STAGE 4: NETWORK (Rule Synthesis)
• Purpose: Generate architectural design rules from evidence
• Input: Validated evidence set with provenance
• Process: Synthesize actionable principles
• Requirement: Each rule links to supporting evidence
• Output: Rules with confidence scores + provenance
• Routes: POST /rules/<job_id>, GET /rules/<job_id>/view

         ↓

STAGE 5: MONITOR (Budget & Lifecycle Management)
• Purpose: Track costs, manage remote storage, ensure sustainability
• Metrics: Queue count, processed count, remote bytes, notional cost
• Safety: Free-limit enforcement, auto-purge option
• Actions: Manual purge of processed files
• Route: GET /monitor/openai

┌─────────────────────────────────────────────────────────────────┐
│                      ADMINISTRATIVE ROUTES                       │
├─────────────────────────────────────────────────────────────────┤
│ /rag/settings    - Provider config, API keys, budget limits     │
│ /jobs            - Index of all jobs with stage completion      │
│ /healthz         - System health check endpoint                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Critical Navigation & Workflow Gaps

**Gap 1: No Global Navigation Structure**

Current State:
- Each page has isolated footer links (inconsistent)
- No persistent header showing main navigation
- Users must use browser back button or memorize URLs

Impact:
- High cognitive load remembering how to navigate
- Users get "lost" after drilling into job views
- No clear path back to jobs index from evidence/rules views

Proposed Solution:
- Persistent header navigation bar on all pages:
  `Ingest | Jobs | RAG Settings | Monitor`
- Always visible regardless of scroll position
- Current page highlighted in navigation

**Gap 2: No Pipeline Progress Indicators**

Current State:
- Job views (shortlist, evidence, rules) show data but not position in pipeline
- Users don't know if they're on step 2 of 5 or if pipeline is complete
- No visual indication of which stages have data

Impact:
- Unclear whether more work is needed
- Can't quickly assess job completeness
- No sense of forward progression

Proposed Solution:
- Five-stage visual indicator below global nav:
  ```
  [1. Ingest] → [2. Triage*] → [3. Link] → [4. Network] → [5. Monitor]
  ```
  (*= current stage highlighted)
- Show completed stages in green, current in blue, pending in gray
- Present on all job-related pages

**Gap 3: No Job State Visualization**

Current State:
- Jobs index shows flat bullet list of job IDs
- Three links per job (shortlist, evidence, rules) with no context
- Cannot determine which jobs are complete vs. in-progress
- No way to quickly scan for jobs needing attention

Impact:
- Must click into each job to assess status
- Time wasted checking empty views
- No prioritization possible

Proposed Solution:
- Table format with columns:
  `Job ID | Status Badge | Stages Complete | Actions`
- Status badges:
  - "New" (gray) = just created, no stages
  - "Triaged" (blue) = has shortlist only
  - "In Progress" (yellow) = has evidence, working on rules
  - "Complete" (green) = all stages finished
- Stage icons: 📋 (shortlist), 🔗 (evidence), 🧠 (rules)
  - Icons filled/highlighted when stage has data
- Sort by creation date (most recent first)

**Gap 4: Missing Breadcrumb Navigation**

Current State:
- Individual views (shortlist/evidence/rules) lack context
- No indication of hierarchical position
- Hard to understand relationship between pages

Impact:
- Disorientation when switching between stages
- Unclear how to navigate to related views
- No path history

Proposed Solution:
- Breadcrumb pattern on all job views:
  `Jobs » job_12345 » Shortlist`
- Clickable ancestors (Jobs, job_id)
- Current page shown as plain text
- Horizontal stage navigation below breadcrumb:
  `[Shortlist*] → [Evidence] → [Rules]`
  (*= current active)

**Gap 5: No Next-Step Guidance**

Current State:
- After completing a stage, no indication of what to do next
- Shortlist view doesn't say "proceed to evidence extraction"
- Evidence view doesn't guide toward rule synthesis
- Rules view doesn't indicate pipeline completion

Impact:
- Users unsure if they should wait, click something, or run a command
- Workflow stalls without explicit progression cues
- No sense of task completion

Proposed Solution:
- Call-to-action buttons at bottom of each view:
  - Shortlist: "Proceed to Evidence Extraction →"
  - Evidence: "Proceed to Rule Synthesis →"
  - Rules: "Pipeline Complete" panel with next options
- Helper text explaining what happens next
- Clear visual hierarchy (large button, supporting text)

---

## 2. PAGE-BY-PAGE USABILITY AUDIT

### 2.1 Ingestion Interface (`/ingest`)

**Current Implementation**: `templates/ingest_choice.html`

Form with:
- Three radio buttons (PDF / Single DOI / DOI List)
- Checkbox for "Use Semantic Scholar"
- Text input for single DOI
- Textarea for DOI list
- Submit button labeled "Save Choice"
- Footer note about PDF uploads

**Problems Identified**:

1. **Mode Selection Confusion** (High Severity)
   - Three options presented with no explanation of differences
   - No guidance on when to use each mode
   - Users unclear about which mode serves their needs

2. **Semantic Scholar Toggle Ambiguity** (Medium Severity)
   - Checkbox label: "Fetch metadata from Semantic Scholar (if DOI provided)"
   - Passive phrasing doesn't convey value proposition
   - No explanation of metadata-first approach or cost benefits
   - Users don't understand why they should check it

3. **Button Label Mismatch** (High Severity)
   - Button says "Save Choice"
   - Implies storing preferences, not initiating processing
   - Users expect configuration save, not job creation
   - No indication that this creates a job_id

4. **Missing Next-Step Context** (High Severity)
   - No explanation of what happens after clicking button
   - Users don't know if they'll be redirected or see confirmation
   - Unclear how to access created job afterward

5. **Navigation Isolation** (Critical)
   - No global navigation header
   - No link back to jobs index
   - No breadcrumb showing "Ingest" position in system

6. **Input Validation Absent** (Medium Severity)
   - No client-side DOI format checking
   - No indication of required vs. optional fields
   - Radio button changes don't update relevant input visibility

7. **Helper Text Inadequate** (Medium Severity)
   - Footer note mentions "main upload wizard" (confusing)
   - Doesn't explain workflow or next steps
   - No guidance on best practices

**Recommended Fixes**:

**Fix 2.1.1: Enhanced Mode Selection with Inline Descriptions**
```html
<fieldset class="mode-selector">
  <legend>Choose Your Ingestion Mode</legend>
  
  <label class="mode-option">
    <input type="radio" name="mode" value="pdf" checked>
    <span class="mode-title">Upload PDF Files</span>
    <span class="mode-description">
      Upload PDFs directly for full-text processing. Best when papers
      aren't yet in academic databases or you have locally stored files.
    </span>
  </label>
  
  <label class="mode-option">
    <input type="radio" name="mode" value="doi_single">
    <span class="mode-title">Single DOI Entry</span>
    <span class="mode-description">
      Enter one DOI to fetch metadata and optionally retrieve full text.
      Ideal for testing the pipeline or analyzing a specific paper.
    </span>
  </label>
  
  <label class="mode-option">
    <input type="radio" name="mode" value="doi_list">
    <span class="mode-title">Batch DOI List</span>
    <span class="mode-description">
      Paste multiple DOIs (one per line) for systematic literature processing.
      Recommended for established research domains with known papers.
    </span>
  </label>
</fieldset>
```

**Fix 2.1.2: Semantic Scholar Value Proposition**
```html
<fieldset class="metadata-options">
  <legend>Metadata Enrichment Strategy</legend>
  
  <label class="toggle-option">
    <input type="checkbox" name="use_semantic_scholar" checked>
    <span class="toggle-title">
      <strong>Recommended:</strong> Use Semantic Scholar First
    </span>
    <span class="toggle-explanation">
      Fetches title, abstract, keywords, and year before full-text retrieval.
      This metadata-first approach dramatically reduces RAG processing costs
      by 80-95% through intelligent pre-filtering. You'll review a shortlist
      before any expensive operations occur.
    </span>
  </label>
</fieldset>
```

**Fix 2.1.3: Clear Call-to-Action**
```html
<div class="action-panel">
  <button type="submit" class="btn-primary">
    Create Job & Begin Triage
  </button>
  <p class="action-helper">
    This will create a new research job and generate a metadata-based shortlist.
    You'll review the shortlist before any RAG processing or costs occur.
  </p>
</div>
```

**Priority**: P1 (Critical)  
**Estimated Effort**: 3 hours  
**Dependencies**: Global nav header (see Fix 2.1.4)

**Fix 2.1.4: Add Global Navigation** (see Section 3.1)

**Acceptance Tests**:
- AT-2.1.1: Mode descriptions visible inline with radio buttons
- AT-2.1.2: Semantic Scholar explanation mentions cost savings
- AT-2.1.3: Button reads "Create Job & Begin Triage"
- AT-2.1.4: Helper text explains next step (review shortlist)
- AT-2.1.5: Global navigation appears at top of page
- AT-2.1.6: Form submission creates job_id and redirects

### 2.2 Jobs Index (`/jobs`)

**Current Implementation**: `templates/jobs_index.html`

Simple list with:
- Heading "Jobs"
- Conditional rendering (if jobs exist / else no jobs message)
- For each job: bullet point with three links
- Footer links to ingestion, RAG settings, OpenAI monitor

**Problems Identified**:

1. **No Status Information** (Critical)
   - Job IDs shown but no indication of completion
   - Cannot tell which jobs have shortlist, evidence, or rules
   - Must click through each job to determine state

2. **Poor Scannability** (High Severity)
   - Bullet list format hard to scan with many jobs
   - No visual hierarchy or grouping
   - All jobs look identical regardless of state

3. **Flat Link Structure** (Medium Severity)
   - Three links per job with no context
   - Doesn't indicate if clicking will show data or empty page
   - Equal visual weight despite different completion states

4. **Missing Sorting/Filtering** (Medium Severity)
   - Jobs appear in filesystem order (arbitrary)
   - No way to sort by creation date
   - No way to filter by status
   - No search functionality

5. **Empty State Minimal** (Medium Severity)
   - Says "No jobs recorded yet"
   - Doesn't explain what jobs are or how to create one
   - No call-to-action button

6. **Navigation Issues** (Critical)
   - No global header navigation
   - Footer links disconnected from main content
   - No indication this is the "home" page for job management

**Recommended Fixes**:

**Fix 2.2.1: Table Format with State Detection**

Backend enhancement (`app/routes_jobs.py`):
```python
from pathlib import Path

@bp.route("/jobs")
def jobs_index():
    jobs = []
    FINDINGS = Path(__file__).resolve().parent.parent / "findings"
    
    if FINDINGS.exists():
        # Sort by creation time, most recent first
        for p in sorted(FINDINGS.iterdir(), 
                       key=lambda x: x.stat().st_ctime, 
                       reverse=True):
            if p.is_dir() and not p.name.startswith('.'):
                # Check for stage completion
                state = {
                    'id': p.name,
                    'has_shortlist': (p / 'shortlist.json').exists(),
                    'has_evidence': (p / 'evidence.json').exists(),
                    'has_rules': (p / 'rules.json').exists(),
                    'created': p.stat().st_ctime
                }
                
                # Determine overall status
                if state['has_rules']:
                    state['status'] = 'complete'
                elif state['has_evidence']:
                    state['status'] = 'active'
                elif state['has_shortlist']:
                    state['status'] = 'pending'
                else:
                    state['status'] = 'new'
                
                jobs.append(state)
    
    return render_template("jobs_index.html", jobs=jobs)
```

Template replacement:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Jobs — Article Eater</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  {% include '_partials/nav.html' %}
  
  <div class="container">
    <header class="page-header">
      <h1>Jobs Overview</h1>
      <p class="page-description">
        Each job represents one evidence synthesis pipeline. Track progress through
        the five stages: Ingest → Triage → Link → Network → Monitor.
      </p>
    </header>
    
    {% if jobs %}
    <div class="actions-bar">
      <a href="/ingest" class="btn-primary">+ New Job</a>
    </div>
    
    <table class="jobs-table">
      <thead>
        <tr>
          <th>Job ID</th>
          <th>Status</th>
          <th>Stages Complete</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for j in jobs %}
        <tr class="job-row">
          <td class="job-id"><code>{{ j.id }}</code></td>
          
          <td class="job-status">
            {% if j.status == 'complete' %}
              <span class="badge badge-complete">Complete</span>
            {% elif j.status == 'active' %}
              <span class="badge badge-active">In Progress</span>
            {% elif j.status == 'pending' %}
              <span class="badge badge-pending">Triaged</span>
            {% else %}
              <span class="badge badge-new">New</span>
            {% endif %}
          </td>
          
          <td class="stages-indicators">
            <span class="stage-icon {% if j.has_shortlist %}complete{% endif %}" 
                  title="Shortlist">📋</span>
            <span class="stage-icon {% if j.has_evidence %}complete{% endif %}" 
                  title="Evidence">🔗</span>
            <span class="stage-icon {% if j.has_rules %}complete{% endif %}" 
                  title="Rules">🧠</span>
          </td>
          
          <td class="job-actions">
            <a href="/shortlist/{{ j.id }}/view" class="btn-sm">Shortlist</a>
            <a href="/evidence/{{ j.id }}/view" class="btn-sm">Evidence</a>
            <a href="/rules/{{ j.id }}/view" class="btn-sm">Rules</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    
    {% else %}
    
    <div class="empty-state">
      <p class="empty-icon">📂</p>
      <h2>No Jobs Yet</h2>
      <p>
        Create your first evidence synthesis job to begin extracting
        architectural design rules from academic literature.
      </p>
      <a href="/ingest" class="btn-primary">Start Ingestion</a>
    </div>
    
    {% endif %}
  </div>
</body>
</html>
```

**Priority**: P1 (Critical)  
**Estimated Effort**: 4 hours  
**Dependencies**: CSS framework with badge/table styles

**Acceptance Tests**:
- AT-2.2.1: Jobs display in table format
- AT-2.2.2: Status badges show correct state (New/Triaged/In Progress/Complete)
- AT-2.2.3: Stage icons reflect actual file existence
- AT-2.2.4: Most recent jobs appear at top
- AT-2.2.5: Empty state shows when no jobs present
- AT-2.2.6: Empty state CTA links to /ingest

### 2.3 Short ENDREPORT

wc -c /mnt/user-data/outputs/Article_Eater_GUI_Audit_Complete.md