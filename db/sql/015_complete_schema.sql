-- Article Eater v18.4 - Complete Schema
-- This file creates ALL tables required by worker and pdf_ingest components
-- Date: 2025-11-14
-- Version: 18.4.1 (schema completion fix)

-- ===== PROCESSING QUEUE (CRITICAL FOR WORKER) =====

CREATE TABLE IF NOT EXISTS processing_queue (
    job_id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL CHECK(job_type IN ('L0_harvest','L1_cluster','L2_extract','L3_synthesize','L4_expand')),
    params TEXT,  -- JSON string
    status TEXT NOT NULL CHECK(status IN ('pending','running','complete','failed')),
    priority INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_queue_status_priority 
ON processing_queue(status, priority DESC, created_at ASC)
WHERE status = 'pending';

COMMENT ON TABLE processing_queue IS 'Job queue for L0-L5 processing pipeline';

-- ===== ARTICLES (REQUIRED BY PDF_INGEST) =====

CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    doi TEXT UNIQUE,
    corpus_id TEXT UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,  -- JSON array of author names
    venue TEXT,
    year INTEGER,
    abstract TEXT,
    full_text TEXT,  -- Extracted from PDF
    sections TEXT,  -- JSON: {abstract, methods, results, discussion}
    text_length INTEGER,
    is_open_access BOOLEAN DEFAULT 0,
    citation_count INTEGER DEFAULT 0,
    url_pdf TEXT,
    ingested_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_articles_doi ON articles(doi) WHERE doi IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_articles_corpus_id ON articles(corpus_id) WHERE corpus_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_articles_year ON articles(year) WHERE year IS NOT NULL;

-- Note: Full-text search on articles.title
-- For FTS5, create separate virtual table if needed

-- ===== FINDINGS (REQUIRED BY WORKER) =====

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_level TEXT NOT NULL CHECK(finding_level IN ('micro','meso','macro')),
    consequent TEXT NOT NULL,  -- Outcome variable
    antecedents TEXT,  -- JSON array of predictor variables
    operational_measure TEXT,
    measure_type TEXT,  -- physiological, psychological, behavioral, neural
    measure_direction TEXT,  -- increase, decrease, u-shaped
    p_value REAL,
    effect_size REAL,
    sample_size INTEGER,
    confidence_interval TEXT,  -- e.g., "[0.23, 0.45]"
    study_design TEXT,  -- RCT, quasi-experimental, observational
    paper_id TEXT,
    job_id TEXT,
    parent_finding_id INTEGER,  -- For meso→micro hierarchy
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_finding_id) REFERENCES findings(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_findings_level ON findings(finding_level);
CREATE INDEX IF NOT EXISTS idx_findings_consequent ON findings(consequent);
CREATE INDEX IF NOT EXISTS idx_findings_paper ON findings(paper_id);

COMMENT ON TABLE findings IS 'Empirical findings extracted from papers (micro/meso/macro hierarchy)';

-- ===== RULES (REQUIRED BY RULE_FRONTIER) =====

CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    rule TEXT NOT NULL,
    confidence REAL CHECK(confidence BETWEEN 0.0 AND 1.0),
    triangulation_score REAL CHECK(triangulation_score BETWEEN 0.0 AND 1.0),
    contradiction_count INTEGER DEFAULT 0,
    evidence_count INTEGER DEFAULT 0,  -- Number of supporting findings
    job_id TEXT,
    cluster_id TEXT,  -- Which cluster of findings generated this rule
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_rules_confidence ON rules(confidence DESC) WHERE confidence IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_rules_triangulation ON rules(triangulation_score DESC) WHERE triangulation_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_rules_cluster ON rules(cluster_id) WHERE cluster_id IS NOT NULL;

COMMENT ON TABLE rules IS 'Synthesized design rules from multiple findings';

-- ===== RULE EVIDENCE (PROVENANCE TRACKING) =====

CREATE TABLE IF NOT EXISTS rule_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    finding_id INTEGER,
    passage TEXT NOT NULL,  -- Direct quote from paper
    evidence_strength TEXT CHECK(evidence_strength IN ('strong','moderate','weak','speculative')),
    stance TEXT CHECK(stance IN ('supporting','contradicting','neutral')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY (finding_id) REFERENCES findings(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_rule ON rule_evidence(rule_id);
CREATE INDEX IF NOT EXISTS idx_evidence_article ON rule_evidence(article_id);

COMMENT ON TABLE rule_evidence IS 'Links rules to source papers with evidence passages';

-- ===== MECHANISMS (V17 FEATURE) =====

CREATE TABLE IF NOT EXISTS mechanisms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    mechanism_level TEXT CHECK(mechanism_level IN ('mechanism','process','theory')),
    parent_mechanism_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (parent_mechanism_id) REFERENCES mechanisms(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_mechanisms_level ON mechanisms(mechanism_level);
CREATE INDEX IF NOT EXISTS idx_mechanisms_parent ON mechanisms(parent_mechanism_id);

COMMENT ON TABLE mechanisms IS 'Explanatory mechanisms (the "why" behind findings)';

-- ===== FINDING-MECHANISM LINKS (V17 FEATURE) =====

CREATE TABLE IF NOT EXISTS finding_mechanism_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_id INTEGER NOT NULL,
    mechanism_id INTEGER NOT NULL,
    paper_id TEXT NOT NULL,
    evidence_strength TEXT CHECK(evidence_strength IN ('strong','moderate','weak','speculative')),
    snippet TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (finding_id) REFERENCES findings(id) ON DELETE CASCADE,
    FOREIGN KEY (mechanism_id) REFERENCES mechanisms(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    UNIQUE(finding_id, mechanism_id, paper_id)
);

CREATE INDEX IF NOT EXISTS idx_fml_finding ON finding_mechanism_links(finding_id);
CREATE INDEX IF NOT EXISTS idx_fml_mechanism ON finding_mechanism_links(mechanism_id);

COMMENT ON TABLE finding_mechanism_links IS 'Links findings to explanatory mechanisms';

-- ===== JOB RESULTS (WORKER OUTPUT STORAGE) =====

CREATE TABLE IF NOT EXISTS job_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    job_type TEXT NOT NULL,
    result_data TEXT NOT NULL,  -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (job_id) REFERENCES processing_queue(job_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_job_results_job ON job_results(job_id);

COMMENT ON TABLE job_results IS 'Stores structured results from completed jobs';

-- ===== PAPER CLUSTERS (FOR L1 TRIAGE) =====

CREATE TABLE IF NOT EXISTS paper_clusters (
    cluster_id TEXT PRIMARY KEY,
    cluster_name TEXT,
    centroid_embedding TEXT,  -- JSON array of floats
    article_count INTEGER DEFAULT 0,
    avg_relevance REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cluster_members (
    cluster_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    relevance_score REAL,
    triage_decision TEXT CHECK(triage_decision IN ('keep','drop','review')),
    triage_rationale TEXT,
    PRIMARY KEY (cluster_id, article_id),
    FOREIGN KEY (cluster_id) REFERENCES paper_clusters(cluster_id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cluster_members_article ON cluster_members(article_id);

COMMENT ON TABLE paper_clusters IS 'Abstract-based paper clustering for L1 triage';
COMMENT ON TABLE cluster_members IS 'Many-to-many: papers in clusters with triage decisions';

-- ===== SAMPLE DATA FOR TESTING =====

-- Insert test user
INSERT OR IGNORE INTO users (user_id, email) VALUES 
    ('test-user-1', 'test@example.com'),
    ('demo-student', 'student@ucsd.edu');

-- Insert sample article
INSERT OR IGNORE INTO articles (article_id, doi, title, authors, year, abstract) VALUES
    ('art-001', '10.1234/test.2024', 'Sample Paper on Biophilic Design', 
     '["Smith, J.", "Johnson, A."]', 2024, 
     'This is a sample abstract about biophilic design and its effects on stress reduction.');

-- Insert sample job
INSERT OR IGNORE INTO processing_queue (job_id, job_type, params, status, priority) VALUES
    ('job-sample-001', 'L1_cluster', '{"article_ids": ["art-001"]}', 'pending', 50);

-- ===== SCHEMA VERSION TRACKING =====

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR REPLACE INTO schema_version (version, description) VALUES
    ('18.4.1', 'Complete schema with all required tables for worker, pdf_ingest, and rule synthesis');

-- ===== VERIFICATION QUERIES =====

-- Run these after applying schema to verify:
-- SELECT COUNT(*) FROM processing_queue;  -- Should return 1 (sample job)
-- SELECT COUNT(*) FROM articles;  -- Should return 1 (sample article)
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;  
--   -- Should show: articles, audit_log, cluster_members, finding_mechanism_links,
--   --              findings, job_results, mechanisms, paper_clusters, processing_queue,
--   --              rule_evidence, rule_frontier, rules, schema_version, user_api_keys, users

-- ===== NOTES =====

-- This schema is designed for:
-- 1. SQLite development (single-file database)
-- 2. Small to medium scale (<10,000 papers, <50,000 findings)
-- 3. Single worker deployment

-- For production at scale (>50 students, >10,000 papers):
-- 1. Migrate to PostgreSQL
-- 2. Add partitioning on large tables (findings, rule_evidence)
-- 3. Add connection pooling
-- 4. Consider read replicas for reporting

-- Foreign key enforcement (SQLite):
PRAGMA foreign_keys = ON;

-- Write-ahead logging for better concurrency (SQLite):
PRAGMA journal_mode = WAL;

-- End of schema
