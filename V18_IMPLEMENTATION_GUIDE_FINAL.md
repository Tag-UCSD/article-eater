# V18 IMPLEMENTATION GUIDE - WITH GEMINI'S DEFINITIVE ANSWERS
## Ready to Execute: All Ambiguity Resolved

**Date**: 2025-11-11  
**Status**: 🟢 **DEFINITIVE GO** - All critical questions answered  
**Confidence**: 95% (was 85%, now higher with Gemini's clarifications)

---

## EXECUTIVE SUMMARY: WHAT GEMINI CONFIRMED

### ✅ CRITICAL CLARIFICATIONS RECEIVED

1. **"Triple Hierarchy" = Dual Hierarchy + Two Edge Types**
   - NOT three hierarchies
   - TWO node types (Findings, Mechanisms)
   - TWO edge types in Findings (CAUSAL, TAXONOMIC)
   - **Solution**: New `finding_links` table with `link_type` field

2. **Set of Support = Concrete Formulas Provided**
   - RCT: `conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)`
   - Meta-Analysis: `conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I²)`
   - Theoretical: `conf = MANUAL_REVIEW_REQUIRED` (HITL)

3. **Librarian vs Synthesizer = Option A (Pre-computed)**
   - 7-Panel extraction during ingestion (not lazy)
   - Human approval gate before expensive extraction
   - "Instant" means literally instant (not 30-second wait)

### 🎯 VERDICT: IMPLEMENT V18 NOW

**Rationale**:
- All "black boxes" specified
- Database schema clear (finding_links table)
- Confidence formulas transparent and tunable
- Data flow unambiguous (pre-compute with HITL gate)
- v17 → v18 migration path obvious

---

## PART 1: THE CRITICAL DATABASE FIX

### Gemini's Revelation: parent_finding_id is "Catastrophically Flawed"

**v17 Problem**:
```sql
-- v17 ONLY has this:
CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    parent_finding_id INTEGER REFERENCES findings(id), -- WRONG!
    ...
);
```

**Why It's Broken**:
- Can only model ONE type of relationship
- Cannot distinguish:
  - `Cortisol↓ → Stress Reduction` (TAXONOMIC - rollup)
  - `Plants → Cortisol↓` (CAUSAL - empirical effect)
- If Cortisol↓ has TWO parents, we lose semantic meaning

**v18 Solution** (Gemini's exact specification):

```sql
-- Migration 005: Create finding_links table (replaces parent_finding_id)
-- Article Eater v18.0 (Dual Hierarchy with Edge Types)

CREATE TABLE finding_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source and target findings
    source_finding_id INTEGER NOT NULL REFERENCES findings(id),
    target_finding_id INTEGER NOT NULL REFERENCES findings(id),
    
    -- THE CRITICAL FIELD
    link_type VARCHAR(20) NOT NULL, -- 'CAUSAL' or 'TAXONOMIC'
    
    -- Link weight (confidence)
    weight REAL,
    
    -- Set of Support (JSON)
    set_of_support TEXT, -- JSON: {N, p, d, method} for CAUSAL links
    
    -- Provenance
    paper_id INTEGER REFERENCES papers(id),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(source_finding_id, target_finding_id, link_type, paper_id)
);

CREATE INDEX idx_finding_links_source ON finding_links(source_finding_id);
CREATE INDEX idx_finding_links_target ON finding_links(target_finding_id);
CREATE INDEX idx_finding_links_type ON finding_links(link_type);
CREATE INDEX idx_finding_links_paper ON finding_links(paper_id);

-- Remove parent_finding_id from findings table (no longer needed)
-- This is done via table recreation in SQLite
```

**Example Data**:

```sql
-- TAXONOMIC link (definitional rollup)
INSERT INTO finding_links (source_finding_id, target_finding_id, link_type, weight)
VALUES (
    (SELECT id FROM findings WHERE name = 'Cortisol↓'),
    (SELECT id FROM findings WHERE name = 'Stress Reduction'),
    'TAXONOMIC',
    1.0  -- Definitional links have weight=1.0
);

-- CAUSAL link (empirical effect)
INSERT INTO finding_links (source_finding_id, target_finding_id, link_type, weight, set_of_support, paper_id)
VALUES (
    (SELECT id FROM findings WHERE name = 'Plants'),
    (SELECT id FROM findings WHERE name = 'Cortisol↓'),
    'CAUSAL',
    0.82,  -- Calculated confidence
    '{"N": 68, "p": 0.03, "d": 0.52, "method": "RCT"}',
    (SELECT id FROM papers WHERE doi = '10.1234/example')
);
```

---

## PART 2: SET OF SUPPORT - CONCRETE FORMULAS

### Gemini's Exact Specifications

**A. For EXPERIMENTAL_RCT**

```python
# setof_support.py - Experimental support calculation

def calculate_confidence_rct(finding: Finding, papers: List[Paper]) -> float:
    """
    Gemini's formula:
    conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
    """
    # Extract from Set of Support JSON
    total_n = sum(p.set_of_support['N'] for p in papers if 'N' in p.set_of_support)
    min_p = min(p.set_of_support['p'] for p in papers if 'p' in p.set_of_support)
    avg_d = mean(p.set_of_support['d'] for p in papers if 'd' in p.set_of_support)
    
    # Normalize scores (Gemini's exact heuristics)
    score_N = min(total_n / 200, 1.0)  # Caps at N=200
    score_p = max(0, 1.0 - (min_p / 0.05))  # p=0.05 → 0, p<0.05 → >0
    score_d = min(abs(avg_d) / 0.8, 1.0)  # Caps at Cohen's d=0.8 (large effect)
    
    # Weighted confidence (Gemini's weights)
    conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
    
    return conf
```

**B. For META_ANALYSIS**

```python
def calculate_confidence_meta(finding: Finding, meta_paper: Paper) -> float:
    """
    Gemini's formula:
    conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
    """
    sos = meta_paper.set_of_support
    
    k_studies = sos['k_studies']
    ci_width = sos['ci_upper'] - sos['ci_lower']
    i_squared = sos['i_squared']  # Heterogeneity (0-100)
    
    # Normalize scores
    score_k = min(k_studies / 20, 1.0)  # Caps at 20 studies
    score_CI = max(0, 1.0 - (ci_width / 0.5))  # Assumes "wide" CI = 0.5
    score_I2 = 1.0 - (i_squared / 100)  # Low heterogeneity = high score
    
    # Weighted confidence
    conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
    
    return conf
```

**C. For THEORETICAL / QUALITATIVE**

```python
def calculate_confidence_theoretical(finding: Finding, papers: List[Paper]) -> float:
    """
    Gemini's answer: DON'T quantify. Set conf = -1.0 (MANUAL_REVIEW_REQUIRED).
    This flags the link for HITL approval in Synthesizer GUI.
    """
    return -1.0  # Sentinel value for "needs human judgment"
```

**D. Edge Case: Pure Qualitative**

```python
def calculate_confidence_qualitative(finding: Finding, papers: List[Paper]) -> float:
    """
    Same as theoretical: escalate to human expert.
    """
    return -1.0
```

---

## PART 3: AGENT CLASSIFIER - TWO-PASS TRIAGE

### Gemini's Exact Specification

```python
# agent_classifier.py

import re
from typing import List, Set
from enum import Enum

class PaperType(Enum):
    EXPERIMENTAL_RCT = "experimental_rct"
    OBSERVATIONAL = "observational"
    META_ANALYSIS = "meta_analysis"
    THEORETICAL = "theoretical"
    QUALITATIVE = "qualitative"
    REVIEW = "review"

class AgentClassifier:
    """
    Two-Pass Heuristic Classifier (Gemini's specification)
    Pass 1: Abstract + Title (fast keyword scan)
    Pass 2: Methods section (targeted parse if ambiguous)
    """
    
    # Pass 1 keywords (Gemini's exact list)
    PASS1_KEYWORDS = {
        PaperType.META_ANALYSIS: [
            "systematic review", "meta-analysis", "meta analysis",
            "pooled effect", "forest plot"
        ],
        PaperType.THEORETICAL: [
            "theoretical", "conceptual", "framework", "review",
            # But NOT "systematic review" (that's meta-analysis)
        ],
        PaperType.EXPERIMENTAL_RCT: [
            "RCT", "randomized", "randomised", "control trial",
            "randomly assigned", "placebo"
        ]
    }
    
    # Pass 2 keywords (for Methods section)
    PASS2_KEYWORDS = {
        PaperType.EXPERIMENTAL_RCT: [
            "randomly assigned", "control group", "randomization",
            "double-blind", "placebo"
        ],
        PaperType.OBSERVATIONAL: [
            "we surveyed", "cohort", "regression analysis",
            "cross-sectional", "longitudinal"
        ],
        PaperType.QUALITATIVE: [
            "interviews", "thematic analysis", "ethnographic",
            "grounded theory", "phenomenology"
        ]
    }
    
    def classify(self, paper: Paper) -> Set[PaperType]:
        """
        Returns SET of PaperTypes (hybrids allowed).
        """
        types = set()
        
        # Pass 1: Abstract + Title
        abstract_title = (paper.abstract or "") + " " + (paper.title or "")
        abstract_title_lower = abstract_title.lower()
        
        for paper_type, keywords in self.PASS1_KEYWORDS.items():
            if any(kw in abstract_title_lower for kw in keywords):
                types.add(paper_type)
        
        # If unambiguous, done
        if len(types) == 1:
            return types
        
        # Pass 2: Methods section (if ambiguous or empty)
        if len(types) == 0 or len(types) > 2:
            methods_text = self._extract_methods_section(paper.full_text)
            methods_lower = methods_text.lower()
            
            for paper_type, keywords in self.PASS2_KEYWORDS.items():
                if any(kw in methods_lower for kw in keywords):
                    types.add(paper_type)
        
        # Hybrid handling (Gemini: "This is a goldmine")
        # Example: [EXPERIMENTAL_RCT, THEORETICAL] = RCT with strong theory
        # This is KEPT as multiple types, not forced to one
        
        # Default if still ambiguous
        if len(types) == 0:
            types.add(PaperType.OBSERVATIONAL)  # Conservative default
        
        return types
    
    def _extract_methods_section(self, full_text: str) -> str:
        """
        Extract "Methods" section from full text.
        Simple heuristic: find section starting with "Methods" header.
        """
        if not full_text:
            return ""
        
        # Look for common Methods headers
        patterns = [
            r"## Methods\n(.*?)(?=##|\Z)",
            r"# Methods\n(.*?)(?=#|\Z)",
            r"Methods\n(.*?)(?=\n[A-Z][a-z]+\n|\Z)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
```

---

## PART 4: AGENT PROMPT ROUTER - MULTI-PROMPT MANAGER

### Gemini's Exact Specification

```python
# agent_prompt_router.py

class AgentPromptRouter:
    """
    Multi-Prompt Manager (Gemini's specification)
    - Multiple simple 7-panel templates (one per PaperType)
    - Hybrid papers get MULTIPLE prompts run and merged
    """
    
    PROMPT_TEMPLATES = {
        PaperType.EXPERIMENTAL_RCT: "prompts/7_panel_prompt_RCT.txt",
        PaperType.THEORETICAL: "prompts/7_panel_prompt_THEORY.txt",
        PaperType.META_ANALYSIS: "prompts/7_panel_prompt_META.txt",
        PaperType.OBSERVATIONAL: "prompts/7_panel_prompt_OBSERVATIONAL.txt",
        PaperType.QUALITATIVE: "prompts/7_panel_prompt_QUALITATIVE.txt",
    }
    
    def route(self, paper: Paper, paper_types: Set[PaperType]) -> SevenPanelArtifact:
        """
        Routes to correct prompt(s) based on PaperType tags.
        Handles hybrids by merging multiple prompt outputs.
        """
        if len(paper_types) == 1:
            # Simple case: single type
            return self._run_single_prompt(paper, list(paper_types)[0])
        else:
            # Hybrid case: run multiple prompts and merge
            return self._run_hybrid_prompts(paper, paper_types)
    
    def _run_single_prompt(self, paper: Paper, paper_type: PaperType) -> SevenPanelArtifact:
        """
        Run single 7-panel prompt on full text.
        """
        prompt_file = self.PROMPT_TEMPLATES[paper_type]
        prompt_text = self._load_prompt(prompt_file)
        
        # Call LLM (Anthropic API)
        result = call_llm(prompt_text, paper.full_text)
        
        return self._parse_seven_panel(result)
    
    def _run_hybrid_prompts(self, paper: Paper, paper_types: Set[PaperType]) -> SevenPanelArtifact:
        """
        Hybrid handling (Gemini's specification):
        
        Example: [OBSERVATIONAL, THEORETICAL]
        1. Run OBSERVATIONAL prompt on full text → get Panels 3,4,5 (Context, Methods, Findings)
        2. Run THEORETICAL prompt on Intro+Discussion → get Panels 2,6 (Focus, Discussion)
        3. Merge into single "super-artifact"
        """
        artifact = SevenPanelArtifact()
        
        # Determine which prompts to run
        if PaperType.EXPERIMENTAL_RCT in paper_types or PaperType.OBSERVATIONAL in paper_types:
            # Run empirical prompt on full text
            empirical_type = PaperType.EXPERIMENTAL_RCT if PaperType.EXPERIMENTAL_RCT in paper_types else PaperType.OBSERVATIONAL
            empirical_result = self._run_single_prompt(paper, empirical_type)
            
            # Merge Panels 3,4,5
            artifact.panel_3 = empirical_result.panel_3
            artifact.panel_4 = empirical_result.panel_4
            artifact.panel_5 = empirical_result.panel_5
        
        if PaperType.THEORETICAL in paper_types:
            # Run theoretical prompt on Intro+Discussion only
            intro_discussion = self._extract_intro_discussion(paper.full_text)
            theoretical_result = self._run_single_prompt_on_sections(
                intro_discussion, 
                PaperType.THEORETICAL
            )
            
            # Merge Panels 2,6
            artifact.panel_2 = theoretical_result.panel_2
            artifact.panel_6 = theoretical_result.panel_6
        
        # Panels 1,7 are always from main prompt
        artifact.panel_1 = empirical_result.panel_1 if 'empirical_result' in locals() else None
        artifact.panel_7 = empirical_result.panel_7 if 'empirical_result' in locals() else None
        
        return artifact
```

---

## PART 5: DATA FLOW - OPTION A (PRE-COMPUTED)

### Gemini's Exact Workflow

```
1. INGEST (Human adds DOI)
   └─> User adds DOI to PaperService
   └─> DOI placed in "Awaiting Ingest" queue

2. TRIAGE (HITL Gate - Gemini's addition)
   └─> User reviews title + abstract (cheap to fetch)
   └─> User clicks "Approve for Full Ingest" or "Reject"
   └─> This prevents wasting API cost on irrelevant papers

3. EXTRACTION (The "Upfront Cost")
   └─> Agent_Classifier runs → tags PaperType(s)
   └─> Agent_PromptRouter runs → selects correct 7-panel prompt(s)
   └─> Agent_Finder runs → generates SevenPanelArtifact
   └─> Extract MicroFindings + Set of Support

4. SAVE (To Graph/Database)
   └─> GraphService saves:
       - Paper node (with paper_type tags)
       - SevenPanelArtifact node
       - MicroFinding nodes (with set_of_support JSON)

5. "INSTANT" ACCESS (Gemini's non-negotiable)
   └─> Paper is now "in the library"
   └─> 100% available in Librarian GUI
   └─> All data available to filters:
       - PaperType filter
       - Set of Support filter (N > 50)
       - Measure filter (cortisol)
```

**Critical Insight from Gemini**:

> "The 7-Panel is the product, not the byproduct. The 'Librarian' is the first product. An un-annotated paper is just a 'todo' item, not an 'inventory' item."

This means: **Option A is not wasteful, it's THE WORKFLOW**

---

## PART 6: V17 → V18 MIGRATION PLAN

### Step-by-Step with Gemini's Clarifications

**Phase 1: Database Migration** (Week 1)

```sql
-- Migration 005: Create finding_links table
-- (Already shown in Part 1)

-- Migration 006: Add paper_type to papers table
ALTER TABLE papers ADD COLUMN paper_type TEXT; -- JSON array of types

-- Migration 007: Add set_of_support to findings
ALTER TABLE findings ADD COLUMN set_of_support TEXT; -- JSON

-- Migration 008: Backfill data from v17
-- Convert parent_finding_id relationships to finding_links
INSERT INTO finding_links (source_finding_id, target_finding_id, link_type, weight)
SELECT 
    id AS source_finding_id,
    parent_finding_id AS target_finding_id,
    'TAXONOMIC' AS link_type,  -- All v17 parent links are TAXONOMIC
    1.0 AS weight
FROM findings
WHERE parent_finding_id IS NOT NULL;

-- Extract CAUSAL links from antecedents JSON (more complex, see below)
```

**Phase 2: Implement Agents** (Week 2-3)

```bash
# Create agent modules
touch src/agents/agent_classifier.py
touch src/agents/agent_prompt_router.py
touch src/agents/agent_aggregator.py  # (for Phase 3)
touch src/agents/agent_linker.py      # (for Phase 3)

# Create prompt templates
mkdir -p prompts
touch prompts/7_panel_prompt_RCT.txt
touch prompts/7_panel_prompt_THEORY.txt
touch prompts/7_panel_prompt_META.txt
touch prompts/7_panel_prompt_OBSERVATIONAL.txt
touch prompts/7_panel_prompt_QUALITATIVE.txt

# Copy v17 prompt → prompts/7_panel_prompt_RCT.txt (starting point)
```

**Phase 3: Integrate Set of Support** (Week 4)

```python
# Create setof_support module
touch src/confidence/setof_support.py

# Implement classes (shown in Part 2)
class SetOfSupportCalculator:
    def calculate(self, finding, papers):
        paper_types = self._get_paper_types(papers)
        
        if PaperType.EXPERIMENTAL_RCT in paper_types:
            return calculate_confidence_rct(finding, papers)
        elif PaperType.META_ANALYSIS in paper_types:
            return calculate_confidence_meta(finding, papers[0])
        elif PaperType.THEORETICAL in paper_types:
            return -1.0  # MANUAL_REVIEW_REQUIRED
        elif PaperType.QUALITATIVE in paper_types:
            return -1.0  # MANUAL_REVIEW_REQUIRED
        else:
            return calculate_confidence_rct(finding, papers)  # Default
```

**Phase 4: Update Ingestion Pipeline** (Week 5)

```python
# Modify ingestion flow (Option A - pre-compute)

def ingest_paper(doi: str):
    # 1. Fetch metadata (cheap)
    paper = fetch_paper_metadata(doi)
    
    # 2. Human triage gate (Gemini's addition)
    await_human_approval(paper)
    
    # 3. If approved, full extraction (expensive)
    if paper.approved:
        # Classify
        paper_types = AgentClassifier().classify(paper)
        paper.paper_type = list(paper_types)
        
        # Route to correct prompt(s)
        seven_panel = AgentPromptRouter().route(paper, paper_types)
        
        # Extract findings with Set of Support
        findings = extract_micro_findings(seven_panel.panel_5)
        
        # Save to database
        save_paper(paper)
        save_seven_panel(seven_panel)
        save_findings(findings)
        
        # Now "instantly available" in Librarian
```

**Phase 5: Implement HITL Approval UI** (Week 6-7)

```python
# Create Synthesizer GUI routes

@app.route('/synthesizer/<job_id>/approve', methods=['GET', 'POST'])
def synthesizer_approve(job_id):
    """
    HITL approval interface.
    User sees proposed:
    - Meso-findings (from Agent_Aggregator)
    - Mechanism links (from Agent_Linker)
    - Theoretical/Qualitative links (conf=-1.0)
    
    User can: Approve, Deny, Edit
    """
    pending_proposals = get_pending_proposals(job_id)
    
    if request.method == 'POST':
        # User approved/denied proposals
        for proposal in pending_proposals:
            if request.form.get(f'approve_{proposal.id}'):
                approve_proposal(proposal)
            elif request.form.get(f'deny_{proposal.id}'):
                deny_proposal(proposal)
    
    return render_template('synthesizer_approve.html', proposals=pending_proposals)
```

---

## PART 7: IMPLEMENTATION CHECKLIST

### ✅ Week 1: Database Migration

- [ ] Create `finding_links` table with `link_type` field
- [ ] Add `paper_type` to papers table
- [ ] Add `set_of_support` to findings table
- [ ] Backfill v17 data (parent_finding_id → finding_links)
- [ ] Test: Can query CAUSAL vs TAXONOMIC links separately

### ✅ Week 2: Agent Classifier

- [ ] Implement two-pass classifier (Gemini's exact spec)
- [ ] Test on 20 papers from corpus
- [ ] Validate accuracy (>90% correct classification)
- [ ] Handle hybrids correctly ([RCT, THEORETICAL])

### ✅ Week 3: Agent Prompt Router + Set of Support

- [ ] Create 5 prompt templates (RCT, Theory, Meta, Obs, Qual)
- [ ] Implement hybrid prompt merging
- [ ] Implement confidence formulas (Gemini's exact heuristics)
- [ ] Test on papers of each type
- [ ] Validate confidence scores make sense

### ✅ Week 4: Update Ingestion Pipeline

- [ ] Add human triage gate (Gemini's Option A requirement)
- [ ] Integrate Agent_Classifier into ingestion
- [ ] Integrate Agent_PromptRouter into ingestion
- [ ] Calculate Set of Support during extraction
- [ ] Save paper_type and set_of_support to database

### ✅ Week 5: Librarian GUI

- [ ] Ensure 7-panel "instantly available" (pre-computed)
- [ ] Add PaperType filter
- [ ] Add Set of Support filter (N > X, p < Y)
- [ ] Add Measure filter
- [ ] Test: No 30-second wait (must be instant)

### ✅ Week 6-7: Synthesizer GUI (HITL)

- [ ] Implement Agent_Aggregator (propose meso-findings)
- [ ] Implement Agent_Linker (propose mechanism links)
- [ ] Create approval interface
- [ ] Handle conf=-1.0 (MANUAL_REVIEW_REQUIRED)
- [ ] Test full HITL workflow

---

## PART 8: GEMINI'S "GO/NO-GO" ANSWERS SUMMARY

### Question 1: Triple vs Dual Hierarchy?

**Gemini's Answer**: ✅ **Dual Hierarchy with Two Edge Types**

- TWO node types: Findings, Mechanisms
- TWO edge types: CAUSAL, TAXONOMIC (in Finding hierarchy)
- "Triple" was confusing terminology, now eliminated
- **Solution**: New `finding_links` table with `link_type` field

**Status**: ✅ RESOLVED

---

### Question 2: Set of Support Formulas?

**Gemini's Answer**: ✅ **Concrete Heuristics Provided**

**For RCT**:
```
conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
where:
  score_N = min(N / 200, 1.0)
  score_p = max(0, 1.0 - (p / 0.05))
  score_d = min(|d| / 0.8, 1.0)
```

**For Meta-Analysis**:
```
conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I²)
where:
  score_k = min(k / 20, 1.0)
  score_CI = max(0, 1.0 - (CI_width / 0.5))
  score_I² = 1.0 - (I² / 100)
```

**For Theoretical/Qualitative**:
```
conf = -1.0  # Sentinel: MANUAL_REVIEW_REQUIRED
```

**Status**: ✅ RESOLVED

---

### Question 3: Agent_Classifier How?

**Gemini's Answer**: ✅ **Two-Pass Triage**

- Pass 1: Keyword scan on abstract + title (fast)
- Pass 2: Methods section parse (if ambiguous)
- Hybrids allowed (multi-tag papers)
- Default to OBSERVATIONAL if still unclear

**Status**: ✅ RESOLVED

---

### Question 4: Agent_PromptRouter How?

**Gemini's Answer**: ✅ **Multi-Prompt Manager**

- 5 separate prompt templates (one per PaperType)
- Hybrids run MULTIPLE prompts and merge
- Example: [RCT, THEORETICAL] runs both prompts, merges Panels

**Status**: ✅ RESOLVED

---

### Question 5: Librarian Data Flow?

**Gemini's Answer**: ✅ **Option A (Pre-computed)**

- 7-Panel extraction DURING ingestion (not lazy)
- Human triage gate BEFORE extraction (cost control)
- "Instant" means literally instant (0 wait)
- "7-Panel is the product, not byproduct"

**Status**: ✅ RESOLVED

---

## PART 9: FINAL VERDICT

### 🟢 DEFINITIVE GO - IMPLEMENT V18

**Confidence**: 95% (up from 85%)

**Rationale**:
1. ✅ All "black boxes" specified by Gemini
2. ✅ Database schema clear and implementable
3. ✅ Confidence formulas transparent and tunable
4. ✅ Data flow unambiguous (Option A with HITL gate)
5. ✅ v17 → v18 migration path obvious
6. ✅ No remaining ambiguity

**Risk**: LOW
- Phased approach allows validation at each step
- Can tune confidence weights as needed
- HITL provides quality control
- Database migration is reversible (backups)

**Timeline**: 7 weeks (phased)
- Week 1: Database
- Week 2: Classifier
- Week 3: Prompt Router + Set of Support
- Week 4: Ingestion Pipeline
- Week 5: Librarian GUI
- Week 6-7: Synthesizer GUI (HITL)

**Next Action**: Start Week 1 (Database Migration)

---

## PART 10: GOVERNANCE INTEGRATION

### Track All v18 Decisions in CONVERSATION_LEDGER.yml

**Log This Session**:

```yaml
- session_id: "session-004"
  date: "2025-11-11T18:00:00Z"
  duration_hours: 2.0
  human_request: |
    Analyzed Gemini's answers to critical v18 questions.
    Questions covered: Triple vs Dual hierarchy, Set of Support formulas,
    Agent_Classifier implementation, Agent_PromptRouter design, and
    Librarian vs Synthesizer data flow.
  
  ai_response_summary: |
    Created comprehensive v18 implementation guide with Gemini's
    definitive answers. All ambiguity resolved. Database schema
    specified (finding_links table). Confidence formulas provided
    (exact heuristics). Agent implementations detailed. Data flow
    clarified (Option A - pre-compute with HITL gate).
  
  artifacts_created:
    - "V18_IMPLEMENTATION_GUIDE_FINAL.md"
  
  decisions_made:
    - decision_id: "DEC-004"
  
  context_updates:
    - "v18 architecture validated by Gemini"
    - "finding_links table with link_type is THE solution"
    - "Set of Support formulas: RCT, Meta, Theoretical(-1.0)"
    - "Option A (pre-compute) is the workflow, not wasteful"
  
  next_steps_identified:
    - "Start Week 1: Database migration (finding_links table)"
    - "Test migration on v17 data"
    - "Begin Week 2: Agent_Classifier implementation"

# Add decision for v18 GO
- decision_id: "DEC-004"
  date: "2025-11-11"
  session: "session-004"
  question: "Implement v18 architecture based on Gemini's clarifications?"
  
  chosen: "YES - Implement v18 (phased, 7 weeks)"
  
  alternatives_considered:
    - option: "Stay at v17 (just add governance)"
      pros:
        - "Lower risk"
        - "Faster to deploy"
      cons:
        - "parent_finding_id conflation remains"
        - "Cannot build proper BBN"
        - "No Set of Support"
      rejected_because: |
        Gemini confirmed v17 parent_finding_id is "catastrophically
        flawed" and cannot model both CAUSAL and TAXONOMIC links.
        Staying at v17 means staying broken.
    
    - option: "Implement v18 all at once (7 weeks, one phase)"
      pros:
        - "Faster to complete"
        - "Single integration point"
      cons:
        - "Higher risk"
        - "Harder to rollback"
        - "No validation checkpoints"
      rejected_because: |
        Too much risk. Phased approach allows validation at each step
        and provides rollback points if something fails.
  
  rationale: |
    Gemini's answers resolved ALL critical ambiguities:
    
    1. finding_links table with link_type field solves conflation
    2. Set of Support formulas are concrete and transparent
    3. Agent_Classifier is simple two-pass heuristic
    4. Agent_PromptRouter is multi-template with merge
    5. Option A (pre-compute) is the right data flow
    
    All "black boxes" now specified. Migration path clear.
    Phased approach mitigates risk. v17 is confirmed broken,
    so staying there is not viable.
    
    Confidence: 95% (high)
  
  impact:
    - "7 weeks of focused development (phased)"
    - "Database schema changes (finding_links table)"
    - "New agent modules (Classifier, PromptRouter, Aggregator, Linker)"
    - "Updated ingestion pipeline (Option A workflow)"
    - "HITL approval interface for Synthesizer"
  
  implementation_notes:
    - "Start with database migration (Week 1)"
    - "Test each phase before proceeding"
    - "Log all subsequent decisions in ledger"
    - "Track tuning of confidence weights as we test"
  
  related_intents:
    - "INTENT-002"  # (new: Implement v18 architecture)
```

---

## APPENDIX: GEMINI'S EXACT QUOTES

### On "Triple" vs "Dual" Hierarchy

> "It is a DUAL Hierarchy (Nodes: Findings + Mechanisms). My 'Triple-Hierarchy insight' was confusingly-named. The insight is that the Finding Hierarchy is not one thing. It's a single set of nodes (Findings) connected by TWO different link types (CAUSAL and TAXONOMIC)."

### On parent_finding_id

> "A simple parent_finding_id foreign key is the source of the v17 conflation. [...] This is a catastrophic modeling error that makes the BBN impossible to build."

### On finding_links Solution

> "Clarify: Do we need a NEW finding_links table with a link_type field? YES. 100%. parent_finding_id is insufficient. That is the old, conflated v17 model."

### On Set of Support for Theoretical

> "For THEORETICAL (Non-Quantitative): THIS IS A TRAP. The agent must not quantify this. [...] The agent's job is to extract, not to judge. [...] It sets conf = -1.0 (or MANUAL_REVIEW_REQUIRED). [...] You, the human expert, are presented with the SetOfSupport [...] and you set the confidence. This is the entire point of HITL."

### On Option A (Pre-compute)

> "The 'Librarian' is the first product. The 7-Panel review is the 'first-class artifact' of the system. [...] The 'high API cost upfront' is not a bug; it is the cost of admission. [...] An un-annotated paper (one without a 7-Panel) is just a 'todo' item, not an 'inventory' item."

---

**Document Status**: COMPLETE ✅  
**All Questions**: ANSWERED ✅  
**Implementation Ready**: YES ✅  
**Confidence**: 95% (DEFINITIVE GO)

**Next Step**: Start Week 1 - Database Migration 🚀