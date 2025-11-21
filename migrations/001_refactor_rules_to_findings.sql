-- ============================================================================
-- Migration 001: Refactor 'rules' to 'findings'
-- Article Eater v17.0 (Dual-Hierarchy)
-- This is a DESTRUCTIVE migration.
-- It removes the v16 'mechanism' columns to prepare for the new model.
-- ============================================================================

-- 1. Rename the table from 'rules' to 'findings'
ALTER TABLE rules RENAME TO findings;

-- 2. Rename columns
ALTER TABLE findings RENAME COLUMN rule_level TO finding_level;
ALTER TABLE findings RENAME COLUMN parent_rule_id TO parent_finding_id;

-- 3. (Optional but Recommended) Create a temporary backup of mechanism data
--    This data will be migrated to the new tables by a Python script.
CREATE TABLE _temp_v16_mechanism_backup AS
SELECT 
    id AS finding_id, 
    mechanism, 
    mechanism_description, 
    theoretical_framework, 
    framework_references
FROM findings
WHERE mechanism IS NOT NULL OR theoretical_framework IS NOT NULL;

-- 4. Drop the conflated mechanism columns (DESTRUCTIVE)
--    These columns are moving to the new 'mechanisms' and 'links' tables.
ALTER TABLE findings DROP COLUMN mechanism;
ALTER TABLE findings DROP COLUMN mechanism_description;
ALTER TABLE findings DROP COLUMN theoretical_framework;
ALTER TABLE findings DROP COLUMN framework_references;

-- 5. Update indexes
DROP INDEX idx_rules_level;
DROP INDEX idx_rules_parent;
DROP INDEX idx_rules_measure;
DROP INDEX idx_rules_framework;
CREATE INDEX idx_findings_level ON findings(finding_level);
CREATE INDEX idx_findings_parent ON findings(parent_finding_id);
CREATE INDEX idx_findings_measure ON findings(operational_measure);

-- 6. Update v16 constraints (if they exist)
ALTER TABLE findings DROP CONSTRAINT check_micro_has_measure;
ALTER TABLE findings ADD CONSTRAINT check_micro_has_measure
  CHECK (finding_level != 'micro' OR operational_measure IS NOT NULL);

PRAGMA foreign_keys=off; -- SQLite specific
-- Recreate table to drop columns if 'DROP COLUMN' is not supported
CREATE TABLE findings_new (
    id INTEGER PRIMARY KEY,
    finding_level VARCHAR(10),
    parent_finding_id INTEGER REFERENCES findings(id),
    consequent VARCHAR(255),
    antecedents TEXT,
    weight REAL,
    operational_measure VARCHAR(100),
    measure_type VARCHAR(50),
    measure_direction VARCHAR(20),
    construct_measured VARCHAR(100),
    p_value REAL,
    effect_size REAL,
    effect_size_type VARCHAR(20),
    sample_size INTEGER,
    statistical_test VARCHAR(100),
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    confidence_triangulation REAL,
    confidence_effect_strength REAL,
    confidence_sample_size REAL,
    confidence_consistency REAL,
    num_child_rules INTEGER DEFAULT 0,
    operational_measures_used TEXT,
    total_sample_size INTEGER,
    CONSTRAINT check_micro_has_measure CHECK (finding_level != 'micro' OR operational_measure IS NOT NULL)
);

INSERT INTO findings_new (id, finding_level, parent_finding_id, consequent, antecedents, weight, operational_measure, measure_type, measure_direction, construct_measured, p_value, effect_size, effect_size_type, sample_size, statistical_test, confidence_interval_lower, confidence_interval_upper, confidence_triangulation, confidence_effect_strength, confidence_sample_size, confidence_consistency, num_child_rules, operational_measures_used, total_sample_size)
SELECT id, finding_level, parent_finding_id, consequent, antecedents, weight, operational_measure, measure_type, measure_direction, construct_measured, p_value, effect_size, effect_size_type, sample_size, statistical_test, confidence_interval_lower, confidence_interval_upper, confidence_triangulation, confidence_effect_strength, confidence_sample_size, confidence_consistency, num_child_rules, operational_measures_used, total_sample_size
FROM findings;

DROP TABLE findings;
ALTER TABLE findings_new RENAME TO findings;

CREATE INDEX idx_findings_level ON findings(finding_level);
CREATE INDEX idx_findings_parent ON findings(parent_finding_id);
CREATE INDEX idx_findings_measure ON findings(operational_measure);
CREATE INDEX idx_findings_construct ON findings(construct_measured);

PRAGMA foreign_keys=on; -- SQLite specific