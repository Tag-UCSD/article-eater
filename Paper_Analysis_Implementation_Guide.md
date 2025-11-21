# Paper-to-Rules Analysis View - Implementation Guide
## Quick-Start for Priority 1.5 Critical Feature

**Estimated Time**: 6 hours  
**Dependencies**: None (standalone feature)  
**Testing**: 1 hour

---

## FILE CHANGES REQUIRED

### 1. New Backend Route (1 hour)

**Create**: `app/routes_papers.py`

```python
"""
Paper Analysis Routes
Provides reverse lookup: Paper → Rules → Evidence
"""

from flask import Blueprint, render_template
from .artifacts import read_json
from pathlib import Path
from urllib.parse import unquote
import re

bp = Blueprint('papers', __name__)

@bp.route("/paper/<path:paper_id>/analysis", methods=["GET"])
def paper_analysis(paper_id):
    """Show all rules and evidence derived from a specific paper."""
    # URL-decode paper_id (handles DOIs with slashes)
    paper_id = unquote(paper_id)
    
    paper_data = initialize_paper_data(paper_id)
    
    # Search across all jobs
    FINDINGS = Path(__file__).resolve().parent.parent / "findings"
    if FINDINGS.exists():
        for job_dir in FINDINGS.iterdir():
            if not job_dir.is_dir() or job_dir.name.startswith('.'):
                continue
            
            collect_from_shortlist(job_dir, paper_id, paper_data)
            collect_from_evidence(job_dir, paper_id, paper_data)
            collect_from_rules(job_dir, paper_id, paper_data)
    
    # Calculate quality metrics
    paper_data['extraction_score'] = calculate_extraction_score(paper_data)
    paper_data['jobs_referenced'] = list(set(paper_data['jobs_referenced']))
    
    return render_template("paper_analysis.html", paper=paper_data)


def initialize_paper_data(paper_id: str) -> dict:
    """Initialize paper data structure."""
    return {
        'id': paper_id,
        'title': None,
        'year': None,
        'doi': None,
        'authors': None,
        'abstract': None,
        'rules_derived': [],
        'evidence_passages': [],
        'extraction_score': 0.0,
        'jobs_referenced': [],
        'categories': []
    }


def collect_from_shortlist(job_dir: Path, paper_id: str, paper_data: dict):
    """Extract paper metadata from shortlist."""
    shortlist = read_json(job_dir.name, "shortlist")
    if not shortlist:
        return
    
    for item in shortlist.get("topk", []):
        if matches_paper(item, paper_id):
            # Found the paper - extract metadata
            paper_data['title'] = paper_data['title'] or item.get('title')
            paper_data['year'] = paper_data['year'] or item.get('year')
            paper_data['doi'] = paper_data['doi'] or item.get('doi')
            paper_data['authors'] = paper_data['authors'] or item.get('authors')
            paper_data['abstract'] = paper_data['abstract'] or item.get('abstract')
            if 'categories' in item:
                paper_data['categories'].extend(item.get('categories', []))
            if job_dir.name not in paper_data['jobs_referenced']:
                paper_data['jobs_referenced'].append(job_dir.name)


def collect_from_evidence(job_dir: Path, paper_id: str, paper_data: dict):
    """Extract evidence passages from this paper."""
    evidence = read_json(job_dir.name, "evidence")
    if not evidence:
        return
    
    for e in evidence.get("evidence", []):
        if matches_paper(e, paper_id):
            paper_data['evidence_passages'].append({
                'passage': e.get('passage'),
                'method': e.get('method'),
                'job_id': job_dir.name,
                'synthesized': False  # Will update when checking rules
            })
            if job_dir.name not in paper_data['jobs_referenced']:
                paper_data['jobs_referenced'].append(job_dir.name)


def collect_from_rules(job_dir: Path, paper_id: str, paper_data: dict):
    """Extract rules that cite this paper."""
    rules = read_json(job_dir.name, "rules")
    if not rules:
        return
    
    for r in rules.get("rules", []):
        if has_provenance_to_paper(r, paper_id):
            paper_data['rules_derived'].append({
                'rule': r.get('rule'),
                'confidence': r.get('confidence'),
                'job_id': job_dir.name,
                'provenance_count': len(r.get('provenance', []))
            })
            if job_dir.name not in paper_data['jobs_referenced']:
                paper_data['jobs_referenced'].append(job_dir.name)
            
            # Mark evidence as synthesized
            for ev in paper_data['evidence_passages']:
                if ev['job_id'] == job_dir.name:
                    ev['synthesized'] = True


def matches_paper(item: dict, paper_id: str) -> bool:
    """
    Check if item matches paper_id.
    Handles DOI, internal ID, or title matching.
    """
    # Direct DOI match
    if item.get('doi') and normalize_doi(item['doi']) == normalize_doi(paper_id):
        return True
    
    # Internal ID match
    if item.get('id') == paper_id:
        return True
    
    # Title fuzzy match (as fallback)
    if item.get('title') and paper_id.lower() in item['title'].lower():
        return True
    
    return False


def has_provenance_to_paper(rule: dict, paper_id: str) -> bool:
    """Check if rule's provenance includes this paper."""
    for prov in rule.get('provenance', []):
        if matches_paper(prov, paper_id):
            return True
    return False


def normalize_doi(doi: str) -> str:
    """Normalize DOI for comparison."""
    if not doi:
        return ""
    # Remove common prefixes and normalize
    doi = doi.lower().strip()
    doi = re.sub(r'^(doi:|https?://doi\.org/)', '', doi)
    return doi


def calculate_extraction_score(paper_data: dict) -> float:
    """
    Calculate extraction quality score (0.0-1.0).
    
    Based on:
    - Number of rules derived (target: 5+)
    - Number of evidence passages (target: 8+)
    - Synthesis rate (evidence → rules conversion)
    """
    rules_count = len(paper_data['rules_derived'])
    evidence_count = len(paper_data['evidence_passages'])
    
    if rules_count == 0 and evidence_count == 0:
        return 0.0
    
    # Rule contribution (up to 0.5)
    rule_score = min(rules_count / 5.0, 1.0) * 0.5
    
    # Evidence extraction (up to 0.3)
    evidence_score = min(evidence_count / 8.0, 1.0) * 0.3
    
    # Synthesis efficiency (up to 0.2)
    if evidence_count > 0:
        synthesis_rate = rules_count / evidence_count
        synthesis_score = min(synthesis_rate / 0.5, 1.0) * 0.2
    else:
        synthesis_score = 0.0
    
    return rule_score + evidence_score + synthesis_score
```

**Register Blueprint** in `app/app.py`:
```python
# Add after other blueprint registrations
try:
    from .routes_papers import bp as papers_bp
    app.register_blueprint(papers_bp)
except Exception as e:
    print("[WARN] Could not register papers blueprint:", e)
```

---

### 2. New Template (2 hours)

**Create**: `templates/paper_analysis.html`

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
      <h1>{{ paper.title or "Untitled Paper" }}</h1>
      
      <div class="paper-metadata">
        {% if paper.year %}
          <span class="paper-year">{{ paper.year }}</span>
        {% endif %}
        
        {% if paper.authors %}
          <span class="paper-authors">{{ paper.authors[:100] }}{% if paper.authors|length > 100 %}...{% endif %}</span>
        {% endif %}
        
        {% if paper.doi %}
          <div class="paper-doi">
            <span class="meta-label">DOI:</span>
            <a href="https://doi.org/{{ paper.doi }}" 
               target="_blank" 
               rel="noopener"
               class="doi-link">{{ paper.doi }}</a>
          </div>
        {% endif %}
        
        {% if paper.categories %}
          <div class="paper-categories">
            {% for cat in paper.categories|unique %}
              <span class="category-badge">{{ cat }}</span>
            {% endfor %}
          </div>
        {% endif %}
      </div>
      
      {% if paper.abstract %}
        <details class="paper-abstract-toggle">
          <summary>View Abstract</summary>
          <p class="paper-abstract">{{ paper.abstract }}</p>
        </details>
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
          <div class="quality-bar">
            <div class="quality-fill 
                        {% if paper.extraction_score >= 0.8 %}high
                        {% elif paper.extraction_score >= 0.5 %}medium
                        {% else %}low{% endif %}"
                 style="width: {{ (paper.extraction_score * 100) }}%"></div>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="summary-value">{{ paper.jobs_referenced|length }}</div>
          <div class="summary-label">Jobs Referenced</div>
        </div>
      </div>
    </section>
    
    {% if paper.rules_derived %}
    <section class="rules-section">
      <h2>Rules Derived from This Paper ({{ paper.rules_derived|length }})</h2>
      
      <p class="section-description">
        Design rules and principles that cite this paper as supporting evidence.
      </p>
      
      {% for r in paper.rules_derived %}
      <article class="rule-card">
        <h3 class="rule-text">{{ loop.index }}. {{ r.rule }}</h3>
        
        <div class="rule-metadata">
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
            <span class="meta-label">Supporting Sources:</span>
            <span class="meta-value">{{ r.provenance_count }} paper(s)</span>
          </div>
          
          <div class="rule-meta">
            <span class="meta-label">From Job:</span>
            <a href="/rules/{{ r.job_id }}/view" class="meta-link">{{ r.job_id }}</a>
          </div>
        </div>
      </article>
      {% endfor %}
    </section>
    {% else %}
    <div class="info-panel">
      <h2>No Rules Derived</h2>
      <p>
        This paper appeared in {{ paper.jobs_referenced|length }} job(s) but didn't 
        generate any synthesized design rules.
      </p>
      {% if paper.evidence_passages %}
        <p>
          However, {{ paper.evidence_passages|length }} evidence passage(s) were extracted.
          These may be awaiting synthesis or may not have met rule generation criteria.
        </p>
      {% else %}
        <p class="diagnostic">
          <strong>Possible reasons:</strong>
        </p>
        <ul class="diagnostic-list">
          <li>Paper was in shortlist but not selected for RAG extraction</li>
          <li>Extraction focused on other papers with stronger evidence</li>
          <li>Paper's methodology didn't meet synthesis criteria</li>
          <li>Content was primarily review/theory rather than empirical</li>
        </ul>
      {% endif %}
    </div>
    {% endif %}
    
    {% if paper.evidence_passages %}
    <section class="evidence-section">
      <h2>Evidence Passages Extracted ({{ paper.evidence_passages|length }})</h2>
      
      <p class="section-description">
        Specific passages extracted from this paper during RAG processing.
      </p>
      
      {% for e in paper.evidence_passages %}
      <article class="evidence-card {% if e.synthesized %}synthesized{% endif %}">
        <div class="evidence-header">
          <span class="evidence-number">#{{ loop.index }}</span>
          {% if e.synthesized %}
            <span class="synthesis-badge">✓ Synthesized into Rules</span>
          {% else %}
            <span class="synthesis-badge pending">⏳ Awaiting Synthesis</span>
          {% endif %}
        </div>
        
        <blockquote class="evidence-passage">
          {{ e.passage }}
        </blockquote>
        
        {% if e.method %}
          <div class="evidence-method">
            <span class="method-label">Methodology:</span>
            <span class="method-value">{{ e.method }}</span>
          </div>
        {% endif %}
        
        <div class="evidence-meta">
          <span class="meta-label">Extracted in Job:</span>
          <a href="/evidence/{{ e.job_id }}/view" class="meta-link">{{ e.job_id }}</a>
        </div>
      </article>
      {% endfor %}
    </section>
    {% endif %}
    
    {% if not paper.rules_derived and not paper.evidence_passages %}
    <div class="empty-state">
      <p class="empty-icon">📄</p>
      <h2>Paper Found in Shortlist Only</h2>
      <p>
        This paper was identified during metadata triage but hasn't been
        processed for evidence extraction yet.
      </p>
      <ul class="empty-reasons">
        <li>It may be in the queue for RAG processing</li>
        <li>Other papers in the shortlist were prioritized</li>
        <li>Budget limits may have restricted processing</li>
      </ul>
      <div class="empty-actions">
        {% if paper.jobs_referenced %}
          <a href="/shortlist/{{ paper.jobs_referenced[0] }}/view" 
             class="btn-secondary">View Shortlist</a>
        {% endif %}
        <a href="/jobs" class="btn-secondary">← Back to Jobs</a>
      </div>
    </div>
    {% endif %}
    
    {% if paper.jobs_referenced %}
    <section class="jobs-section">
      <h2>Referenced in Jobs</h2>
      <p class="section-description">
        This paper appears in the following research jobs:
      </p>
      <ul class="jobs-list">
        {% for job_id in paper.jobs_referenced %}
          <li class="job-item">
            <code>{{ job_id }}</code>
            <span class="job-links">
              <a href="/shortlist/{{ job_id }}/view">Shortlist</a> |
              <a href="/evidence/{{ job_id }}/view">Evidence</a> |
              <a href="/rules/{{ job_id }}/view">Rules</a>
            </span>
          </li>
        {% endfor %}
      </ul>
    </section>
    {% endif %}
  </div>
</body>
</html>
```

---

### 3. Add CSS Styles (1 hour)

**Append to**: `static/style.css`

```css
/* Paper Analysis Styles */
.paper-header {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.paper-metadata {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  color: #718096;
  font-size: 0.875rem;
}

.paper-year {
  font-weight: 600;
  color: #4a5568;
}

.paper-authors {
  color: #718096;
}

.paper-doi {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.doi-link {
  font-family: monospace;
  font-size: 0.875rem;
}

.paper-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.category-badge {
  background: #edf2f7;
  color: #2d3748;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.paper-abstract-toggle {
  margin-top: 1rem;
  border-top: 1px solid #e2e8f0;
  padding-top: 1rem;
}

.paper-abstract-toggle summary {
  cursor: pointer;
  color: #3182ce;
  font-weight: 500;
}

.paper-abstract {
  margin-top: 0.75rem;
  color: #4a5568;
  line-height: 1.6;
}

/* Extraction Summary Grid */
.extraction-summary {
  margin-bottom: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.summary-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
}

.summary-label {
  font-size: 0.875rem;
  color: #718096;
  margin-top: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.quality-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.quality-fill {
  height: 100%;
  transition: width 0.3s;
}

.quality-fill.high {
  background: #48bb78;
}

.quality-fill.medium {
  background: #ed8936;
}

.quality-fill.low {
  background: #e53e3e;
}

/* Evidence Cards Enhanced */
.evidence-card.synthesized {
  border-left-color: #48bb78;
}

.evidence-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.evidence-number {
  font-weight: 700;
  color: #2d3748;
}

.synthesis-badge {
  background: #c6f6d5;
  color: #22543d;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.synthesis-badge.pending {
  background: #fefcbf;
  color: #744210;
}

/* Info Panel (Not Empty, Just Info) */
.info-panel {
  background: #ebf8ff;
  border-left: 4px solid #3182ce;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.info-panel h2 {
  color: #2c5282;
  margin-bottom: 0.75rem;
}

.info-panel p {
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.diagnostic {
  font-weight: 600;
  margin-top: 1rem;
}

.diagnostic-list {
  list-style: disc;
  padding-left: 1.5rem;
  color: #4a5568;
}

.diagnostic-list li {
  margin: 0.5rem 0;
}

/* Jobs List */
.jobs-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.jobs-list {
  list-style: none;
  padding: 0;
}

.job-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.job-item:last-child {
  border-bottom: none;
}

.job-item code {
  font-size: 0.875rem;
  background: #edf2f7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.job-links {
  font-size: 0.875rem;
}

.job-links a {
  color: #3182ce;
}
```

---

### 4. Add Clickable Links to Existing Views (2 hours)

**A. In Rules View** (`templates/rules_view.html`):

Find the provenance list section and add click handlers:

```html
<!-- BEFORE -->
<li class="provenance-item">
  <span class="provenance-title">{{ p.title or "Untitled" }}</span>
  {% if p.year %}<span class="provenance-year">({{ p.year }})</span>{% endif %}
  {% if p.doi %}
    <a href="https://doi.org/{{ p.doi }}" target="_blank">{{ p.doi }}</a>
  {% endif %}
</li>

<!-- AFTER -->
<li class="provenance-item">
  {% if p.doi %}
    <a href="/paper/{{ p.doi|urlencode }}/analysis" class="provenance-paper-link">
      <span class="provenance-title">{{ p.title or "Untitled" }}</span>
      {% if p.year %}<span class="provenance-year">({{ p.year }})</span>{% endif %}
    </a>
    <a href="https://doi.org/{{ p.doi }}" 
       target="_blank" 
       class="doi-external"
       title="View at publisher">🔗</a>
  {% else %}
    <span class="provenance-title">{{ p.title or "Untitled" }}</span>
    {% if p.year %}<span class="provenance-year">({{ p.year }})</span>{% endif %}
  {% endif %}
</li>
```

**B. In Evidence View** (`templates/evidence_view.html`):

Make paper titles clickable:

```html
<!-- Find the evidence header section -->
<header class="evidence-header">
  {% if e.doi %}
    <h3 class="evidence-source">
      <a href="/paper/{{ e.doi|urlencode }}/analysis" class="paper-title-link">
        {{ e.title or "Untitled Source" }}
      </a>
      {% if e.year %}<span class="source-year">({{ e.year }})</span>{% endif %}
    </h3>
  {% else %}
    <h3 class="evidence-source">
      {{ e.title or "Untitled Source" }}
      {% if e.year %}<span class="source-year">({{ e.year }})</span>{% endif %}
    </h3>
  {% endif %}
</header>
```

**C. In Shortlist View** (`templates/shortlist_view.html`):

Add "Analyze" link to each paper card:

```html
<!-- In the paper-card structure -->
<article class="paper-card">
  <h3 class="paper-title">
    {{ loop.index }}. {{ it.title or "Untitled" }}
    {% if it.year %}<span class="paper-year">({{ it.year }})</span>{% endif %}
  </h3>
  
  <!-- ADD THIS -->
  {% if it.doi %}
    <div class="paper-actions">
      <a href="/paper/{{ it.doi|urlencode }}/analysis" 
         class="btn-sm btn-analysis">
        📊 View Analysis
      </a>
    </div>
  {% endif %}
  
  <!-- Rest of card content -->
</article>
```

---

## TESTING CHECKLIST

**Test Case 1: Paper with Complete Data**
- [ ] Navigate to paper that has rules, evidence, and appears in shortlist
- [ ] Verify all metrics display correctly
- [ ] Check that rules link back to job views
- [ ] Confirm evidence passages show synthesis status

**Test Case 2: Paper with No Rules**
- [ ] Navigate to paper that's in shortlist but has no rules
- [ ] Verify helpful diagnostic message appears
- [ ] Check that reasons are relevant and actionable

**Test Case 3: DOI Handling**
- [ ] Test with DOI containing slashes (10.1234/foo/bar)
- [ ] Test with URL-encoded DOI
- [ ] Verify DOI matching works across all views

**Test Case 4: Multi-Job Paper**
- [ ] Create paper that appears in 2+ jobs
- [ ] Verify all jobs listed in "Referenced in Jobs" section
- [ ] Check that metrics aggregate across jobs

**Test Case 5: Link Integration**
- [ ] Click paper link from rules view provenance
- [ ] Click paper link from evidence view title
- [ ] Click "View Analysis" from shortlist
- [ ] Verify all paths lead to correct paper analysis

**Test Case 6: Empty States**
- [ ] Test paper with only shortlist presence
- [ ] Test paper with evidence but no rules
- [ ] Verify each empty state provides appropriate guidance

---

## DEPLOYMENT

1. Add new files: `routes_papers.py`, `paper_analysis.html`
2. Update existing files: `app.py`, `rules_view.html`, `evidence_view.html`, `shortlist_view.html`, `style.css`
3. Test locally with sample job data
4. Deploy to staging
5. User acceptance testing
6. Production deployment

**Rollback Plan**: 
- Blueprint registration can be commented out without affecting existing functionality
- New route is standalone, no changes to database or core logic

---

**Implementation Priority**: P1.5 (Critical Gap)  
**Estimated Total Time**: 6 hours + 1 hour testing  
**User Value**: High - Enables research validation and quality assessment