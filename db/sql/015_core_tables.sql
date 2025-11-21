-- Article Eater v18.4.1 - Core Tables
-- Processing queue, articles, findings, rules
-- Date: 2025-11-14

-- ===== PROCESSING QUEUE =====

CREATE TABLE IF NOT EXISTS processing_queue (
    job_id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL CHECK(job_type IN ('L0_harvest', 'L1_cluster', 'L2_extract', 'L3_synthesize', 'L4_expand')),
    params TEXT,  -- JSON string
    status TEXT NOT NULL CHECK(status IN ('pending', 'running', 'complete', 'failed')) DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_queue_pending 
ON processing_queue(status, priority DESC, created_at ASC)
WHERE status = 'pending';

-- ===== ARTICLES =====

CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    doi TEXT,
    corpus_id TEXT,
    title TEXT NOT NULL,
    authors TEXT,  -- JSON array
    year INTEGER,
    venue TEXT,
    abstract TEXT,
    full_text TEXT,
    sections TEXT,  -- JSON object {abstract, methods, results, discussion}
    text_length INTEGER,
    is_open_access BOOLEAN,
    citation_count INTEGER,
    url_pdf TEXT,
    ingested_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_doi 
ON articles(doi) WHERE doi IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_corpus 
ON articles(corpus_id) WHERE corpus_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_articles_year 
ON articles(year) WHERE year IS NOT NULL;

-- ===== FINDINGS =====

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_level TEXT CHECK(finding_level IN ('micro', 'meso', 'macro')),
    consequent TEXT NOT NULL,
    antecedents TEXT,  -- JSON array
    operational_measure TEXT,
    measure_type TEXT,
    measure_direction TEXT,
    p_value REAL,
    effect_size REAL,
    sample_size INTEGER,
    job_id TEXT,
    paper_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_findings_level 
ON findings(finding_level);

CREATE INDEX IF NOT EXISTS idx_findings_job 
ON findings(job_id);

-- ===== RULES =====

CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    rule TEXT NOT NULL,
    confidence REAL,
    triangulation_score REAL CHECK(triangulation_score IS NULL OR (triangulation_score BETWEEN 0 AND 1)),
    contradiction_count INTEGER DEFAULT 0 CHECK(contradiction_count >= 0),
    job_id TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_rules_confidence 
ON rules(triangulation_score DESC);

-- ===== RULE EVIDENCE =====

CREATE TABLE IF NOT EXISTS rule_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    passage TEXT,
    page_number INTEGER,
    stance TEXT CHECK(stance IN ('supporting', 'contradicting', 'neutral')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_rule 
ON rule_evidence(rule_id);

CREATE INDEX IF NOT EXISTS idx_evidence_article 
ON rule_evidence(article_id);

-- ===== INITIAL TEST DATA =====

-- Create test job for smoke testing
INSERT OR IGNORE INTO processing_queue (job_id, job_type, params, status, priority)
VALUES ('test-job-smoke', 'L1_cluster', '{"article_ids": [1, 2, 3]}', 'pending', 100);

-- Test article
INSERT OR IGNORE INTO articles (article_id, title, year)
VALUES ('test-article-1', 'Test Paper for Validation', 2025);
