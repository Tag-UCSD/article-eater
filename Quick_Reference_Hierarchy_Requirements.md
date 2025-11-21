# Quick Reference: CNfA Hierarchical Rules
## Article Eater v15.8.1 → v16.0 Upgrade Requirements

**Date**: November 8, 2025

---

## THE CORE PROBLEM

**Current v15.8.1**:
```
Paper A → "Plants reduce stress" (confidence: 0.7)
Paper B → "Plants reduce stress" (confidence: 0.8)
Paper C → "Plants reduce stress" (confidence: 0.6)

Result: 3 duplicate rules ❌
```

**What CNfA Needs**:
```
META-RULE: "Plants → stress reduction" (confidence: 0.89)
├─ MICRO: Plants → cortisol↓ (p<.05, d=0.42, N=32) [Paper A]
├─ MICRO: Plants → HR↓ (p<.01, d=0.56, N=50) [Paper B]
├─ MICRO: Plants → BP↓ (p<.03, d=0.38, N=120) [Paper C]
└─ MICRO: Plants → HRV↑ (p<.02, d=0.51, N=85) [Paper D]

Mechanism: Biophilia Hypothesis
Framework: Evolutionary Psychology
Triangulation: 4 operational measures ✅
```

---

## THREE-LEVEL HIERARCHY

### MICRO-RULES (Operational/Sensor Level)
**Definition**: Single study, single operational measure  
**Example**: "Indoor plants → ↓ salivary cortisol (p<.05, d=0.42, N=32)"

**Required Fields**:
- `operational_measure`: "cortisol" | "heart_rate" | "blood_pressure" | "hrv" | "reaction_time" | etc.
- `measure_direction`: "increase" | "decrease" | "stable"
- `p_value`: 0.05
- `effect_size`: 0.42
- `effect_size_type`: "cohen_d" | "eta_squared" | "r"
- `sample_size`: 32
- `provenance`: [Single paper]

### MESO-RULES (Construct Level)
**Definition**: Aggregated from multiple micro-rules measuring same construct  
**Example**: "Indoor plants → stress reduction (confidence: 0.89)"

**Required Fields**:
- `consequent`: Theoretical construct ("stress_reduction", not "cortisol_decrease")
- `child_rules`: List of micro-rule IDs
- `operational_measures_used`: ["cortisol", "heart_rate", "blood_pressure", "hrv"]
- `triangulation_score`: 0.89 (based on measure diversity)
- `mechanism`: "biophilia_hypothesis"
- `theoretical_framework`: "Evolutionary Psychology"

**Confidence Calculation**:
```python
triangulation = min(num_unique_measures / 4.0, 1.0) * 0.4  # 4 measures → 0.4
effect_strength = min(avg_effect_size / 0.8, 1.0) * 0.3    # d=0.47 → 0.18
sample_strength = min(total_n / 200.0, 1.0) * 0.3          # N=287 → 0.3
consistency = 0.15 if all_same_direction else 0.0          # All ↓ → 0.15

Total: 0.4 + 0.18 + 0.3 + 0.15 = 0.89 ✅
```

### MACRO-RULES (Theoretical/Framework Level)
**Definition**: High-level principles explained by unifying theories  
**Example**: "Biophilic design → improved affective state"

**Required Fields**:
- `consequent`: Broad outcome ("affective_state", "cognitive_performance")
- `child_rules`: List of meso-rule IDs
- `pathways`: ["stress_reduction", "attention_restoration", "mood_regulation"]
- `theoretical_framework`: "Predictive Processing" | "Embodied Cognition" | "Allostasis"
- `explanatory_power`: How well framework explains subordinate rules

---

## OPERATIONAL MEASURES → CONSTRUCT MAPPING

### Stress / Anxiety
```python
STRESS_MEASURES = {
    'cortisol',           # Physiological
    'heart_rate',         # Physiological
    'blood_pressure',     # Physiological
    'hrv',                # Physiological (inverse)
    'skin_conductance',   # Physiological
    'state_anxiety',      # Self-report (STAI)
    'perceived_stress'    # Self-report (PSS)
}
→ Construct: "stress_reduction" | "anxiety_reduction"
```

### Attention / Focus
```python
ATTENTION_MEASURES = {
    'reaction_time',      # Behavioral (inverse)
    'accuracy',           # Behavioral
    'omission_errors',    # Behavioral (inverse)
    'commission_errors',  # Behavioral (inverse)
    'digit_span',         # Behavioral
    'sustained_attention' # Self-report
}
→ Construct: "attention_performance" | "focus_capacity"
```

### Mood / Affect
```python
MOOD_MEASURES = {
    'panas_positive',     # Self-report
    'panas_negative',     # Self-report (inverse)
    'valence',            # Self-report (circumplex)
    'arousal',            # Self-report (circumplex)
    'mood_rating',        # Self-report
    'life_satisfaction'   # Self-report
}
→ Construct: "affective_state" | "mood_regulation"
```

### Memory / Cognition
```python
MEMORY_MEASURES = {
    'recall_accuracy',    # Behavioral
    'recognition_accuracy', # Behavioral
    'working_memory_span',  # Behavioral
    'spatial_memory',      # Behavioral
    'verbal_memory'        # Behavioral
}
→ Construct: "memory_performance" | "cognitive_capacity"
```

---

## MECHANISM EXTRACTION

### From Panel 6: Discussion & Theoretical Insights

**Look For**:
1. "This effect may be explained by..."
2. "We propose that..."
3. "Consistent with [Theory Name]..."
4. "These results support the idea that..."
5. Citations to theoretical papers (Friston, Barsalou, Barrett, etc.)

**Extract**:
```json
{
  "mechanism_name": "predictive_processing_fluency",
  "mechanism_description": "Curved forms reduce prediction error in visual cortex, lowering cognitive load",
  "theoretical_framework": "Predictive Processing (Friston, 2010)",
  "evidence_strength": "strong" | "moderate" | "speculative",
  "supporting_citations": [
    "Friston, K. (2010). The free-energy principle...",
    "Bar, M. (2004). Visual objects in context..."
  ],
  "neural_basis": "Reduced BOLD signal in FFA during curved vs angular exposure"
}
```

**Common Mechanisms in Architecture**:
- `predictive_processing_fluency`: Reduced prediction error → reduced anxiety
- `motor_simulation_affordances`: Embodied cognition → safety perception
- `attention_restoration_theory`: Nature exposure → directed attention recovery
- `biophilia_hypothesis`: Evolutionary affinity → stress reduction
- `allostatic_load_reduction`: Reduced physiological demands → health
- `perceptual_fluency`: Easy processing → positive affect

---

## UI TOGGLE VIEWS

### View 1: FLAT LIST (Default, Current)
```
Simple, scannable list of all rules regardless of level

✓ Rule 1: Plants reduce stress (0.89) [MESO]
✓ Rule 2: Curved walls reduce anxiety (0.76) [MESO]
✓ Rule 3: Natural light improves focus (0.82) [MESO]
✓ Rule 4: Plants → cortisol↓ (0.7) [MICRO]
  ... (shows all micro-rules too, can be overwhelming)

Use case: Quick scan, export, initial review
```

### View 2: TREE STRUCTURE (Hierarchical)
```
Collapsible hierarchy showing rule relationships

▼ MACRO: Biophilic design → improved affective state [0.91]
  │
  ├─▼ MESO: Plants → stress reduction [0.89]
  │  ├─ MICRO: Plants → cortisol↓ (p<.05, d=0.42, N=32) [Study A]
  │  ├─ MICRO: Plants → HR↓ (p<.01, d=0.56, N=50) [Study B]
  │  ├─ MICRO: Plants → BP↓ (p<.03, d=0.38, N=120) [Study C]
  │  └─ MICRO: Plants → HRV↑ (p<.02, d=0.51, N=85) [Study D]
  │
  └─▼ MESO: Natural views → attention restoration [0.84]
     ├─ MICRO: Nature views → RT↓ (p<.01, d=0.61, N=45) [Study E]
     └─ MICRO: Nature views → accuracy↑ (p<.02, d=0.49, N=45) [Study E]

Use case: Understanding evidence structure, validation, theoretical mapping
```

### View 3: NETWORK GRAPH (Future/v2.0)
```
Interactive graph showing explanatory relationships

[Curved Walls] ──via──> [Predictive Processing] ──explains──> [Anxiety ↓]
      │                        │
      └──via──> [Motor Simulation] ──explains──> [Safety Perception]
                                                        │
                                                        └──> [Affective +]

Use case: Theory building, mechanism discovery, publication figures
```

---

## DATABASE SCHEMA ADDITIONS

### Rule Table Enhancements

```sql
ALTER TABLE rules ADD COLUMN rule_level VARCHAR(10); 
  -- 'micro' | 'meso' | 'macro'

ALTER TABLE rules ADD COLUMN parent_rule_id INTEGER REFERENCES rules(id);
  -- Creates hierarchy: micro → meso → macro

-- Mechanism fields
ALTER TABLE rules ADD COLUMN mechanism VARCHAR(255);
ALTER TABLE rules ADD COLUMN mechanism_description TEXT;
ALTER TABLE rules ADD COLUMN theoretical_framework VARCHAR(255);

-- Operational measure fields (for MICRO rules)
ALTER TABLE rules ADD COLUMN operational_measure VARCHAR(100);
  -- 'cortisol' | 'heart_rate' | 'reaction_time' | etc.

ALTER TABLE rules ADD COLUMN measure_direction VARCHAR(20);
  -- 'increase' | 'decrease' | 'stable'

ALTER TABLE rules ADD COLUMN p_value REAL;
ALTER TABLE rules ADD COLUMN effect_size REAL;
ALTER TABLE rules ADD COLUMN effect_size_type VARCHAR(20);
  -- 'cohen_d' | 'eta_squared' | 'r' | 'odds_ratio'

ALTER TABLE rules ADD COLUMN sample_size INTEGER;

-- Confidence decomposition (for MESO/MACRO rules)
ALTER TABLE rules ADD COLUMN confidence_triangulation REAL;
  -- Score from measure diversity

ALTER TABLE rules ADD COLUMN confidence_effect_strength REAL;
  -- Score from average effect size

ALTER TABLE rules ADD COLUMN confidence_sample_size REAL;
  -- Score from total N

-- Indexes for performance
CREATE INDEX idx_rules_level ON rules(rule_level);
CREATE INDEX idx_rules_parent ON rules(parent_rule_id);
CREATE INDEX idx_rules_measure ON rules(operational_measure);
CREATE INDEX idx_rules_framework ON rules(theoretical_framework);
```

---

## EXAMPLE: COMPLETE HIERARCHY

### Scenario: Processing 5 papers on biophilic design

**Papers**:
1. Study A: Plants in offices (cortisol, N=32)
2. Study B: Plants in classrooms (HR, BP, N=50)
3. Study C: Green walls (HRV, N=120)
4. Study D: Nature views (RT, accuracy, N=45)
5. Study E: Window access (sleep quality, N=85)

**Extracted Micro-Rules** (9 total):
```
1. Plants → cortisol↓ (p=.05, d=0.42, N=32) [A]
2. Plants → HR↓ (p=.01, d=0.56, N=50) [B]
3. Plants → BP↓ (p=.03, d=0.38, N=50) [B]
4. Green wall → HRV↑ (p=.02, d=0.51, N=120) [C]
5. Nature view → RT↓ (p=.01, d=0.61, N=45) [D]
6. Nature view → accuracy↑ (p=.02, d=0.49, N=45) [D]
7. Window → sleep_quality↑ (p=.04, d=0.44, N=85) [E]
8. Window → melatonin_rhythm (p=.03, d=0.39, N=85) [E]
9. Window → wake_time_regularity (p=.05, d=0.35, N=85) [E]
```

**Meta-Aggregated Meso-Rules** (3):
```
M1. Plants → stress_reduction (conf=0.89)
    └─ Children: [1,2,3,4] 
    └─ Measures: cortisol, HR, BP, HRV
    └─ Mechanism: biophilia_hypothesis

M2. Nature views → attention_restoration (conf=0.84)
    └─ Children: [5,6]
    └─ Measures: reaction_time, accuracy
    └─ Mechanism: attention_restoration_theory

M3. Window access → circadian_regulation (conf=0.81)
    └─ Children: [7,8,9]
    └─ Measures: sleep_quality, melatonin, wake_regularity
    └─ Mechanism: photoentrainment
```

**Synthesized Macro-Rule** (1):
```
MACRO. Biophilic design → improved wellbeing (conf=0.92)
       └─ Children: [M1, M2, M3]
       └─ Pathways: stress↓, attention↑, sleep↑
       └─ Framework: Biophilia Hypothesis (Wilson, 1984)
       └─ Unified by: Predictive Processing (natural = low prediction error)
```

**Final Hierarchy Display**:
```
▼ MACRO: Biophilic design → improved wellbeing [0.92]
  ⚙️ Framework: Biophilia Hypothesis, Predictive Processing
  │
  ├─▼ MESO: Plants → stress reduction [0.89]
  │  ⚙️ Mechanism: biophilia_hypothesis
  │  ├─ Plants → cortisol↓ (p=.05, d=0.42, N=32) [Study A: Offices]
  │  ├─ Plants → HR↓ (p=.01, d=0.56, N=50) [Study B: Classrooms]
  │  ├─ Plants → BP↓ (p=.03, d=0.38, N=50) [Study B: Classrooms]
  │  └─ Green wall → HRV↑ (p=.02, d=0.51, N=120) [Study C: Green walls]
  │
  ├─▼ MESO: Nature views → attention restoration [0.84]
  │  ⚙️ Mechanism: attention_restoration_theory
  │  ├─ Nature view → RT↓ (p=.01, d=0.61, N=45) [Study D: Views]
  │  └─ Nature view → accuracy↑ (p=.02, d=0.49, N=45) [Study D: Views]
  │
  └─▼ MESO: Window access → circadian regulation [0.81]
     ⚙️ Mechanism: photoentrainment
     ├─ Window → sleep_quality↑ (p=.04, d=0.44, N=85) [Study E: Windows]
     ├─ Window → melatonin_rhythm (p=.03, d=0.39, N=85) [Study E: Windows]
     └─ Window → wake_regularity (p=.05, d=0.35, N=85) [Study E: Windows]
```

---

## IMPLEMENTATION PRIORITY

**MUST HAVE (v16.0)**:
1. ✅ Schema: Add hierarchy fields to Rule model
2. ✅ Extraction: Capture operational measures from Panel 5
3. ✅ Extraction: Capture mechanisms from Panel 6
4. ✅ Aggregation: Meta-review logic (micro → meso)
5. ✅ Display: Tree view toggle

**SHOULD HAVE (v16.1)**:
6. ⚠️ Macro synthesis: Meso → macro aggregation
7. ⚠️ Mechanism validation: Check theoretical coherence
8. ⚠️ Confidence visualization: Show decomposition

**NICE TO HAVE (v17.0)**:
9. ◯ Network graph: D3.js visualization
10. ◯ Cross-job meta-analysis: Aggregate across projects
11. ◯ Export: Bayesian network format with hierarchy

---

## FILE CHANGES SUMMARY

**New Files**:
- `meta_review.py` - Aggregation logic
- `templates/_partials/rules_hierarchical.html` - Tree view

**Modified Files**:
- `models.py` - Add hierarchy fields
- `tasks.py` - Enhanced Panel 5&6 extraction
- `database_schema.sql` - ALTER TABLE migrations
- `templates/rules_view.html` - Add toggle buttons

**Total Implementation**: ~56 hours (7 development days)

---

**Version**: v15.8.1 → v16.0  
**Last Updated**: November 8, 2025