-- ============================================================================
-- Migration 003: Create 'mechanisms' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- This NEW table stores the "Why" (explanatory hierarchy).
-- ============================================================================

CREATE TABLE mechanisms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- The name of the mechanism
    name VARCHAR(255) NOT NULL UNIQUE, -- e.g., "Perceptual Fluency"
    
    -- A clear definition
    description TEXT,
    
    -- The level in the hierarchy
    mechanism_level VARCHAR(50) NOT NULL, -- 'theory', 'framework', 'mechanism', 'process'
    
    -- Self-referencing key for hierarchy
    parent_mechanism_id INTEGER REFERENCES mechanisms(id) ON DELETE SET NULL,
    
    -- Key citations that *define* this mechanism
    defining_citations TEXT -- JSON array of APA citations
);

CREATE INDEX idx_mechanisms_parent ON mechanisms(parent_mechanism_id);
CREATE INDEX idx_mechanisms_level ON mechanisms(mechanism_level);
CREATE UNIQUE INDEX idx_mechanisms_name ON mechanisms(name);