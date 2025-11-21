-- ============================================================================
-- Migration 002: Add 'papers' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- Required for linking findings and mechanisms to provenance.
-- ============================================================================

CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT, -- JSON array
    year INTEGER,
    journal VARCHAR(255),
    abstract TEXT,
    -- Internal reference to the job that ingested this paper
    ingested_by_job_id VARCHAR(255)
);

CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_year ON papers(year);

-- This migration must be run *before* 004, which references it.
-- A data backfill script will be needed to populate this table from
-- existing `findings` provenance and `shortlist.json` files.