-- v18.3 Confidence & Contradictions (idempotent)
ALTER TABLE rules ADD COLUMN IF NOT EXISTS triangulation_score NUMERIC;
ALTER TABLE rules ADD COLUMN IF NOT EXISTS contradiction_count INT DEFAULT 0;