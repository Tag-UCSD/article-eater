# PHASE 1 IMPLEMENTATION PACKAGE
## Article Eater v15.8.1 → v16.0 Hierarchical Rules Upgrade

**Date**: November 8, 2025  
**Implementation Time**: 16 hours  
**Deliverables**: 5 production-ready components

---

## PACKAGE CONTENTS

1. **SQL Database Migrations** - Schema enhancements for hierarchy
2. **Enhanced 7-Panel Extraction** - Operational measures + mechanisms
3. **Meta-Review Aggregation Module** - Micro-to-meso synthesis
4. **Paper-to-Rules Analysis View** - Reverse lookup interface
5. **Integration Guide & Next Steps** - Deployment instructions

---

## COMPONENT 1: DATABASE SCHEMA MIGRATIONS

### File: `migrations/001_add_hierarchy_fields.sql`

```sql
-- ============================================================================
-- Migration 001: Add Hierarchical Rule Support
-- Article Eater v15.8.1 → v16.0
-- ============================================================================

-- Add hierarchy structure
ALTER TABLE rules ADD COLUMN rule_level VARCHAR(10);
  -- Values: 'micro', 'meso', 'macro'
  -- micro: Single study, single operational measure
  -- meso: Aggregated construct from multiple micro-rules
  -- macro: Theoretical framework-level principle

ALTER TABLE rules ADD COLUMN parent_rule_id INTEGER REFERENCES rules(id) ON DELETE CASCADE;
  -- Creates parent-child relationships
  -- micro.parent_rule_id → meso.id
  -- meso.parent_rule_id → macro.id

-- Add mechanism extraction fields
ALTER TABLE rules ADD COLUMN mechanism VARCHAR(255);
  -- e.g., 'predictive_processing_fluency', 'biophilia_hypothesis'

ALTER TABLE rules ADD COLUMN mechanism_description TEXT;
  -- Detailed explanation of how mechanism works

ALTER TABLE rules ADD COLUMN theoretical_framework VARCHAR(255);
  -- e.g., 'Predictive Processing', 'Embodied Cognition', 'Allostasis'

ALTER TABLE rules ADD COLUMN framework_references TEXT;
  -- JSON array of APA citations for framework

-- Add operational measure fields (for MICRO-level rules)
ALTER TABLE rules ADD COLUMN operational_measure VARCHAR(100);
  -- e.g., 'cortisol', 'heart_rate', 'reaction_time', 'accuracy'
  -- NULL for meso/macro rules

ALTER TABLE rules ADD COLUMN measure_type VARCHAR(50);
  -- 'physiological', 'behavioral', 'self_report'

ALTER TABLE rules ADD COLUMN measure_direction VARCHAR(20);
  -- 'increase', 'decrease', 'stable'

ALTER TABLE rules ADD COLUMN construct_measured VARCHAR(100);
  -- e.g., 'stress', 'anxiety', 'attention', 'mood'

-- Add statistical detail fields (for MICRO-level rules)
ALTER TABLE rules ADD COLUMN p_value REAL;
ALTER TABLE rules ADD COLUMN effect_size REAL;
ALTER TABLE rules ADD COLUMN effect_size_type VARCHAR(20);
  -- 'cohen_d', 'eta_squared', 'r', 'odds_ratio'

ALTER TABLE rules ADD COLUMN sample_size INTEGER;
ALTER TABLE rules ADD COLUMN statistical_test VARCHAR(100);
  -- e.g., 'paired_t_test', 'ANOVA', 'regression'

ALTER TABLE rules ADD COLUMN confidence_interval_lower REAL;
ALTER TABLE rules ADD COLUMN confidence_interval_upper REAL;

-- Add confidence decomposition (for MESO/MACRO rules)
ALTER TABLE rules ADD COLUMN confidence_triangulation REAL;
  -- Score from operational measure diversity (0-1)

ALTER TABLE rules ADD COLUMN confidence_effect_strength REAL;
  -- Score from average effect size (0-1)

ALTER TABLE rules ADD COLUMN confidence_sample_size REAL;
  -- Score from total sample size (0-1)

ALTER TABLE rules ADD COLUMN confidence_consistency REAL;
  -- Score from direction consistency across studies (0-1)

-- Add aggregation metadata (for MESO rules)
ALTER TABLE rules ADD COLUMN num_child_rules INTEGER DEFAULT 0;
ALTER TABLE rules ADD COLUMN operational_measures_used TEXT;
  -- JSON array: ["cortisol", "heart_rate", "blood_pressure"]

ALTER TABLE rules ADD COLUMN total_sample_size INTEGER;
  -- Sum of all child rule sample sizes

-- Performance indexes
CREATE INDEX idx_rules_level ON rules(rule_level);
CREATE INDEX idx_rules_parent ON rules(parent_rule_id);
CREATE INDEX idx_rules_measure ON rules(operational_measure);
CREATE INDEX idx_rules_framework ON rules(theoretical_framework);
CREATE INDEX idx_rules_construct ON rules(construct_measured);

-- Add comments for documentation
COMMENT ON COLUMN rules.rule_level IS 'Hierarchy level: micro (operational), meso (construct), macro (theoretical)';
COMMENT ON COLUMN rules.operational_measure IS 'Specific sensor/measure used (micro-rules only)';
COMMENT ON COLUMN rules.mechanism IS 'Proposed cognitive/neural mechanism';
COMMENT ON COLUMN rules.confidence_triangulation IS 'Confidence from measure diversity (meso-rules)';

-- ============================================================================
-- Validation Constraints
-- ============================================================================

-- Ensure micro-rules have operational measures
ALTER TABLE rules ADD CONSTRAINT check_micro_has_measure 
  CHECK (rule_level != 'micro' OR operational_measure IS NOT NULL);

-- Ensure parent-child relationships respect levels
-- (This would require a trigger in production; shown as comment)
-- CREATE TRIGGER enforce_hierarchy_levels ...

-- ============================================================================
-- Migration Rollback (if needed)
-- ============================================================================

-- DROP INDEX idx_rules_construct;
-- DROP INDEX idx_rules_framework;
-- DROP INDEX idx_rules_measure;
-- DROP INDEX idx_rules_parent;
-- DROP INDEX idx_rules_level;
-- ALTER TABLE rules DROP CONSTRAINT check_micro_has_measure;
-- ALTER TABLE rules DROP COLUMN total_sample_size;
-- ... (drop all added columns in reverse order)
```

### File: `migrations/002_update_evidence_table.sql`

```sql
-- ============================================================================
-- Migration 002: Enhance Evidence Table for Operational Details
-- Article Eater v16.0
-- ============================================================================

-- Add detailed experimental context to evidence table
ALTER TABLE evidence ADD COLUMN experimental_condition VARCHAR(255);
  -- e.g., 'treatment_group', 'control_group', 'curved_wall_condition'

ALTER TABLE evidence ADD COLUMN intervention_duration VARCHAR(100);
  -- e.g., '30_minutes', '2_weeks', 'single_exposure'

ALTER TABLE evidence ADD COLUMN pretest_value REAL;
ALTER TABLE evidence ADD COLUMN posttest_value REAL;
  -- For within-subjects designs

ALTER TABLE evidence ADD COLUMN device_used VARCHAR(255);
  -- Specific measuring device: 'Polar_H7_monitor', 'Tobii_eye_tracker'

ALTER TABLE evidence ADD COLUMN stimulus_description TEXT;
  -- Detailed description for replication

ALTER TABLE evidence ADD COLUMN stimulus_image_reference VARCHAR(500);
  -- Page number or figure reference in article

-- Index for querying by condition
CREATE INDEX idx_evidence_condition ON evidence(experimental_condition);
CREATE INDEX idx_evidence_device ON evidence(device_used);
```

---

## COMPONENT 2: ENHANCED 7-PANEL EXTRACTION

### File: `prompts/7_panel_extraction_v16_hierarchical.txt`

```
ARTICLE EATER v16.0: ENHANCED 7-PANEL EXTRACTION
For Hierarchical Rule Synthesis with Operational Measures

================================================================================
CRITICAL INSTRUCTIONS FOR PANEL 5 & 6 ENHANCEMENTS
================================================================================

Your task is to extract structured data from academic articles for evidence
synthesis in Cognitive Neuroscience for Architecture (CNfA). The output will
feed a hierarchical rule system with three levels:
  - MICRO: Individual operational measures (cortisol↓, RT↓, etc.)
  - MESO: Aggregated constructs (stress reduction, attention performance)
  - MACRO: Theoretical principles (Biophilic design → wellbeing)

Follow the 7-panel structure below with SPECIAL ATTENTION to Panels 5 & 6.

================================================================================
PANEL 1: CITATION INFORMATION
================================================================================

Provide:
• APA-format citation (include DOI if available)
• Citation count (Google Scholar or reliable source)
• Seminal/foundational status? (yes/no; if yes, explain briefly)

OUTPUT FORMAT:
{
  "citation_apa": "Author, A. (2020). Title. Journal, 12(3), 45-67. https://doi.org/...",
  "citation_doi": "10.1234/example",
  "citation_count": 145,
  "is_seminal": false,
  "seminal_explanation": null
}

================================================================================
PANEL 2: RESEARCH FOCUS
================================================================================

Provide:
• Main research question or topic
• Type of study (experimental, observational, survey, longitudinal, theoretical, neuro-imaging, etc.)
• Specific hypothesis or conjecture

OUTPUT FORMAT:
{
  "research_question": "Does exposure to curved architectural forms reduce anxiety?",
  "study_type": "experimental",
  "hypothesis": "Curved walls will elicit lower cortisol and anxiety ratings than angular walls"
}

================================================================================
PANEL 3: STUDY CONTEXT
================================================================================

Provide:
• Setting (physical lab, VR, field study, fMRI scanner, etc.)
• Type of building/feature studied (office, classroom, hospital, urban plaza, etc.)
• DETAILED stimulus description (sufficient for replication)
• Image/figure reference (page number or "Figure 3" in article)

OUTPUT FORMAT:
{
  "setting": "Virtual reality laboratory",
  "building_type": "Office interior",
  "stimulus_description": "Two identical 4x4m virtual offices differing only in wall curvature. Curved condition: walls with 2m radius convex curve. Angular condition: standard 90° corners. Both had identical furniture, lighting (500 lux), and window views.",
  "stimulus_image_reference": "Figure 2, page 1245"
}

================================================================================
PANEL 4: METHODOLOGY
================================================================================

Provide:
• Experimental conditions and control groups
• Experimental procedure (pretests, post-tests, intervention duration, steps)
• Number of subjects and demographics (age, gender, expert/novice, etc.)
• Measuring devices/sensors (eye tracking, EEG, fNIRS, GSR, HR monitors, etc.)

OUTPUT FORMAT:
{
  "experimental_conditions": [
    "Curved wall condition (treatment)",
    "Angular wall condition (control)"
  ],
  "procedure": "Within-subjects design. Participants experienced both conditions in counterbalanced order. Each exposure: 15 minutes. Baseline cortisol measured 10 min before, post-exposure at 20 min after entry. STAI administered after each condition.",
  "num_subjects": 68,
  "demographics": "Age: 22-34 (M=26.3, SD=3.1), 52% female, university students, no architecture training",
  "measuring_devices": [
    "Salivary cortisol assay (ELISA kit)",
    "State-Trait Anxiety Inventory (STAI)",
    "Heart rate monitor (Polar H7)"
  ]
}

================================================================================
PANEL 5: FINDINGS (*** ENHANCED FOR HIERARCHICAL RULES ***)
================================================================================

*** CRITICAL: Extract EVERY operational measure separately ***

For EACH outcome variable measured, provide:
1. The CONSTRUCT being assessed (stress, anxiety, attention, mood, etc.)
2. The OPERATIONAL MEASURE (cortisol, heart_rate, STAI score, etc.)
3. The MEASURE TYPE (physiological, behavioral, self_report)
4. The DIRECTION of effect (increase, decrease, stable)
5. COMPLETE STATISTICAL DETAILS:
   - p-value
   - Effect size (d, g, eta_squared, r, etc.) and TYPE
   - Sample size for this specific measure
   - Statistical test used
   - Confidence intervals (if reported)
   - Descriptive statistics (means, SDs)

*** DO NOT aggregate measures ***
*** Report cortisol, heart_rate, and STAI as SEPARATE findings ***

OUTPUT FORMAT:
{
  "main_finding_summary": "Curved walls reduced anxiety compared to angular walls",
  
  "operational_findings": [
    {
      "construct": "anxiety",
      "operational_measure": "salivary_cortisol",
      "measure_type": "physiological",
      "measure_direction": "decrease",
      "statistical_details": {
        "p_value": 0.03,
        "effect_size": 0.52,
        "effect_size_type": "cohen_d",
        "sample_size": 68,
        "statistical_test": "paired_t_test",
        "confidence_interval": [0.18, 0.86],
        "descriptives": {
          "curved_mean": 12.3,
          "curved_sd": 3.2,
          "angular_mean": 15.7,
          "angular_sd": 4.1,
          "units": "nmol/L"
        }
      }
    },
    {
      "construct": "anxiety",
      "operational_measure": "state_anxiety_inventory",
      "measure_type": "self_report",
      "measure_direction": "decrease",
      "statistical_details": {
        "p_value": 0.01,
        "effect_size": 0.64,
        "effect_size_type": "cohen_d",
        "sample_size": 68,
        "statistical_test": "paired_t_test",
        "confidence_interval": [0.28, 1.00],
        "descriptives": {
          "curved_mean": 32.1,
          "curved_sd": 8.4,
          "angular_mean": 37.8,
          "angular_sd": 9.2,
          "units": "STAI_score"
        }
      }
    },
    {
      "construct": "physiological_arousal",
      "operational_measure": "heart_rate",
      "measure_type": "physiological",
      "measure_direction": "decrease",
      "statistical_details": {
        "p_value": 0.08,
        "effect_size": 0.31,
        "effect_size_type": "cohen_d",
        "sample_size": 68,
        "statistical_test": "paired_t_test",
        "confidence_interval": [-0.04, 0.66],
        "descriptives": {
          "curved_mean": 72.3,
          "curved_sd": 11.2,
          "angular_mean": 75.1,
          "angular_sd": 12.8,
          "units": "bpm"
        }
      }
    }
  ],
  
  "tables_summary": "Table 2 shows full descriptive statistics for all measures across conditions",
  
  "figures_summary": "Figure 3 displays cortisol time-course; Figure 4 shows STAI score distributions"
}

================================================================================
PANEL 6: DISCUSSION & THEORETICAL INSIGHTS (*** ENHANCED ***)
================================================================================

*** CRITICAL: Extract proposed MECHANISMS ***

For EACH finding, identify:
1. The MECHANISM proposed by authors to explain the effect
2. The THEORETICAL FRAMEWORK invoked (Predictive Processing, Embodied Cognition, etc.)
3. The EVIDENCE STRENGTH for this mechanism (strong, moderate, speculative)
4. CITATIONS for the theoretical framework
5. Any NEURAL BASIS mentioned (brain regions, neurotransmitters, etc.)

OUTPUT FORMAT:
{
  "discussion_main_points": [
    "Curved forms reduce anxiety through reduced prediction error",
    "Results align with evolutionary preferences for natural, organic shapes",
    "Limitations: Lab setting may not generalize to real offices; short exposure time"
  ],
  
  "mechanisms": [
    {
      "mechanism_name": "predictive_processing_fluency",
      "mechanism_description": "Curved forms are processed more fluently in visual cortex, reducing prediction error and cognitive load. Lower prediction error signals safety, reducing anxiety.",
      "theoretical_framework": "Predictive Processing / Free Energy Principle",
      "evidence_strength": "moderate",
      "neural_basis": "Reduced BOLD signal in fusiform face area (FFA) during curve processing (Bar et al., 2006)",
      "supporting_citations": [
        "Friston, K. (2010). The free-energy principle: A unified brain theory? Nature Reviews Neuroscience, 11(2), 127-138.",
        "Bar, M. (2004). Visual objects in context. Nature Reviews Neuroscience, 5(8), 617-629."
      ]
    },
    {
      "mechanism_name": "evolutionary_preference_natural_forms",
      "mechanism_description": "Humans evolved in natural environments dominated by curved, organic shapes. Angular forms signal potential threats (sharp objects, predators).",
      "theoretical_framework": "Evolutionary Psychology / Biophilia Hypothesis",
      "evidence_strength": "speculative",
      "neural_basis": "Amygdala response to angular shapes (Vartanian et al., 2013)",
      "supporting_citations": [
        "Wilson, E. O. (1984). Biophilia. Harvard University Press.",
        "Vartanian, O., et al. (2013). Impact of contour on aesthetic judgments. Neuropsychologia, 51(1), 80-93."
      ]
    }
  ],
  
  "additional_frameworks": [
    {
      "framework": "Stress Reduction Theory",
      "application": "Curved environments may facilitate parasympathetic activation",
      "citation": "Ulrich, R. S. (1991). Stress recovery during exposure to natural environments."
    }
  ],
  
  "limitations": [
    "Short exposure duration (15 min) may not reflect chronic effects",
    "Virtual reality may lack ecological validity",
    "Student sample limits generalizability to working professionals"
  ]
}

================================================================================
PANEL 7: KEY REFERENCES
================================================================================

List top 3-5 most important references from article's bibliography.
Prioritize seminal/foundational works.

OUTPUT FORMAT:
{
  "key_references": [
    "Friston, K. (2010). The free-energy principle: A unified brain theory? Nature Reviews Neuroscience, 11(2), 127-138.",
    "Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. Psychological Science, 17(8), 645-648.",
    "Vartanian, O., et al. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. PNAS, 110(Suppl 2), 10446-10453."
  ]
}

================================================================================
QUALITY CHECKLIST
================================================================================

Before submitting, verify:
□ Panel 5: Each operational measure extracted separately (not aggregated)
□ Panel 5: All statistical details complete (p, d, N, CI, descriptives)
□ Panel 5: Measure type and direction specified for each
□ Panel 6: At least one mechanism identified with theoretical framework
□ Panel 6: Evidence strength rated (strong/moderate/speculative)
□ Panel 6: APA citations provided for all frameworks
□ All panels: No hallucinated data - only information from actual article
□ Reproducibility: Stimulus description detailed enough to replicate

================================================================================
FINAL OUTPUT FORMAT
================================================================================

Return a SINGLE JSON object with all 7 panels:

{
  "panel_1_citation": { ... },
  "panel_2_research_focus": { ... },
  "panel_3_study_context": { ... },
  "panel_4_methodology": { ... },
  "panel_5_findings": { ... },
  "panel_6_discussion": { ... },
  "panel_7_references": { ... }
}
```

---

## COMPONENT 3: META-REVIEW AGGREGATION MODULE

### File: `meta_review.py`

```python
"""
Meta-Review Aggregation Module
===============================
Aggregates micro-rules into meso-rules based on operational measure diversity.

Article Eater v16.0 - Hierarchical Rule Synthesis

This module implements the core logic for creating hierarchical rule structures:
  MICRO-RULES: Individual operational measures from single studies
    → "Plants → cortisol↓ (p<.05, d=0.42, N=32)"
  
  MESO-RULES: Aggregated constructs from multiple micro-rules
    → "Plants → stress reduction" (from cortisol, HR, BP, HRV)
  
  MACRO-RULES: Theoretical principles (future implementation)
    → "Biophilic design → improved wellbeing"

Example Usage:
    from meta_review import find_aggregation_opportunities, aggregate_to_meso
    
    # Find micro-rules that can be aggregated
    opportunities = find_aggregation_opportunities()
    
    # Create meso-rules
    for micro_group in opportunities:
        meso_rule = aggregate_to_meso(micro_group)
        session.add(meso_rule)
"""

from typing import List, Dict, Set, Tuple, Optional
from models import Rule
from database import session_scope
import json
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Construct Mapping: Operational Measures → Theoretical Constructs
# ============================================================================

STRESS_MEASURES = {
    'cortisol', 'salivary_cortisol', 'serum_cortisol',
    'heart_rate', 'hr', 'pulse',
    'blood_pressure', 'systolic_bp', 'diastolic_bp',
    'hrv', 'heart_rate_variability', 'rmssd',
    'skin_conductance', 'gsr', 'eda',
    'state_anxiety', 'stai', 'perceived_stress', 'pss'
}

ATTENTION_MEASURES = {
    'reaction_time', 'rt', 'response_time',
    'accuracy', 'error_rate', 'correct_responses',
    'omission_errors', 'commission_errors',
    'digit_span', 'working_memory_span',
    'sustained_attention', 'vigilance',
    'd_prime', 'signal_detection'
}

MOOD_MEASURES = {
    'panas_positive', 'panas_negative',
    'valence', 'arousal',
    'mood_rating', 'affect_grid',
    'positive_affect', 'negative_affect',
    'depression_score', 'bdi',
    'life_satisfaction', 'happiness_scale'
}

MEMORY_MEASURES = {
    'recall_accuracy', 'recognition_accuracy',
    'free_recall', 'cued_recall',
    'working_memory_capacity', 'wm_span',
    'spatial_memory', 'verbal_memory',
    'episodic_memory', 'semantic_memory'
}

SOCIAL_MEASURES = {
    'interpersonal_distance', 'proxemics',
    'social_interaction_frequency',
    'collaboration_quality', 'team_performance',
    'trust_rating', 'social_cohesion'
}

PERFORMANCE_MEASURES = {
    'task_completion_time', 'productivity',
    'task_accuracy', 'work_quality',
    'creative_output', 'problem_solving',
    'decision_making_quality'
}

CONSTRUCT_MAP = {
    'stress_reduction': STRESS_MEASURES,
    'anxiety_reduction': STRESS_MEASURES,  # Overlaps with stress
    'attention_performance': ATTENTION_MEASURES,
    'focus_capacity': ATTENTION_MEASURES,
    'affective_state': MOOD_MEASURES,
    'mood_regulation': MOOD_MEASURES,
    'memory_performance': MEMORY_MEASURES,
    'cognitive_capacity': MEMORY_MEASURES,
    'social_facilitation': SOCIAL_MEASURES,
    'task_performance': PERFORMANCE_MEASURES
}


# ============================================================================
# Micro-Rule Aggregation
# ============================================================================

def find_aggregation_opportunities() -> List[List[Rule]]:
    """
    Identify groups of micro-rules that should be aggregated into meso-rules.
    
    Grouping criteria:
    1. Share same antecedents (e.g., all have "plants" as stimulus)
    2. Operational measures map to same theoretical construct
    3. At least 2 micro-rules in group (minimum for triangulation)
    
    Returns:
        List of micro-rule groups ready for aggregation
    """
    with session_scope() as session:
        # Get all micro-level rules
        micro_rules = session.query(Rule).filter_by(rule_level='micro').all()
        
        if not micro_rules:
            logger.info("No micro-rules found for aggregation")
            return []
        
        # Group by antecedents (stimulus variables)
        grouped_by_antecedent = {}
        for rule in micro_rules:
            key = rule.antecedents  # JSON string
            if key not in grouped_by_antecedent:
                grouped_by_antecedent[key] = []
            grouped_by_antecedent[key].append(rule)
        
        # Filter groups with 2+ rules measuring similar constructs
        opportunities = []
        for antecedent_key, rules in grouped_by_antecedent.items():
            if len(rules) < 2:
                continue
            
            # Check if measures map to same construct
            construct = infer_construct_from_measures(rules)
            if construct and construct != "unknown_construct":
                opportunities.append(rules)
                logger.info(f"Found aggregation opportunity: {len(rules)} micro-rules → {construct}")
        
        logger.info(f"Total aggregation opportunities: {len(opportunities)}")
        return opportunities


def aggregate_to_meso(micro_rules: List[Rule]) -> Rule:
    """
    Create a meso-rule by aggregating multiple micro-rules.
    
    Process:
    1. Infer theoretical construct from operational measures
    2. Calculate meta-confidence from triangulation
    3. Create meso-rule with proper relationships
    4. Update child rules to link to parent
    
    Args:
        micro_rules: List of micro-rules sharing antecedents
    
    Returns:
        New meso-rule with aggregated confidence
    """
    if not micro_rules:
        raise ValueError("Cannot aggregate empty micro-rule list")
    
    # Infer construct from operational measures
    construct = infer_construct_from_measures(micro_rules)
    if not construct:
        raise ValueError("Could not infer construct from micro-rules")
    
    # Extract common antecedents
    antecedents = micro_rules[0].antecedents
    
    # Calculate aggregated confidence with decomposition
    confidence_scores = calculate_meta_confidence(micro_rules)
    total_confidence = sum(confidence_scores.values())
    
    # Collect operational measures used
    measures_used = list(set(r.operational_measure for r in micro_rules if r.operational_measure))
    
    # Sum sample sizes
    total_n = sum(r.sample_size or 0 for r in micro_rules)
    
    # Create meso-rule
    meso_rule = Rule(
        consequent=construct,
        antecedents=antecedents,
        weight=total_confidence,
        rule_level='meso',
        rule_type='meta_aggregated',
        num_child_rules=len(micro_rules),
        operational_measures_used=json.dumps(measures_used),
        total_sample_size=total_n,
        confidence_triangulation=confidence_scores['triangulation'],
        confidence_effect_strength=confidence_scores['effect_strength'],
        confidence_sample_size=confidence_scores['sample_size'],
        confidence_consistency=confidence_scores['consistency']
    )
    
    logger.info(f"Created meso-rule: {antecedents} → {construct} (conf={total_confidence:.2f})")
    logger.info(f"  Based on {len(micro_rules)} micro-rules, {len(measures_used)} measures, N={total_n}")
    
    return meso_rule


def infer_construct_from_measures(rules: List[Rule]) -> Optional[str]:
    """
    Map operational measures to theoretical construct.
    
    Uses CONSTRUCT_MAP to find best match based on measure overlap.
    
    Args:
        rules: List of rules with operational_measure fields
    
    Returns:
        Theoretical construct name or None
    """
    # Extract all operational measures
    measures = set()
    for r in rules:
        if r.operational_measure:
            measures.add(r.operational_measure.lower())
    
    if not measures:
        logger.warning("No operational measures found in rules")
        return None
    
    # Find best matching construct
    best_construct = None
    best_overlap = 0
    
    for construct, measure_set in CONSTRUCT_MAP.items():
        overlap = len(measures & measure_set)
        if overlap > best_overlap:
            best_overlap = overlap
            best_construct = construct
    
    # Require at least 2 measures to match
    if best_overlap >= 2:
        logger.info(f"Inferred construct '{best_construct}' from {best_overlap} overlapping measures")
        return best_construct
    
    # Fallback: use most common construct_measured field
    constructs = [r.construct_measured for r in rules if r.construct_measured]
    if constructs:
        fallback = max(set(constructs), key=constructs.count)
        logger.info(f"Using fallback construct from rules: {fallback}")
        return fallback
    
    logger.warning("Could not infer construct from measures")
    return None


def calculate_meta_confidence(rules: List[Rule]) -> Dict[str, float]:
    """
    Calculate aggregated confidence with decomposition.
    
    Four components:
    1. Triangulation: More unique operational measures = higher confidence
    2. Effect Strength: Larger average effect sizes = higher confidence
    3. Sample Size: Larger total N = higher confidence
    4. Consistency: All effects in same direction = higher confidence
    
    Args:
        rules: List of micro-rules to aggregate
    
    Returns:
        Dict with component scores and total
    """
    # Component 1: Triangulation (0-0.4)
    unique_measures = len(set(r.operational_measure for r in rules if r.operational_measure))
    triangulation = min(unique_measures / 4.0, 1.0) * 0.4
    
    # Component 2: Effect Strength (0-0.3)
    effect_sizes = [r.effect_size for r in rules if r.effect_size]
    if effect_sizes:
        avg_effect = sum(effect_sizes) / len(effect_sizes)
        # Cohen's d benchmarks: 0.2=small, 0.5=medium, 0.8=large
        effect_strength = min(avg_effect / 0.8, 1.0) * 0.3
    else:
        effect_strength = 0.15  # Default medium if not reported
    
    # Component 3: Sample Size (0-0.2)
    total_n = sum(r.sample_size or 0 for r in rules)
    # Benchmark: 200+ participants = full score
    sample_strength = min(total_n / 200.0, 1.0) * 0.2
    
    # Component 4: Consistency (0-0.1)
    directions = [r.measure_direction for r in rules if r.measure_direction]
    direction_consistent = len(set(directions)) == 1 if directions else False
    consistency = 0.1 if direction_consistent else 0.0
    
    logger.debug(f"Confidence components: tri={triangulation:.2f}, eff={effect_strength:.2f}, "
                 f"sam={sample_strength:.2f}, con={consistency:.2f}")
    
    return {
        'triangulation': triangulation,
        'effect_strength': effect_strength,
        'sample_size': sample_strength,
        'consistency': consistency
    }


# ============================================================================
# Batch Aggregation
# ============================================================================

def aggregate_all_micro_rules() -> List[Rule]:
    """
    Find all aggregation opportunities and create meso-rules.
    
    This is typically called after processing all articles in a job,
    before presenting final rules to user.
    
    Returns:
        List of newly created meso-rules
    """
    opportunities = find_aggregation_opportunities()
    
    if not opportunities:
        logger.info("No aggregation opportunities found")
        return []
    
    meso_rules = []
    
    with session_scope() as session:
        for micro_group in opportunities:
            try:
                meso_rule = aggregate_to_meso(micro_group)
                session.add(meso_rule)
                session.flush()  # Get ID assigned
                
                # Update child rules to link to parent
                for micro in micro_group:
                    micro.parent_rule_id = meso_rule.id
                
                meso_rules.append(meso_rule)
                
            except Exception as e:
                logger.error(f"Failed to aggregate micro-group: {e}")
                continue
        
        session.commit()
    
    logger.info(f"Successfully created {len(meso_rules)} meso-rules from {len(opportunities)} opportunities")
    return meso_rules


# ============================================================================
# Quality Validation
# ============================================================================

def validate_aggregation_quality(meso_rule: Rule) -> Dict[str, any]:
    """
    Assess quality of a meso-rule aggregation.
    
    Criteria:
    - Sufficient triangulation (2+ measures)
    - Reasonable confidence (>0.5)
    - Adequate sample size (N>30 total)
    - Consistent direction
    
    Returns:
        Quality report dict
    """
    with session_scope() as session:
        # Get child rules
        children = session.query(Rule).filter_by(parent_rule_id=meso_rule.id).all()
        
        measures = json.loads(meso_rule.operational_measures_used or '[]')
        
        report = {
            'rule_id': meso_rule.id,
            'consequent': meso_rule.consequent,
            'quality_score': 0.0,
            'issues': [],
            'strengths': []
        }
        
        # Check triangulation
        if len(measures) >= 3:
            report['strengths'].append(f"Good triangulation: {len(measures)} operational measures")
            report['quality_score'] += 0.3
        elif len(measures) == 2:
            report['strengths'].append("Adequate triangulation: 2 measures")
            report['quality_score'] += 0.2
        else:
            report['issues'].append("Weak triangulation: <2 measures")
        
        # Check confidence
        if meso_rule.weight >= 0.7:
            report['strengths'].append(f"High confidence: {meso_rule.weight:.2f}")
            report['quality_score'] += 0.3
        elif meso_rule.weight >= 0.5:
            report['strengths'].append(f"Adequate confidence: {meso_rule.weight:.2f}")
            report['quality_score'] += 0.2
        else:
            report['issues'].append(f"Low confidence: {meso_rule.weight:.2f}")
        
        # Check sample size
        total_n = meso_rule.total_sample_size or 0
        if total_n >= 100:
            report['strengths'].append(f"Large sample: N={total_n}")
            report['quality_score'] += 0.2
        elif total_n >= 50:
            report['strengths'].append(f"Adequate sample: N={total_n}")
            report['quality_score'] += 0.1
        else:
            report['issues'].append(f"Small sample: N={total_n}")
        
        # Check direction consistency
        if meso_rule.confidence_consistency > 0:
            report['strengths'].append("Consistent effect direction")
            report['quality_score'] += 0.2
        else:
            report['issues'].append("Inconsistent effect directions across studies")
        
        return report


if __name__ == "__main__":
    # Example usage for testing
    logging.basicConfig(level=logging.INFO)
    
    # Find and aggregate
    meso_rules = aggregate_all_micro_rules()
    
    # Validate each
    for meso in meso_rules:
        report = validate_aggregation_quality(meso)
        print(f"\n{report['consequent']}: Quality={report['quality_score']:.2f}")
        for strength in report['strengths']:
            print(f"  ✓ {strength}")
        for issue in report['issues']:
            print(f"  ⚠ {issue}")
```

---

## COMPONENT 4: PAPER-TO-RULES ANALYSIS VIEW

### File: `app/routes_papers.py`

```python
"""
Paper-to-Rules Analysis Routes
===============================
Provides reverse lookup: Paper → Rules → Evidence

Addresses critical gap: Users need to see ALL rules derived from a specific paper
for validation, quality assessment, and literature gap analysis.

Routes:
    GET /paper/<paper_id>/analysis - Show all rules from this paper
"""

from flask import Blueprint, render_template, jsonify
from .artifacts import read_json
from pathlib import Path
from urllib.parse import unquote
import re
import logging

bp = Blueprint('papers', __name__)
logger = logging.getLogger(__name__)

@bp.route("/paper/<path:paper_id>/analysis", methods=["GET"])
def paper_analysis(paper_id):
    """
    Show all rules and evidence derived from a specific paper.
    
    Args:
        paper_id: DOI (URL-encoded) or internal identifier
    
    Returns:
        Rendered template with paper analysis
    """
    # URL-decode paper_id (handles DOIs with slashes)
    paper_id = unquote(paper_id)
    logger.info(f"Analyzing paper: {paper_id}")
    
    paper_data = initialize_paper_data(paper_id)
    
    # Search across all jobs for this paper
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
    
    logger.info(f"Paper analysis complete: {len(paper_data['rules_derived'])} rules, "
                f"{len(paper_data['evidence_passages'])} evidence items")
    
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
            
            logger.debug(f"Found paper in shortlist: {job_dir.name}")


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
                'operational_measure': e.get('operational_measure'),  # NEW in v16
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
                'rule_level': r.get('rule_level', 'meso'),  # NEW in v16
                'operational_measure': r.get('operational_measure'),  # NEW in v16
                'mechanism': r.get('mechanism'),  # NEW in v16
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

---

## COMPONENT 5: INTEGRATION GUIDE

### File: `DEPLOYMENT_GUIDE_v16.0.md`

```markdown
# Article Eater v16.0 Deployment Guide
## Hierarchical Rules Implementation

**Deployment Time**: 2-4 hours  
**Rollback Time**: 15 minutes  
**Testing Required**: Yes (see checklist)

---

## PRE-DEPLOYMENT CHECKLIST

□ Backup production database
□ Backup `findings/` directory
□ Verify Python 3.11+ installed
□ Verify SQLAlchemy 2.0+ installed
□ Review migration scripts for syntax
□ Create rollback plan

---

## STEP 1: DATABASE MIGRATIONS (30 minutes)

### 1.1 Backup Database

```bash
# For SQLite
cp article_eater.db article_eater.db.backup_pre_v16

# For PostgreSQL
pg_dump article_eater > backup_pre_v16.sql
```

### 1.2 Run Migrations

```bash
# Apply schema enhancements
sqlite3 article_eater.db < migrations/001_add_hierarchy_fields.sql
sqlite3 article_eater.db < migrations/002_update_evidence_table.sql

# Verify migrations
sqlite3 article_eater.db "PRAGMA table_info(rules);" | grep rule_level
# Should show: rule_level|VARCHAR(10)|0||0
```

### 1.3 Test Migration

```bash
# Create test micro-rule
sqlite3 article_eater.db << SQL
INSERT INTO rules (consequent, antecedents, weight, rule_level, operational_measure)
VALUES ('stress_reduction', '["plants"]', 0.7, 'micro', 'cortisol');

SELECT id, consequent, rule_level, operational_measure FROM rules ORDER BY id DESC LIMIT 1;
SQL
# Should display the new rule with all fields
```

---

## STEP 2: INSTALL NEW MODULES (15 minutes)

### 2.1 Copy Files

```bash
# Copy meta-review module
cp meta_review.py /path/to/article_eater/

# Copy paper analysis routes
cp app/routes_papers.py /path/to/article_eater/app/

# Copy enhanced templates (if provided separately)
cp templates/paper_analysis.html /path/to/article_eater/templates/
cp templates/_partials/rules_hierarchical.html /path/to/article_eater/templates/_partials/
```

### 2.2 Register Blueprint

Edit `app/app.py`, add after existing blueprint registrations:

```python
# --- PAPER ANALYSIS ROUTES (v16.0) ---
try:
    from .routes_papers import bp as papers_bp
    app.register_blueprint(papers_bp)
except Exception as e:
    print("[WARN] Could not register papers blueprint:", e)
```

### 2.3 Verify Import

```bash
python3 -c "from meta_review import aggregate_all_micro_rules; print('✓ meta_review loaded')"
python3 -c "from app.routes_papers import bp; print('✓ routes_papers loaded')"
```

---

## STEP 3: UPDATE 7-PANEL EXTRACTION (30 minutes)

### 3.1 Update Anthropic API Call

In `tasks.py` (or wherever LLM synthesis occurs), replace the Panel 5/6 prompt:

```python
# Load enhanced prompt
with open('prompts/7_panel_extraction_v16_hierarchical.txt', 'r') as f:
    ENHANCED_PROMPT = f.read()

def call_llm_for_summary(article_text: str) -> dict:
    """Calls LLM with enhanced 7-panel prompt."""
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": ENHANCED_PROMPT + "\n\nARTICLE TEXT:\n" + article_text
        }]
    )
    return response.content[0].text
```

### 3.2 Update Rule Creation Logic

Modify rule synthesis to create micro-rules from operational findings:

```python
def create_rules_from_7panel(panel_data: dict, job_id: str):
    """Create hierarchical rules from enhanced 7-panel data."""
    
    # Extract operational findings from Panel 5
    operational_findings = panel_data.get('panel_5_findings', {}).get('operational_findings', [])
    
    micro_rules = []
    for finding in operational_findings:
        # Create micro-rule for each operational measure
        micro_rule = {
            'rule': f"{get_antecedent(panel_data)} → {finding['construct']}",
            'rule_level': 'micro',
            'operational_measure': finding['operational_measure'],
            'measure_type': finding['measure_type'],
            'measure_direction': finding['measure_direction'],
            'construct_measured': finding['construct'],
            'p_value': finding['statistical_details']['p_value'],
            'effect_size': finding['statistical_details']['effect_size'],
            'effect_size_type': finding['statistical_details']['effect_size_type'],
            'sample_size': finding['statistical_details']['sample_size'],
            'statistical_test': finding['statistical_details']['statistical_test'],
            'confidence': calculate_micro_confidence(finding),
            'provenance': [extract_citation(panel_data)]
        }
        micro_rules.append(micro_rule)
    
    # Write micro-rules
    write_json(job_id, "rules", {"rules": micro_rules, "rule_level": "micro"})
    
    return micro_rules
```

---

## STEP 4: TESTING (60 minutes)

### 4.1 Unit Tests

```python
# test_meta_review.py
import unittest
from meta_review import infer_construct_from_measures, calculate_meta_confidence
from models import Rule

class TestMetaReview(unittest.TestCase):
    def test_construct_inference(self):
        rules = [
            Rule(operational_measure='cortisol'),
            Rule(operational_measure='heart_rate'),
            Rule(operational_measure='blood_pressure')
        ]
        construct = infer_construct_from_measures(rules)
        self.assertIn(construct, ['stress_reduction', 'anxiety_reduction'])
    
    def test_confidence_calculation(self):
        rules = [
            Rule(operational_measure='cortisol', effect_size=0.5, sample_size=50, measure_direction='decrease'),
            Rule(operational_measure='heart_rate', effect_size=0.6, sample_size=50, measure_direction='decrease')
        ]
        scores = calculate_meta_confidence(rules)
        self.assertGreater(scores['triangulation'], 0)
        self.assertGreater(scores['consistency'], 0)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python test_meta_review.py
```

### 4.2 Integration Tests

**Test 1: Full Pipeline with Hierarchical Rules**

```bash
# 1. Create test job
curl -X POST http://localhost:8080/ingest \
  -F "mode=doi_list" \
  -F "dois=10.1234/test1
10.1234/test2
10.1234/test3"

# 2. Process articles (manually trigger 7-panel extraction)

# 3. Verify micro-rules created
sqlite3 article_eater.db "SELECT COUNT(*) FROM rules WHERE rule_level='micro';"
# Should be >0

# 4. Run meta-aggregation
python3 << PY
from meta_review import aggregate_all_micro_rules
meso_rules = aggregate_all_micro_rules()
print(f"Created {len(meso_rules)} meso-rules")
PY

# 5. Verify meso-rules
sqlite3 article_eater.db "SELECT COUNT(*) FROM rules WHERE rule_level='meso';"
# Should be >0

# 6. Check parent-child relationships
sqlite3 article_eater.db "SELECT id, rule_level, parent_rule_id FROM rules ORDER BY id;"
# Micro-rules should have non-null parent_rule_id pointing to meso-rules
```

**Test 2: Paper-to-Rules Analysis**

```bash
# Find a DOI from your test data
DOI="10.1234/test1"

# Access paper analysis view
curl http://localhost:8080/paper/$(echo $DOI | jq -sRr @uri)/analysis

# Should return HTML with rules derived from that paper
```

### 4.3 Regression Tests

□ Existing JSON-based jobs still work  
□ Flat rules view still displays correctly  
□ Jobs index shows all jobs  
□ RAG settings page functional  
□ Monitor page displays correctly  

---

## STEP 5: DATA MIGRATION (Optional, 45 minutes)

If you have existing rules in JSON format that need hierarchy:

### 5.1 Mark Existing Rules as Meso-Level

```bash
# All existing rules are assumed meso-level by default
sqlite3 article_eater.db << SQL
UPDATE rules 
SET rule_level = 'meso',
    rule_type = 'legacy_flat'
WHERE rule_level IS NULL;
SQL
```

### 5.2 Attempt Micro-Rule Inference

If your existing rules have provenance with statistical details, you can attempt to reconstruct micro-rules:

```python
# migrate_legacy_rules.py
from models import Rule, Evidence
from database import session_scope

with session_scope() as session:
    # Get all legacy meso rules
    meso_rules = session.query(Rule).filter_by(rule_type='legacy_flat').all()
    
    for meso in meso_rules:
        # Get evidence items
        evidence_items = session.query(Evidence).filter_by(rule_id=meso.id).all()
        
        for ev in evidence_items:
            # If evidence has statistical details, create micro-rule
            if ev.statistical_support:
                # Parse statistical support (depends on your format)
                # Create micro-rule
                # Link to meso as parent
                pass
```

---

## STEP 6: USER DOCUMENTATION (30 minutes)

### 6.1 Update README

Add section explaining hierarchical rules:

```markdown
## Hierarchical Rules (v16.0)

Article Eater now supports three-level rule hierarchies:

**MICRO-RULES**: Individual operational measures
- Example: "Plants → cortisol↓ (p<.05, d=0.42, N=32)"

**MESO-RULES**: Aggregated theoretical constructs
- Example: "Plants → stress reduction" (from 4 operational measures)

**MACRO-RULES**: High-level principles (future)
- Example: "Biophilic design → improved wellbeing"

### Viewing Hierarchical Rules

1. Navigate to `/rules/<job_id>/view`
2. Toggle between "Flat List" and "Tree Structure"
3. Tree view shows parent-child relationships
4. Click mechanisms to see theoretical frameworks
```

### 6.2 Create Quick Start Guide

```markdown
## Quick Start: Hierarchical Rule Synthesis

1. **Ingest**: Upload papers or DOI list as usual
2. **Extract**: 7-panel analysis now captures operational measures
3. **Review Micro**: Individual findings appear as micro-rules
4. **Aggregate**: Run meta-review to create meso-rules
   ```python
   from meta_review import aggregate_all_micro_rules
   aggregate_all_micro_rules()
   ```
5. **Visualize**: View hierarchical tree in rules view
```

---

## ROLLBACK PROCEDURE (if needed)

If issues arise, rollback in reverse order:

```bash
# 1. Stop application
sudo systemctl stop article-eater

# 2. Restore database
cp article_eater.db.backup_pre_v16 article_eater.db

# 3. Remove new modules
rm meta_review.py
rm app/routes_papers.py

# 4. Revert app.py changes (remove papers blueprint registration)

# 5. Restart application
sudo systemctl start article-eater
```

---

## POST-DEPLOYMENT MONITORING

### Week 1: Watch for Issues

□ Monitor error logs for Python exceptions  
□ Check database query performance  
□ Verify aggregation runs successfully  
□ Collect user feedback on hierarchical views  

### Week 2-4: Optimization

□ Add indexes if queries slow  
□ Tune confidence calculation thresholds  
□ Refine construct inference mappings  
□ Improve empty state messaging  

---

## SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue**: Meta-aggregation creates no meso-rules

*Solution*: Check that micro-rules have `operational_measure` populated. Run:
```sql
SELECT COUNT(*) FROM rules WHERE rule_level='micro' AND operational_measure IS NULL;
```
If >0, re-run 7-panel extraction with enhanced prompt.

**Issue**: Parent-child relationships broken

*Solution*: Verify foreign key constraint:
```sql
SELECT * FROM rules WHERE parent_rule_id IS NOT NULL 
AND parent_rule_id NOT IN (SELECT id FROM rules);
```
Should return 0 rows.

**Issue**: Paper analysis shows no rules

*Solution*: Check DOI normalization. Try both with and without `https://doi.org/` prefix.

---

## SUCCESS CRITERIA

✅ Database migrated with no data loss  
✅ Micro-rules created from 7-panel extraction  
✅ Meso-rules aggregated from micro-rules  
✅ Hierarchical tree view displays correctly  
✅ Paper-to-rules analysis functional  
✅ All regression tests pass  
✅ Documentation updated  

---

**Version**: v15.8.1 → v16.0  
**Deployed By**: _______________  
**Date**: _______________  
**Rollback Tested**: Yes / No  
```

---

## NEXT STEPS AFTER PHASE 1

### Immediate (Week 1-2 Post-Deployment)

1. **Monitor Production Usage**
   - Watch error logs for exceptions
   - Track aggregation success rate
   - Collect user feedback on hierarchy views

2. **Quick Wins**
   - Add "Aggregate Rules" button to jobs view
   - Implement export of hierarchical rules to JSON
   - Create example jobs showcasing micro→meso→macro

### Short-Term (Month 2)

3. **Phase 2: Macro-Rule Synthesis**
   - Identify patterns across meso-rules
   - Create macro-rules from theoretical frameworks
   - Add macro level to tree visualization

4. **Enhanced Mechanism Extraction**
   - Improve Panel 6 parsing for mechanisms
   - Add mechanism validation (check citations)
   - Create mechanism taxonomy

### Medium-Term (Month 3-4)

5. **Phase 3: Network Visualization**
   - Implement D3.js network graph
   - Show explanatory relationships (mechanism links)
   - Allow interactive exploration

6. **Cross-Job Meta-Analysis**
   - Aggregate rules across multiple jobs
   - Identify literature gaps
   - Generate comprehensive CNfA knowledge base

### Long-Term (v17.0)

7. **Bayesian Network Export**
   - Convert hierarchical rules to BN format
   - Export to GeNIe, Hugin, or custom XML
   - Enable probabilistic reasoning

8. **Advanced Features**
   - Contradiction detection between rules
   - Temporal analysis (how rules evolved 2010→2025)
   - Collaborative rule refinement

---

## FILES DELIVERED IN THIS PACKAGE

1. ✅ `migrations/001_add_hierarchy_fields.sql` - Database schema
2. ✅ `migrations/002_update_evidence_table.sql` - Evidence enhancements
3. ✅ `prompts/7_panel_extraction_v16_hierarchical.txt` - Enhanced extraction prompt
4. ✅ `meta_review.py` - Aggregation module
5. ✅ `app/routes_papers.py` - Paper analysis routes
6. ✅ `DEPLOYMENT_GUIDE_v16.0.md` - This guide
7. ✅ `test_meta_review.py` - Unit tests (embedded in guide)

---

**Estimated Total Implementation Time**: 16 hours  
**Estimated Deployment Time**: 2-4 hours  
**Next Phase Start**: After 2 weeks production monitoring

**Version**: Article Eater v15.8.1 → v16.0  
**Package Date**: November 8, 2025  
**Status**: READY FOR DEPLOYMENT