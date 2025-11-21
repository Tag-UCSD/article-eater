# Article Eater Enhancement Analysis
## Paper-to-Rules View + Revitalized Components Evaluation

**Date**: November 8, 2025  
**Analysis Focus**: Missing article-level inspection + Integration feasibility of revitalized modules

---

## PART 1: CRITICAL MISSING FEATURE - PAPER-TO-RULES VIEW

### 1.1 Problem Statement

**Current System Gap**: Users can see rules with provenance, but cannot answer:
- "What rules did this specific paper generate?"
- "How influential is paper X in my evidence base?"
- "Which papers from my shortlist didn't contribute any rules?"
- "Does this highly-cited paper actually support the claims I'm making?"

**Current Flow (One-Directional)**:
```
Rule → View Details → Provenance List → Links to multiple papers
```

**Missing Flow (Reverse Lookup)**:
```
Paper → All Rules Derived → Evidence Passages → Validation
```

### 1.2 Use Cases

**Research Quality Assessment**:
- Researcher notices Rule #5 cites Paper A as provenance
- Wants to verify: "Does Paper A really support this rule?"
- Needs to see: All rules attributed to Paper A, evidence passages extracted
- Current system: Must manually search through all rules

**Literature Gap Analysis**:
- Shortlist contains 20 papers
- Rules reference only 12 papers
- Question: "Why didn't the other 8 papers contribute?"
- Current system: No way to identify non-contributing papers

**Source Validation**:
- Peer reviewer questions Rule #3's evidence base
- Needs to show: "Here are ALL rules derived from the cited papers"
- Current system: Can only show individual rule provenance

**Productivity Enhancement**:
- Researcher finds influential paper in field
- Wants to prioritize: "Did our RAG extract maximum value from this?"
- Current system: Cannot assess per-paper extraction completeness

### 1.3 Proposed Implementation

**New Route**: `/paper/<paper_id>/analysis`

**Page Structure**:
```
PAPER ANALYSIS VIEW
├── Header
│   ├── Paper metadata (title, authors, year, DOI)
│   ├── Link to full text
│   └── Shortlist position (if applicable)
│
├── Extraction Summary
│   ├── Total rules derived: 5
│   ├── Total evidence passages: 8
│   ├── Extraction quality score: 0.82
│   └── Categories covered: natural_lighting, biophilic_design
│
├── Rules Derived from This Paper
│   ├── Rule #3: "Natural light reduces cortisol levels"
│   │   ├── Confidence: 0.85
│   │   ├── Evidence passage: "Study found 23% reduction in salivary cortisol..."
│   │   ├── Method: RCT, N=120
│   │   └── Co-cited with: Paper B, Paper C
│   │
│   ├── Rule #7: "Window access improves sleep quality"
│   │   └── [similar structure]
│   │
│   └── [Additional rules...]
│
├── Evidence Passages Not Yet Synthesized
│   ├── Passage 1: "Participants reported higher satisfaction..."
│   │   └── Status: Awaiting rule synthesis
│   └── [More passages...]
│
└── Related Papers (Optional - if revitalized enrichment enabled)
    └── "More papers on natural_lighting? [5 suggestions]"
```

**Backend Implementation** (`app/routes_papers.py` - NEW):
```python
from flask import Blueprint, render_template
from .artifacts import read_json
from pathlib import Path

bp = Blueprint('papers', __name__)

@bp.route("/paper/<paper_id>/analysis", methods=["GET"])
def paper_analysis(paper_id):
    """
    Show all rules and evidence derived from a specific paper.
    paper_id can be DOI (URL-encoded) or internal identifier.
    """
    # Find all jobs
    FINDINGS = Path(__file__).resolve().parent.parent / "findings"
    
    paper_data = {
        'id': paper_id,
        'title': None,
        'year': None,
        'doi': None,
        'rules_derived': [],
        'evidence_passages': [],
        'extraction_score': 0.0
    }
    
    # Search across all jobs for this paper
    if FINDINGS.exists():
        for job_dir in FINDINGS.iterdir():
            if not job_dir.is_dir():
                continue
            
            # Check shortlist for paper metadata
            shortlist = read_json(job_dir.name, "shortlist")
            if shortlist:
                for item in shortlist.get("topk", []):
                    if matches_paper(item, paper_id):
                        paper_data['title'] = item.get('title')
                        paper_data['year'] = item.get('year')
                        paper_data['doi'] = item.get('doi')
            
            # Check evidence for passages from this paper
            evidence = read_json(job_dir.name, "evidence")
            if evidence:
                for e in evidence.get("evidence", []):
                    if matches_paper(e, paper_id):
                        paper_data['evidence_passages'].append({
                            'passage': e.get('passage'),
                            'method': e.get('method'),
                            'job_id': job_dir.name
                        })
            
            # Check rules for those citing this paper
            rules = read_json(job_dir.name, "rules")
            if rules:
                for r in rules.get("rules", []):
                    if has_provenance_to_paper(r, paper_id):
                        paper_data['rules_derived'].append({
                            'rule': r.get('rule'),
                            'confidence': r.get('confidence'),
                            'job_id': job_dir.name
                        })
    
    # Calculate extraction score
    paper_data['extraction_score'] = calculate_extraction_score(paper_data)
    
    return render_template("paper_analysis.html", paper=paper_data)


def matches_paper(item: dict, paper_id: str) -> bool:
    """Check if item matches paper_id (DOI or internal ID)."""
    return (
        item.get('doi') == paper_id or
        item.get('id') == paper_id or
        normalize_doi(item.get('doi', '')) == normalize_doi(paper_id)
    )


def has_provenance_to_paper(rule: dict, paper_id: str) -> bool:
    """Check if rule's provenance includes this paper."""
    for prov in rule.get('provenance', []):
        if matches_paper(prov, paper_id):
            return True
    return False


def calculate_extraction_score(paper_data: dict) -> float:
    """
    Score extraction quality: 0.0-1.0
    Based on: number of rules, evidence diversity, confidence levels
    """
    rules_count = len(paper_data['rules_derived'])
    evidence_count = len(paper_data['evidence_passages'])
    
    if rules_count == 0:
        return 0.0
    
    # Simple heuristic
    base_score = min(rules_count / 5.0, 1.0) * 0.6  # Up to 0.6 for rule count
    evidence_score = min(evidence_count / 8.0, 1.0) * 0.4  # Up to 0.4 for evidence
    
    return base_score + evidence_score
```

**Template** (`templates/paper_analysis.html` - NEW):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Paper Analysis — {{ paper.title or paper.id }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  {% include '_partials/nav.html' %}
  
  <div class="container">
    <div class="breadcrumb">
      <a href="/jobs">Jobs</a> &raquo;
      <span class="current">Paper Analysis</span>
    </div>
    
    <header class="paper-header">
      <h1>{{ paper.title or "Paper Analysis" }}</h1>
      {% if paper.year %}
        <p class="paper-meta">{{ paper.year }}</p>
      {% endif %}
      {% if paper.doi %}
        <p class="paper-doi">
          DOI: <a href="https://doi.org/{{ paper.doi }}" 
                  target="_blank" 
                  rel="noopener">{{ paper.doi }}</a>
        </p>
      {% endif %}
    </header>
    
    <section class="extraction-summary">
      <h2>Extraction Summary</h2>
      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-value">{{ paper.rules_derived|length }}</div>
          <div class="summary-label">Rules Derived</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ paper.evidence_passages|length }}</div>
          <div class="summary-label">Evidence Passages</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ (paper.extraction_score * 100)|round }}%</div>
          <div class="summary-label">Extraction Quality</div>
        </div>
      </div>
    </section>
    
    {% if paper.rules_derived %}
    <section class="rules-section">
      <h2>Rules Derived from This Paper</h2>
      
      {% for r in paper.rules_derived %}
      <article class="rule-card">
        <h3 class="rule-text">{{ r.rule }}</h3>
        
        {% if r.confidence %}
        <div class="rule-confidence">
          <span class="confidence-label">Confidence:</span>
          <span class="confidence-value">{{ (r.confidence * 100)|round }}%</span>
          <div class="confidence-bar">
            <div class="confidence-fill" 
                 style="width: {{ (r.confidence * 100) }}%"></div>
          </div>
        </div>
        {% endif %}
        
        <div class="rule-meta">
          <span class="meta-label">From Job:</span>
          <a href="/rules/{{ r.job_id }}/view" class="meta-link">{{ r.job_id }}</a>
        </div>
      </article>
      {% endfor %}
    </section>
    {% else %}
    <div class="empty-state">
      <p class="empty-icon">📋</p>
      <h2>No Rules Derived</h2>
      <p>
        This paper appeared in the shortlist but didn't generate any design rules.
        Possible reasons:
      </p>
      <ul class="empty-reasons">
        <li>RAG extraction focused on other papers with stronger evidence</li>
        <li>Paper's methodology didn't meet synthesis criteria</li>
        <li>Evidence was extracted but not yet synthesized into rules</li>
      </ul>
    </div>
    {% endif %}
    
    {% if paper.evidence_passages %}
    <section class="evidence-section">
      <h2>Evidence Passages Extracted</h2>
      
      {% for e in paper.evidence_passages %}
      <article class="evidence-card">
        <blockquote class="evidence-passage">
          {{ e.passage }}
        </blockquote>
        
        {% if e.method %}
        <div class="evidence-method">
          <span class="method-label">Method:</span>
          <span class="method-value">{{ e.method }}</span>
        </div>
        {% endif %}
        
        <div class="evidence-meta">
          <span class="meta-label">From Job:</span>
          <a href="/evidence/{{ e.job_id }}/view" class="meta-link">{{ e.job_id }}</a>
        </div>
      </article>
      {% endfor %}
    </section>
    {% endif %}
  </div>
</body>
</html>
```

**Integration Points**:

1. **From Rules View**: Add "View paper analysis" link on each provenance item
2. **From Evidence View**: Make paper titles clickable → paper analysis
3. **From Shortlist View**: Add "Analysis" link next to each paper
4. **From Jobs Index**: Add "Paper Analysis" tab (optional)

**Priority**: **P1.5** (Between Critical and High-Value)  
**Estimated Effort**: 6 hours  
**Dependencies**: None (can be implemented independently)

---

## PART 2: REVITALIZED COMPONENTS EVALUATION

### 2.1 Component Overview

The BUILD_COMPLETE/revitalized directory contains four sophisticated modules:

1. **Interaction Analysis** (`interaction_analysis.py`)
   - Detects synergistic/destructive interactions between rules
   - Example: natural_light + plants → stress_reduction (synergistic)
   - Example: natural_light + glare → stress_reduction (destructive)

2. **Prima Facie Categorization** (`categorization.py`)
   - Auto-categorizes papers into 17 architecture domains
   - Categories: natural_lighting, acoustics, spatial_layout, biophilic_design, etc.
   - Uses keyword matching + LLM for ambiguous cases

3. **Auto-Suggest Enrichment** (`enrichment.py`)
   - Suggests related papers when evidence is weak
   - Triggers: <3 supporting articles OR confidence <0.7
   - Uses external RAG to find papers NOT in collection

4. **Rule Review UI** (HTML/JS components)
   - Interactive interface for reviewing and refining rules
   - Batch operations, filtering, search

### 2.2 Fit Assessment

#### ✅ HIGHLY BENEFICIAL: Prima Facie Categorization

**Alignment**: ★★★★★ (5/5)

**Why It Fits**:
- Article Eater already processes architecture research papers
- Categories match domain: lighting, acoustics, spatial, biophilic, thermal
- Enhances metadata-first approach with semantic grouping
- Enables: "Show me all natural_lighting papers in my collection"

**Integration Benefits**:
1. **Better Shortlist Organization**: Group by category before review
2. **Gap Analysis**: "I have 15 lighting papers but only 2 on acoustics"
3. **Targeted Searches**: "Find more papers on biophilic_design"
4. **Category-Based Rules**: "Generate rules for spatial_layout category only"

**Implementation Path**:
```python
# During ingestion, after Semantic Scholar fetch
from categorization import categorize_paper

for paper in shortlist:
    categories = categorize_paper(
        title=paper['title'],
        abstract=paper['abstract'],
        keywords=paper.get('keywords', '')
    )
    paper['categories'] = categories  # ['natural_lighting', 'biophilic_design']
    paper['primary_category'] = categories[0] if categories else 'uncategorized'
```

**UI Enhancement**:
- Shortlist view: Group papers by category
- Jobs index: Show category distribution (5 lighting, 3 acoustics, 2 spatial)
- Filters: "Show only natural_lighting papers"

**Estimated Integration**: 8 hours  
**Priority**: P2 (High Value)  
**Recommendation**: **INTEGRATE**

---

#### ⚠️ CONDITIONALLY BENEFICIAL: Interaction Analysis

**Alignment**: ★★★☆☆ (3/5)

**Why It's Useful**:
- Detects when rules interact (synergy or destructive interference)
- Example: natural_light + glare might counteract stress_reduction
- Adds sophistication to Bayesian network exports

**Why It's Conditional**:
- Requires mature rule base (50+ rules) to find meaningful interactions
- Most Article Eater users likely processing 5-20 rules per job
- Complex UI needed to display interaction graphs
- Academic validation required (are detected interactions real?)

**When to Integrate**:
1. **Later Stage**: After user base grows and jobs accumulate
2. **Advanced Users**: Researchers doing meta-analyses across multiple jobs
3. **Network Visualization Ready**: When Bayesian network UI exists

**Current System Readiness**: ⚠️ Not Yet
- Rules currently job-isolated (no cross-job analysis)
- No network visualization (D3.js, Cytoscape)
- Users focused on single-job workflows

**Estimated Integration**: 20 hours (including interaction visualization)  
**Priority**: P4 (Future Enhancement)  
**Recommendation**: **DEFER until v2.0 with network features**

---

#### ✅ MODERATELY BENEFICIAL: Auto-Suggest Enrichment

**Alignment**: ★★★★☆ (4/5)

**Why It Fits**:
- Addresses real need: "This rule only has 2 papers supporting it"
- Extends metadata-first approach to continuous improvement
- Uses existing RAG infrastructure (OpenAI/Anthropic)

**Why Not Perfect Fit**:
- Article Eater designed for batch processing, not iterative refinement
- Budget concerns: Additional RAG calls for suggestions cost money
- UX complexity: Where do suggested papers go? New job or existing?

**Integration Benefits**:
1. **Quality Flagging**: Highlight weak rules (<3 sources) in rules view
2. **Targeted Suggestions**: "Find 3 more papers on 'curved walls reduce anxiety'"
3. **Literature Completeness**: "Your rule is based on 2015 papers; here are 5 from 2023-2024"

**Implementation Path**:
```python
# After rule synthesis
from enrichment import should_suggest_for_rule, generate_search_query

for rule in synthesized_rules:
    needs_enrichment, reason = should_suggest_for_rule(rule)
    if needs_enrichment:
        rule['enrichment_suggested'] = True
        rule['enrichment_reason'] = reason  # 'weak_evidence' or 'low_confidence'
        rule['suggested_query'] = generate_search_query(rule)
```

**UI Enhancement**:
- Rules view: Badge on weak rules: "⚠️ Only 2 sources - Find more?"
- Click → Modal: "Search Semantic Scholar for additional evidence?"
- Option: Add to current job OR create enrichment job

**Trade-offs**:
- **Pro**: Improves research rigor
- **Pro**: Guides users toward completeness
- **Con**: Additional API costs
- **Con**: UX complexity (managing suggested papers)

**Estimated Integration**: 12 hours  
**Priority**: P3 (Polish)  
**Recommendation**: **INTEGRATE with user opt-in**  
- Default: OFF (no automatic suggestions)
- Enable: In RAG settings, checkbox "Suggest enrichment for weak rules"
- Display: Only when explicitly requested

---

#### ❌ LOW FIT: Rule Review UI

**Alignment**: ★★☆☆☆ (2/5)

**Why It Doesn't Fit Well**:
- Article Eater already has rule views
- Revitalized UI assumes database-backed editing
- Current system: JSON files, read-only views
- Batch operations less relevant for 5-20 rules per job

**What's Useful**:
- Filtering/search patterns (could adapt for shortlist view)
- Batch selection UI (could use for multi-job operations)

**What's Not Useful**:
- Editing individual rules (not current workflow)
- Database queries (system uses JSON artifacts)
- Complex review workflow (users want simple export)

**Estimated Integration**: 25 hours (significant refactoring)  
**Priority**: N/A  
**Recommendation**: **DO NOT INTEGRATE**  
- Extract useful patterns (filters, search) for shortlist view
- Keep current read-only, export-focused rule views

---

### 2.3 Integration Roadmap

**Phase 1: Paper Analysis (Immediate)**
- [ ] Implement `/paper/<id>/analysis` route
- [ ] Create paper_analysis.html template
- [ ] Add clickable links from existing views
- [ ] Test with multi-job scenarios

**Phase 2: Categorization (Near-Term)**
- [ ] Integrate categorization during ingestion
- [ ] Add category badges to shortlist view
- [ ] Implement category filtering
- [ ] Display category distribution in jobs index

**Phase 3: Enrichment (Mid-Term)**
- [ ] Add "needs enrichment" detection to rules synthesis
- [ ] Create suggestion UI with opt-in trigger
- [ ] Implement suggested paper workflow
- [ ] Add budget tracking for suggestion searches

**Phase 4: Interaction Analysis (Long-Term / V2.0)**
- [ ] Defer until cross-job analysis exists
- [ ] Defer until network visualization implemented
- [ ] Defer until user base validates need

---

## PART 3: RECOMMENDATIONS SUMMARY

### 3.1 Implement Immediately

1. **Paper-to-Rules View** ✅
   - Critical missing feature
   - 6 hours implementation
   - High research value
   - No dependencies

2. **Prima Facie Categorization** ✅
   - Perfect fit for current workflow
   - 8 hours integration
   - Enhances existing features
   - Minimal new UI needed

### 3.2 Implement with Controls

3. **Auto-Suggest Enrichment** ⚠️
   - Valuable but requires opt-in
   - 12 hours integration
   - Add budget controls
   - User-triggered only (not automatic)

### 3.3 Defer to Future Version

4. **Interaction Analysis** ⏸️
   - Powerful but premature
   - 20+ hours with visualization
   - Wait for network features
   - Consider for v2.0

5. **Rule Review UI** ❌
   - Poor fit for current architecture
   - 25 hours significant refactoring
   - Doesn't match workflow
   - Extract patterns only

### 3.4 Revised Priority List

**Updated Implementation Priorities**:

**Priority 1 (Critical - 13 hours)**:
- Global navigation
- Pipeline indicators
- Job state badges
- Enhanced ingest
- Monitor auto-refresh

**Priority 1.5 (Critical Gap - 6 hours)**: ← NEW
- **Paper-to-Rules Analysis View**

**Priority 2 (High Value - 25 hours)**: ← EXPANDED
- Evidence view enhancements (3h)
- Rules view enhancements (3h)
- RAG settings improvements (4h)
- Empty states (3h)
- Event log display (4h)
- **Prima Facie Categorization** (8h) ← NEW

**Priority 3 (Polish - 39 hours)**: ← EXPANDED
- Microcopy (4h)
- Metrics dashboard (5h)
- Accessibility (6h)
- Visual design (8h)
- Loading states (4h)
- **Auto-Suggest Enrichment** (12h) ← NEW

**Priority 4 (Future / V2.0)**:
- Interaction Analysis (with network viz)
- Cross-job meta-analysis
- Advanced Bayesian network features

---

## PART 4: ACADEMIC JUSTIFICATION

### 4.1 Paper-Level Analysis (Cognitive Science Foundation)

The need for paper-to-rules reverse lookup is grounded in established research on source monitoring and knowledge validation:

**Source Monitoring Theory** (Johnson et al., 1993):
- Researchers must track origin of claims for credibility assessment
- External source memory requires explicit attribution mechanisms
- System should support both forward (rule→source) and backward (source→rules) retrieval

**Evidence Integration** (Rapp & Braasch, 2014):
- Multiple-source comprehension requires comparing claims across documents
- Readers benefit from aggregated views showing all claims from single source
- Facilitates detection of contradictions and corroborating evidence

**Citation**: 
Johnson, M. K., Hashtroudi, S., & Lindsay, D. S. (1993). Source monitoring. *Psychological Bulletin*, 114(1), 3-28.

Rapp, D. N., & Braasch, J. L. G. (2014). Processing inaccurate information: Theoretical and applied perspectives from cognitive science and the educational sciences. *MIT Press*.

### 4.2 Categorization (Information Architecture)

Prima facie categorization aligns with faceted classification theory:

**Faceted Classification** (Ranganathan, 1967):
- Multi-dimensional categorization superior to single hierarchies
- Architecture domain naturally splits into facets: lighting, acoustics, spatial, thermal
- Enables flexible navigation and discovery

**Category-Based Induction** (Heit, 2000):
- People make stronger inferences when evidence comes from diverse categories
- System should highlight category coverage: "5 lighting studies, 2 acoustic studies"
- Supports meta-cognitive awareness of evidence base breadth

**Citation**:
Ranganathan, S. R. (1967). *Prolegomena to library classification* (3rd ed.). Asia Publishing House.

Heit, E. (2000). Properties of inductive reasoning. *Psychonomic Bulletin & Review*, 7(4), 569-592.

### 4.3 Enrichment Suggestions (Metacognition)

Auto-suggest enrichment supports metacognitive monitoring:

**Metacognitive Monitoring** (Nelson & Narens, 1990):
- Researchers must judge adequacy of evidence base
- System should make weakness salient: "Only 2 sources for this rule"
- Provides scaffolding for improving research quality

**Optimal Stopping in Information Search** (Pirolli & Card, 1999):
- Information foraging theory: balance cost vs. value of additional search
- Suggestion system should indicate diminishing returns
- Helps researchers decide when evidence is "sufficient"

**Citation**:
Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 26, pp. 125-173). Academic Press.

Pirolli, P., & Card, S. (1999). Information foraging. *Psychological Review*, 106(4), 643-675.

---

## CONCLUSION

**Immediate Actions**:
1. ✅ Implement Paper-to-Rules Analysis View (P1.5, 6 hours)
2. ✅ Integrate Prima Facie Categorization (P2, 8 hours)
3. ⚠️ Add Auto-Suggest Enrichment with opt-in (P3, 12 hours)

**Defer**:
4. ⏸️ Interaction Analysis to v2.0 (needs network visualization)
5. ❌ Rule Review UI (poor fit for current architecture)

**Total Recommended Integration**: 26 hours across 3 features

The paper-to-rules view addresses a critical missing capability for research validation. Categorization enhances the existing metadata-first approach with semantic organization. Enrichment suggestions provide valuable quality scaffolding when users opt in. Together, these additions strengthen Article Eater's theoretical rigor while maintaining the system's core focus on efficient, cost-aware evidence synthesis.

---

**Report Version**: 1.0  
**Date**: November 8, 2025