-- ============================================================================
-- Migration 004: Create 'finding_mechanism_links' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- This NEW table is the "Bridge" connecting "What" to "Why".
-- ============================================================================

CREATE TABLE finding_mechanism_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign key to the empirical finding
    finding_id INTEGER NOT NULL,
    
    -- Foreign key to the theoretical mechanism
    mechanism_id INTEGER NOT NULL,
    
    -- Foreign key to the *paper* that makes this claim
    paper_id INTEGER NOT NULL,
    
    -- How strongly does the paper claim this link?
    evidence_strength VARCHAR(50) NOT NULL, -- 'strong', 'moderate', 'speculative'
    
    -- The exact quote from the paper proposing this link
    snippet TEXT,

    FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE,
    FOREIGN KEY(mechanism_id) REFERENCES mechanisms(id) ON DELETE CASCADE,
    FOREIGN KEY(paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    
    -- A paper should only link a finding to a mechanism once
    UNIQUE(finding_id, mechanism_id, paper_id)
);

CREATE INDEX idx_links_finding ON finding_mechanism_links(finding_id);
CREATE INDEX idx_links_mechanism ON finding_mechanism_links(mechanism_id);
CREATE INDEX idx_links_paper ON finding_mechanism_links(paper_id);