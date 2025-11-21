# CNfA Requirements Integration Analysis
## Article Eater v15.8.1 - Hierarchical Rules & Meta-Review Logic

**Date**: November 8, 2025  
**Version Analyzed**: v15.8.1  
**Context**: Your uploaded architecture diagrams + theoretical requirements

---

## EXECUTIVE SUMMARY

Your requirements reveal that **Article Eater v15.8.1 is architecturally incomplete** for true CNfA (Cognitive Neuroscience for Architecture) evidence synthesis. The current system treats rules as **flat, isolated findings** when CNfA requires:

1. **Hierarchical rule structures** (surface → mechanism → principle)
2. **Meta-review logic** (aggregating across operational measures)
3. **Mechanism extraction** (not just correlations)
4. **Toggle-capable display** (flat list AND hierarchical tree AND network graph)

**Critical Gap**: v15.8.1 uses JSON files with no relational structure. The revitalized components in `BUILD_COMPLETE/` have the **database schema** needed for hierarchical rules, but aren't integrated.

**Recommendation**: **Hybrid approach** - Keep v15.8.1's lightweight JSON for simple jobs, but add optional database mode for complex hierarchical analysis.

---

## PART 1: YOUR REQUIREMENTS MAPPED TO SYSTEM CAPABILITIES

### Requirement 1: Rule Granularity Levels

**What You Need**:
```
MICRO-RULES (Operational/Sensor Level):
- "Indoor plants → ↓ salivary cortisol (p<.05, N=32)" [Study A]
- "Indoor plants → ↓ heart rate (p<.01, N=50)" [Study B]  
- "Indoor plants → ↓ blood pressure (p<.03, N=120)" [Study C]
- "Indoor plants → ↑ HRV (p<.02, N=85)" [Study D]

MESO-RULES (Construct Level):
- "Indoor plants → stress reduction"
  └─ Aggregated from: cortisol(A), HR(B), BP(C), HRV(D)
  └─ Confidence: 0.89 (triangulated from 4 operational measures)

MACRO-RULES (Theoretical Level):
- "Biophilic design → improved affective state"
  └─ Via pathways: stress reduction, attention restoration, mood regulation
  └─ Explained by: Predictive Processing, Embodied Cognition
```

**Current v15.8.1 Capability**: ❌ **NONE**

Current rule schema (JSON):
```json
{
  "rule": "Indoor plants reduce stress",
  "confidence": 0.85,
  "provenance": [
    {"title": "Study A", "doi": "10.1234/abc", "year": 2020},
    {"title": "Study B", "doi": "10.5678/def", "year": 2021}
  ]
}
```

**Problems**:
- No distinction between micro/meso/macro levels
- No representation of operational measures (cortisol vs HR vs BP)
- No aggregation logic
- No mechanism field
- No hierarchical parent-child relationships

**Revitalized Schema Capability**: ✅ **PARTIAL**

The `BUILD_COMPLETE/revitalized/models.py` has:
```python
class Rule(Base):
    consequent = Column(String)           # "stress_reduction"
    antecedents = Column(Text)            # ["plants", "natural_light"]
    weight = Column(Float)                # 0.85
    rule_type = Column(String)            # Could be: 'micro', 'meso', 'macro'
```

**Missing**: 
- No `parent_rule_id` field for hierarchy
- No `operational_measure` field (cortisol, HR, BP)
- No `mechanism` field (predictive processing, embodied cognition)
- No `rule_level` field (micro/meso/macro)

---

### Requirement 2: Mechanism Extraction

**What You Need**:

From 7-panel analysis, extract not just:
- ❌ "Curved walls → reduced anxiety" (correlation only)

But also:
- ✅ "Curved walls → reduced anxiety **via predictive processing fluency**" (mechanism)
- ✅ "Curved walls → reduced anxiety **via motor simulation of safe enclosure**" (mechanism)

**Current v15.8.1 Capability**: ⚠️ **PARTIAL**

The 7-panel prompt (in `BUILD_COMPLETE/tasks.py`) requests:
- Panel 6: "Discussion & Theoretical Insights"
- Field: `theoretical_frameworks` (JSON list)

Example extraction:
```json
{
  "theoretical_frameworks": [
    "Predictive Processing",
    "Embodied Cognition", 
    "Allostasis"
  ]
}
```

**Problem**: Frameworks extracted at **article level**, not **rule level**. 

You need:
```json
{
  "rule": "Curved walls → reduced anxiety",
  "mechanism": "predictive_processing_fluency",
  "mechanism_description": "Curved forms reduce prediction error...",
  "theoretical_framework": "Predictive Processing",
  "evidence_for_mechanism": "Authors cite Friston (2010) FEP..."
}
```

**Fix Required**: Enhance rule synthesis to extract mechanism from Panel 6.

---

### Requirement 3: Meta-Review Logic (Option B)

**What You Need**:

```
AGGREGATE across studies:

Study A: plants → cortisol↓ (p<.05, d=0.42, N=32)
Study B: plants → HR↓ (p<.01, d=0.56, N=50)
Study C: plants → BP↓ (p<.03, d=0.38, N=120)
Study D: plants → HRV↑ (p<.02, d=0.51, N=85)

META-RULE: "Plants → stress reduction"
├─ Evidence count: 4 studies
├─ Operational measures: cortisol, HR, BP, HRV
├─ Total N: 287 participants
├─ Effect size range: 0.38-0.56 (medium)
├─ Confidence: 0.89 (high triangulation)
└─ Sub-findings: [Study A micro-rule, Study B micro-rule, ...]
```

**Current v15.8.1 Capability**: ❌ **NONE**

Current synthesis creates **one rule per paper**:
- Paper A → Rule: "plants reduce stress" (confidence 0.7)
- Paper B → Rule: "plants reduce stress" (confidence 0.8)  
- Paper C → Rule: "plants reduce stress" (confidence 0.6)

**Result**: 3 duplicate rules instead of 1 meta-rule with 3 sub-findings.

**Revitalized Capability**: ⚠️ **PARTIAL**

The `interaction_analysis.py` detects rules sharing consequents:
```python
def detect_potential_interactions():
    # Groups rules by consequent
    consequent_map = {}
    for rule in rules:
        if rule.consequent not in consequent_map:
            consequent_map[rule.consequent] = []
        consequent_map[rule.consequent].append(rule)
```

**Problem**: Designed for **interaction detection** (synergy/destructive), not **meta-aggregation**.

**Solution Needed**: New `meta_review.py` module that:
1. Groups micro-rules by consequent
2. Identifies operational measure diversity
3. Aggregates confidence scores
4. Creates meso-rule with child references

---

### Requirement 4: Hierarchical Display (Toggle-Capable)

**What You Need**:

```
USER TOGGLES BETWEEN 3 VIEWS:

VIEW 1: FLAT LIST (current)
├─ Rule 1: Plants reduce stress (0.89)
├─ Rule 2: Natural light improves focus (0.82)
├─ Rule 3: Curved walls reduce anxiety (0.76)
└─ ... (simple, scannable)

VIEW 2: TREE STRUCTURE (hierarchical)
├─ MACRO: Biophilic design → improved affective state
│   ├─ MESO: Plants → stress reduction (0.89)
│   │   ├─ MICRO: Plants → cortisol↓ [Study A]
│   │   ├─ MICRO: Plants → HR↓ [Study B]
│   │   └─ MICRO: Plants → BP↓ [Study C]
│   └─ MESO: Natural views → attention restoration (0.84)
└─ MACRO: Curved architecture → positive affect
    └─ MESO: Curved walls → anxiety reduction (0.76)
        ├─ MICRO: Curved → cortisol↓ [Study D]
        └─ MICRO: Curved → subjective anxiety↓ [Study E]

VIEW 3: NETWORK GRAPH (explanatory)
[Curved walls] ───via───> [Predictive Processing] ───explains───> [Anxiety Reduction]
       │                           │
       └───via───> [Motor Simulation] ──explains──> [Safety Perception]
```

**Current v15.8.1 Capability**: ❌ **FLAT LIST ONLY**

`templates/rules_view.html` shows:
```html
<ol>
  {% for r in data.rules %}
  <li>{{ r.rule }}</li>
  {% endfor %}
</ol>
```

**Revitalized Capability**: ❌ **NONE** (no visualization beyond table)

**What's Needed**:

1. **Backend**: Compute hierarchy from database relationships
2. **Frontend**: JavaScript tree component (collapsible nodes)
3. **Network View**: D3.js or Cytoscape.js graph (defer to v2.0)

---

## PART 2: ARCHITECTURAL RECOMMENDATIONS

### Option A: Enhance v15.8.1 JSON (Lightweight)

**Approach**: Add hierarchy fields to JSON without database

Enhanced rule schema:
```json
{
  "rule_id": "rule_001",
  "rule": "Indoor plants reduce stress",
  "rule_level": "meso",
  "parent_rule_id": "rule_macro_001",
  "child_rule_ids": ["rule_micro_001", "rule_micro_002", "rule_micro_003"],
  "operational_measures": ["cortisol", "heart_rate", "blood_pressure"],
  "mechanism": "biophilia_hypothesis",
  "mechanism_description": "Innate affinity to natural elements...",
  "theoretical_framework": "Evolutionary Psychology",
  "confidence": 0.89,
  "confidence_sources": {
    "triangulation": 0.4,
    "effect_size": 0.3,
    "sample_size": 0.19
  },
  "provenance": [...],
  "sub_findings": [
    {
      "study": "Study A",
      "measure": "cortisol",
      "effect": "decrease",
      "p_value": 0.05,
      "effect_size": 0.42,
      "n": 32
    },
    ...
  ]
}
```

**Pros**:
- No database required
- Lightweight for simple jobs
- Backward compatible with v15.8.1

**Cons**:
- Manual hierarchy management (no foreign keys)
- Hard to query across jobs
- No validation of parent-child consistency

---

### Option B: Integrate Revitalized Database (Full-Featured)

**Approach**: Use `BUILD_COMPLETE/revitalized/models.py` with enhancements

**Step 1**: Enhance Rule model
```python
class Rule(Base):
    __tablename__ = 'rules'
    
    id = Column(Integer, primary_key=True)
    consequent = Column(String, nullable=False)
    antecedents = Column(Text)  # JSON array
    weight = Column(Float, default=0.5)
    
    # NEW: Hierarchy fields
    rule_level = Column(String)  # 'micro', 'meso', 'macro'
    parent_rule_id = Column(Integer, ForeignKey('rules.id'))
    
    # NEW: Mechanism fields  
    mechanism = Column(String)  # 'predictive_processing_fluency'
    mechanism_description = Column(Text)
    theoretical_framework = Column(String)  # 'Predictive Processing'
    
    # NEW: Operational measure (for micro-rules)
    operational_measure = Column(String)  # 'cortisol', 'heart_rate', etc.
    measure_direction = Column(String)  # 'increase', 'decrease'
    
    # Statistical details (for micro-rules)
    p_value = Column(Float)
    effect_size = Column(Float)
    sample_size = Column(Integer)
    
    # Relationships
    parent_rule = relationship('Rule', remote_side=[id], backref='child_rules')
    evidence = relationship('Evidence', back_populates='rule')
```

**Step 2**: Meta-Review Synthesis
```python
# New module: meta_review.py

def aggregate_micro_rules_to_meso(micro_rules: List[Rule]) -> Rule:
    """
    Aggregate multiple micro-rules into one meso-rule.
    
    Example:
    Input: [plants→cortisol↓, plants→HR↓, plants→BP↓]
    Output: plants→stress_reduction (meso-rule)
    """
    # Group by consequent construct
    consequent = infer_construct_from_measures(micro_rules)
    
    # Calculate meta-confidence
    confidence = calculate_triangulation_score(micro_rules)
    
    # Create meso-rule
    meso_rule = Rule(
        consequent=consequent,
        antecedents=micro_rules[0].antecedents,
        weight=confidence,
        rule_level='meso'
    )
    
    # Link children
    for micro in micro_rules:
        micro.parent_rule_id = meso_rule.id
    
    return meso_rule


def infer_construct_from_measures(micro_rules: List[Rule]) -> str:
    """
    Map operational measures to theoretical constructs.
    
    cortisol, HR, BP, HRV → "stress_reduction"
    RT, accuracy, omissions → "attention_performance"  
    mood ratings, affect grid → "affective_state"
    """
    measures = {r.operational_measure for r in micro_rules}
    
    stress_indicators = {'cortisol', 'heart_rate', 'blood_pressure', 'hrv'}
    attention_indicators = {'reaction_time', 'accuracy', 'omission_errors'}
    affect_indicators = {'mood_rating', 'valence', 'arousal', 'panas'}
    
    if measures & stress_indicators:
        return "stress_reduction"
    elif measures & attention_indicators:
        return "attention_performance"
    elif measures & affect_indicators:
        return "affective_state"
    else:
        return "unknown_construct"


def calculate_triangulation_score(micro_rules: List[Rule]) -> float:
    """
    Confidence increases with:
    - Number of operational measures (more triangulation)
    - Consistency of effect direction (all decrease or all increase)
    - Statistical strength (p-values, effect sizes)
    - Total sample size
    """
    num_measures = len(set(r.operational_measure for r in micro_rules))
    avg_effect_size = sum(r.effect_size for r in micro_rules) / len(micro_rules)
    total_n = sum(r.sample_size for r in micro_rules)
    
    triangulation = min(num_measures / 4.0, 1.0) * 0.4  # Up to 0.4
    effect_strength = min(avg_effect_size / 0.8, 1.0) * 0.3  # Up to 0.3
    sample_strength = min(total_n / 200.0, 1.0) * 0.3  # Up to 0.3
    
    return triangulation + effect_strength + sample_strength
```

**Pros**:
- Proper relational structure
- Query capabilities (find all micro-rules for meso-rule)
- Validation via foreign keys
- Supports interaction analysis (already implemented)

**Cons**:
- Database setup complexity
- Migration from JSON files
- May be overkill for simple 5-rule jobs

---

### Option C: Hybrid Approach (RECOMMENDED)

**Approach**: Start JSON, migrate to database when needed

**Workflow**:
```
SIMPLE JOBS (1-20 rules):
├─ Use JSON artifacts (current v15.8.1)
├─ Flat list display
└─ Export to database if user wants hierarchy

COMPLEX JOBS (20+ rules, hierarchical needs):
├─ Use database from start
├─ Enable meta-review synthesis
├─ Tree/network visualization
└─ Cross-job meta-analysis
```

**Implementation**:

1. **Add "Enable Advanced Mode" toggle** in `/rag/settings`:
   - OFF: JSON artifacts (default, current behavior)
   - ON: Database + hierarchical rules

2. **Migration path**:
   ```python
   @bp.route("/job/<job_id>/migrate_to_database", methods=["POST"])
   def migrate_job_to_database(job_id):
       """Convert JSON artifacts to database records."""
       # Load JSON rules
       rules_json = read_json(job_id, "rules")
       
       # Create database records
       with session_scope() as session:
           for r in rules_json['rules']:
               rule = Rule(
                   consequent=extract_consequent(r['rule']),
                   antecedents=extract_antecedents(r['rule']),
                   weight=r.get('confidence', 0.5),
                   rule_level='meso'  # Default assumption
               )
               session.add(rule)
       
       return jsonify({"ok": True, "migrated": len(rules_json['rules'])})
   ```

3. **Template adaptation**:
   ```html
   <!-- templates/rules_view.html -->
   {% if job.uses_database %}
     {% include '_partials/rules_hierarchical.html' %}
   {% else %}
     {% include '_partials/rules_flat.html' %}
   {% endif %}
   ```

---

## PART 3: IMMEDIATE ACTION ITEMS (Priority Order)

### P0: Critical Schema Enhancements (4 hours)

**File**: `BUILD_COMPLETE/revitalized/models.py`

Add to Rule model:
```python
# Hierarchy
rule_level = Column(String)  # 'micro', 'meso', 'macro'
parent_rule_id = Column(Integer, ForeignKey('rules.id'))
parent_rule = relationship('Rule', remote_side=[id], backref='child_rules')

# Mechanism
mechanism = Column(String)
mechanism_description = Column(Text)
theoretical_framework = Column(String)

# Operational measures (micro-rules)
operational_measure = Column(String)
measure_direction = Column(String)  # 'increase', 'decrease', 'stable'
p_value = Column(Float)
effect_size = Column(Float)
effect_size_type = Column(String)  # 'cohen_d', 'eta_squared', 'r'
sample_size = Column(Integer)

# Confidence decomposition
confidence_triangulation = Column(Float)
confidence_effect_strength = Column(Float)
confidence_sample_size = Column(Float)
```

**SQL Migration**:
```sql
ALTER TABLE rules ADD COLUMN rule_level VARCHAR(10);
ALTER TABLE rules ADD COLUMN parent_rule_id INTEGER REFERENCES rules(id);
ALTER TABLE rules ADD COLUMN mechanism VARCHAR(255);
ALTER TABLE rules ADD COLUMN mechanism_description TEXT;
ALTER TABLE rules ADD COLUMN theoretical_framework VARCHAR(255);
ALTER TABLE rules ADD COLUMN operational_measure VARCHAR(100);
ALTER TABLE rules ADD COLUMN measure_direction VARCHAR(20);
ALTER TABLE rules ADD COLUMN p_value REAL;
ALTER TABLE rules ADD COLUMN effect_size REAL;
ALTER TABLE rules ADD COLUMN sample_size INTEGER;

CREATE INDEX idx_rules_level ON rules(rule_level);
CREATE INDEX idx_rules_parent ON rules(parent_rule_id);
CREATE INDEX idx_rules_measure ON rules(operational_measure);
```

---

### P1: Enhance 7-Panel Extraction (6 hours)

**File**: `BUILD_COMPLETE/tasks.py` (or equivalent rule synthesis)

Current Panel 6 extraction:
```python
"Panel 6: Discussion & Theoretical Insights"
{
  "theoretical_frameworks": ["Predictive Processing", "Embodied Cognition"]
}
```

**Enhanced extraction**:
```python
"Panel 6: Mechanism Extraction"
{
  "rule": "Curved walls reduce anxiety",
  "mechanisms": [
    {
      "mechanism_type": "predictive_processing_fluency",
      "description": "Curved forms reduce prediction error in visual cortex",
      "theoretical_framework": "Predictive Processing (Friston, 2010)",
      "evidence_in_article": "Authors cite reduced BOLD signal in FFA..."
    },
    {
      "mechanism_type": "motor_simulation_safety",
      "description": "Curved enclosures simulate protective embrace gestures",
      "theoretical_framework": "Embodied Cognition (Barsalou, 2008)",
      "evidence_in_article": "Discussion mentions affordance theory..."
    }
  ],
  "operational_measures": [
    {
      "construct": "anxiety",
      "measure": "salivary_cortisol",
      "direction": "decrease",
      "stats": {"p": 0.03, "d": 0.52, "n": 68}
    },
    {
      "construct": "anxiety",
      "measure": "state_anxiety_inventory",
      "direction": "decrease", 
      "stats": {"p": 0.01, "d": 0.64, "n": 68}
    }
  ]
}
```

**Prompt Enhancement**:
```
Panel 6 (Enhanced): Mechanisms & Operational Measures

CRITICAL INSTRUCTIONS:
1. IDENTIFY ALL OPERATIONAL MEASURES used to assess outcomes
   - Physiological: cortisol, HR, BP, HRV, EEG, fMRI BOLD, skin conductance
   - Behavioral: reaction time, accuracy, task performance, error rates
   - Self-report: anxiety scales, mood ratings, affect grids, satisfaction

2. EXTRACT PROPOSED MECHANISMS from Discussion section
   - Look for: "This effect may be explained by...", "We propose that...", "Consistent with X theory..."
   - Identify: Specific cognitive/neural processes cited
   - Link: Mechanism to theoretical framework (Predictive Processing, Embodied Cognition, etc.)

3. MAP: Stimulus → Mechanism → Operational Measure → Construct
   Example: Curved walls → predictive fluency → cortisol decrease → anxiety reduction

FORMAT:
{
  "operational_measures": [
    {
      "construct": "anxiety" | "stress" | "attention" | "mood",
      "measure_type": "physiological" | "behavioral" | "self_report",
      "measure_name": "salivary_cortisol",
      "direction": "increase" | "decrease" | "stable",
      "statistical_support": {
        "p_value": 0.03,
        "effect_size": 0.52,
        "effect_type": "cohen_d",
        "sample_size": 68,
        "test": "paired_t_test"
      }
    }
  ],
  "mechanisms": [
    {
      "mechanism_name": "predictive_processing_fluency",
      "description": "Curved forms reduce prediction error...",
      "framework": "Predictive Processing",
      "evidence_strength": "strong" | "moderate" | "speculative",
      "citations": ["Friston (2010)", "Bar (2004)"]
    }
  ]
}
```

---

### P2: Meta-Review Synthesis Module (8 hours)

**New File**: `meta_review.py`

```python
"""
Meta-Review Synthesis
=====================
Aggregates micro-rules into meso-rules based on operational measure diversity.

Example:
    Study A: plants → cortisol↓ (p<.05, d=0.42)
    Study B: plants → HR↓ (p<.01, d=0.56)
    Study C: plants → BP↓ (p<.03, d=0.38)
    
    → META: plants → stress_reduction (confidence=0.89, n_measures=3)
"""

from typing import List, Dict, Set
from models import Rule
from database import session_scope

# Construct mapping
STRESS_MEASURES = {'cortisol', 'heart_rate', 'blood_pressure', 'hrv', 
                   'skin_conductance', 'state_anxiety'}
ATTENTION_MEASURES = {'reaction_time', 'accuracy', 'omission_errors', 
                      'commission_errors', 'digit_span'}
MOOD_MEASURES = {'panas_positive', 'panas_negative', 'valence', 
                 'arousal', 'mood_rating'}

CONSTRUCT_MAP = {
    'stress_reduction': STRESS_MEASURES,
    'attention_performance': ATTENTION_MEASURES,
    'affective_state': MOOD_MEASURES
}


def aggregate_to_meta_rule(micro_rules: List[Rule]) -> Rule:
    """Create meso-rule from micro-rules sharing antecedents."""
    
    # Infer construct from operational measures
    construct = infer_construct(micro_rules)
    
    # Calculate aggregated confidence
    confidence = calculate_meta_confidence(micro_rules)
    
    # Create meso-rule
    meso_rule = Rule(
        consequent=construct,
        antecedents=micro_rules[0].antecedents,
        weight=confidence,
        rule_level='meso',
        rule_type='meta_aggregated'
    )
    
    # Link children
    for micro in micro_rules:
        micro.parent_rule_id = meso_rule.id
        micro.rule_level = 'micro'
    
    return meso_rule


def infer_construct(rules: List[Rule]) -> str:
    """Map operational measures to theoretical construct."""
    measures = {r.operational_measure for r in rules if r.operational_measure}
    
    for construct, measure_set in CONSTRUCT_MAP.items():
        overlap = measures & measure_set
        if len(overlap) >= 2:  # At least 2 measures match
            return construct
    
    # Fallback: use most common consequent
    consequents = [r.consequent for r in rules]
    return max(set(consequents), key=consequents.count)


def calculate_meta_confidence(rules: List[Rule]) -> float:
    """
    Confidence based on triangulation across operational measures.
    
    Factors:
    1. Number of unique measures (more = better)
    2. Consistency of direction (all decrease or all increase)
    3. Average effect size
    4. Total sample size
    """
    unique_measures = len(set(r.operational_measure for r in rules if r.operational_measure))
    avg_effect_size = sum(r.effect_size or 0.5 for r in rules) / len(rules)
    total_n = sum(r.sample_size or 0 for r in rules)
    
    # Check direction consistency
    directions = [r.measure_direction for r in rules if r.measure_direction]
    direction_consistent = len(set(directions)) == 1
    
    # Scoring
    triangulation_score = min(unique_measures / 4.0, 1.0) * 0.35
    effect_score = min(avg_effect_size / 0.8, 1.0) * 0.25
    sample_score = min(total_n / 200.0, 1.0) * 0.25
    consistency_score = 0.15 if direction_consistent else 0.0
    
    return triangulation_score + effect_score + sample_score + consistency_score


def find_meta_aggregation_opportunities() -> List[List[Rule]]:
    """
    Find groups of micro-rules that should be aggregated.
    
    Returns:
        List of rule groups, each group shares antecedents and targets same construct
    """
    with session_scope() as session:
        # Get all micro-level rules
        micro_rules = session.query(Rule).filter_by(rule_level='micro').all()
        
        # Group by antecedents
        grouped = {}
        for rule in micro_rules:
            key = rule.antecedents  # JSON string
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(rule)
        
        # Filter groups with 2+ rules measuring similar constructs
        opportunities = []
        for rules in grouped.values():
            if len(rules) >= 2:
                # Check if measures map to same construct
                construct = infer_construct(rules)
                if construct != "unknown_construct":
                    opportunities.append(rules)
        
        return opportunities
```

**Usage**:
```python
# After extracting all rules from a job
opportunities = find_meta_aggregation_opportunities()

for micro_group in opportunities:
    meso_rule = aggregate_to_meta_rule(micro_group)
    session.add(meso_rule)
    
session.commit()
```

---

### P3: Hierarchical Tree View (12 hours)

**New Template**: `templates/_partials/rules_hierarchical.html`

```html
<!-- Hierarchical tree view for rules -->
<div class="rules-hierarchy">
  <div class="view-toggle">
    <button class="toggle-btn active" data-view="tree">🌳 Tree View</button>
    <button class="toggle-btn" data-view="flat">📋 Flat List</button>
    <button class="toggle-btn" data-view="network">🕸️ Network (Coming Soon)</button>
  </div>
  
  <div id="tree-view" class="hierarchy-container">
    {% for macro_rule in macro_rules %}
    <div class="rule-node macro">
      <div class="rule-header" onclick="toggleChildren(this)">
        <span class="expand-icon">▼</span>
        <span class="rule-level-badge macro">MACRO</span>
        <span class="rule-text">{{ macro_rule.rule }}</span>
        <span class="rule-confidence">{{ (macro_rule.weight * 100)|round }}%</span>
      </div>
      
      <div class="rule-children">
        {% for meso_rule in macro_rule.child_rules %}
        <div class="rule-node meso">
          <div class="rule-header" onclick="toggleChildren(this)">
            <span class="expand-icon">▼</span>
            <span class="rule-level-badge meso">MESO</span>
            <span class="rule-text">{{ meso_rule.rule }}</span>
            <span class="rule-confidence">{{ (meso_rule.weight * 100)|round }}%</span>
            
            {% if meso_rule.mechanism %}
            <span class="mechanism-tag" title="{{ meso_rule.mechanism_description }}">
              ⚙️ {{ meso_rule.mechanism }}
            </span>
            {% endif %}
          </div>
          
          <div class="rule-children">
            {% for micro_rule in meso_rule.child_rules %}
            <div class="rule-node micro">
              <div class="rule-header">
                <span class="rule-level-badge micro">MICRO</span>
                <span class="rule-text">{{ micro_rule.rule }}</span>
                
                <div class="micro-details">
                  <span class="measure-badge">{{ micro_rule.operational_measure }}</span>
                  <span class="direction-badge {{ micro_rule.measure_direction }}">
                    {% if micro_rule.measure_direction == 'decrease' %}↓{% else %}↑{% endif %}
                  </span>
                  <span class="stats">
                    p={{ micro_rule.p_value }}, d={{ micro_rule.effect_size }}, N={{ micro_rule.sample_size }}
                  </span>
                </div>
                
                <div class="micro-source">
                  {% for prov in micro_rule.provenance %}
                    <a href="/paper/{{ prov.doi|urlencode }}/analysis" class="source-link">
                      {{ prov.title[:50] }}... ({{ prov.year }})
                    </a>
                  {% endfor %}
                </div>
              </div>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
  
  <div id="flat-view" class="hierarchy-container" style="display: none;">
    <!-- Standard flat list (current view) -->
    {% include '_partials/rules_flat.html' %}
  </div>
</div>

<script>
function toggleChildren(header) {
  const parent = header.parentElement;
  const children = parent.querySelector('.rule-children');
  const icon = header.querySelector('.expand-icon');
  
  if (children.style.display === 'none') {
    children.style.display = 'block';
    icon.textContent = '▼';
  } else {
    children.style.display = 'none';
    icon.textContent = '▶';
  }
}

document.querySelectorAll('.toggle-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const view = this.dataset.view;
    
    // Update active button
    document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    
    // Show selected view
    document.querySelectorAll('.hierarchy-container').forEach(c => c.style.display = 'none');
    document.getElementById(`${view}-view`).style.display = 'block';
  });
});
</script>

<style>
.rules-hierarchy {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  border-bottom-color: white;
  font-weight: 600;
}

.rule-node {
  margin-left: 1.5rem;
  margin-bottom: 0.5rem;
  border-left: 2px solid #e2e8f0;
  padding-left: 1rem;
}

.rule-node.macro {
  margin-left: 0;
  border-left: 3px solid #3182ce;
}

.rule-node.meso {
  border-left-color: #48bb78;
}

.rule-node.micro {
  border-left-color: #ed8936;
}

.rule-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.rule-header:hover {
  background: #edf2f7;
}

.expand-icon {
  font-size: 0.75rem;
  color: #718096;
  width: 1rem;
}

.rule-level-badge {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  letter-spacing: 0.05em;
}

.rule-level-badge.macro {
  background: #bee3f8;
  color: #2c5282;
}

.rule-level-badge.meso {
  background: #c6f6d5;
  color: #22543d;
}

.rule-level-badge.micro {
  background: #fed7d7;
  color: #742a2a;
}

.rule-text {
  flex: 1;
  font-weight: 500;
  color: #2d3748;
}

.rule-confidence {
  font-weight: 600;
  color: #3182ce;
}

.mechanism-tag {
  font-size: 0.75rem;
  background: #fefcbf;
  color: #744210;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  cursor: help;
}

.micro-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.measure-badge {
  background: #edf2f7;
  padding: 0.125rem 0.5rem;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.75rem;
}

.direction-badge {
  font-weight: 700;
  font-size: 1.25rem;
}

.direction-badge.decrease {
  color: #48bb78;
}

.direction-badge.increase {
  color: #e53e3e;
}

.stats {
  color: #718096;
  font-size: 0.75rem;
  font-family: monospace;
}

.micro-source {
  margin-top: 0.25rem;
  font-size: 0.75rem;
}

.source-link {
  color: #3182ce;
  text-decoration: none;
}

.source-link:hover {
  text-decoration: underline;
}

.rule-children {
  margin-top: 0.5rem;
}
</style>
```

---

## PART 4: IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2)

**Priority 0: Schema Enhancement** [4 hours]
- Add hierarchy fields to Rule model
- Add mechanism fields
- Add operational measure fields
- Run database migrations

**Priority 1: Enhanced 7-Panel Extraction** [6 hours]
- Update Panel 6 prompt for mechanism extraction
- Add operational measures extraction
- Update rule synthesis to populate new fields

**Priority 2: Paper-to-Rules View** [6 hours]
- Implement reverse lookup (your original request)
- Add clickable links from existing views

**Total Phase 1**: 16 hours

### Phase 2: Meta-Review Logic (Week 3)

**Priority 3: Meta-Review Module** [8 hours]
- Implement `meta_review.py`
- Create micro-to-meso aggregation
- Add construct inference logic
- Add triangulation scoring

**Priority 4: Batch Processing** [4 hours]
- Add "Aggregate Rules" button to jobs view
- Run meta-review after all papers processed
- Display aggregation results

**Total Phase 2**: 12 hours

### Phase 3: Hierarchical Display (Week 4)

**Priority 5: Tree View UI** [12 hours]
- Create hierarchical template
- Add toggle between flat/tree views
- Implement collapse/expand JavaScript
- Style micro/meso/macro levels distinctly

**Priority 6: Backend Hierarchy Query** [4 hours]
- Add route to fetch hierarchical rules
- Recursive query for parent-child relationships
- JSON serialization of tree structure

**Total Phase 3**: 16 hours

### Phase 4: Integration & Polish (Week 5)

**Priority 7: Hybrid Mode Toggle** [4 hours]
- Add "Advanced Mode" setting in RAG settings
- JSON vs Database backend selection
- Migration path from JSON to database

**Priority 8: Testing & Documentation** [8 hours]
- Test hierarchical rule creation
- Test meta-aggregation
- Update docs with new workflow
- Create example jobs

**Total Phase 4**: 12 hours

---

**GRAND TOTAL: 56 hours** (7 days of development)

---

## PART 5: YOUR IDEAS vs MY IDEAS - INTEGRATION

### Where We Align ✅

1. **Paper-to-Rules Reverse Lookup**: You didn't explicitly mention this, but when I proposed it, you said "I like your ideas" - this addresses validation needs

2. **Hierarchical Display**: Your toggle requirement (flat/tree/network) matches my recommendation for different view modes

3. **Categorization**: Your architecture diagram shows categories (lighting, acoustics, spatial) - this aligns with integrating the Prima Facie Categorization module

### Where You Add Critical Depth 🎯

1. **Rule Granularity (Micro/Meso/Macro)**: I didn't understand this hierarchy until you explained it. My original audit assumed flat rules.

2. **Operational Measures**: I completely missed that stress = {cortisol, HR, BP, HRV}. Your meta-review logic is essential.

3. **Mechanism Extraction**: I saw Panel 6 had "theoretical frameworks" but didn't realize rules need mechanism attribution at rule-level, not article-level.

4. **Meta-Aggregation**: My enrichment suggestion was about "find more papers," but you need "aggregate existing micro-findings into meso-rules."

### Where I Add Practical Implementation 🛠️

1. **Hybrid Approach**: You need hierarchy, but not every job needs it. My recommendation for JSON (simple) vs Database (complex) provides flexibility.

2. **Migration Path**: Your requirements need database, but v15.8.1 uses JSON. My staged migration preserves existing work.

3. **UI Components**: Your toggle concept needs actual HTML/CSS/JS. My templates provide the interface.

4. **Integration with Existing**: Your needs work with revitalized components I found in BUILD_COMPLETE, but they weren't wired up. I'm showing how to integrate.

---

## CONCLUSION

**Version Analyzed**: Article Eater v15.8.1

**Gap**: Current system is architecturally incomplete for CNfA's hierarchical, meta-review requirements.

**Solution**: 
1. **Immediate** (Week 1-2): Schema enhancement + Paper-to-Rules view
2. **Near-term** (Week 3): Meta-review aggregation logic  
3. **Mid-term** (Week 4): Hierarchical tree display
4. **Long-term**: Network graph visualization (defer to v2.0)

**Your Requirements Are Better**: They reveal the true depth of CNfA evidence synthesis. My GUI audit was surface-level until you explained the theoretical foundation.

**My Implementation Is Practical**: I'm showing how to build what you need using existing components (revitalized models) + strategic enhancements.

**Next Step**: Confirm this roadmap aligns with your vision, then I'll generate production-ready code for Phase 1.