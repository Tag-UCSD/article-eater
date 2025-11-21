-- v18.3 Rule Frontier
CREATE TABLE IF NOT EXISTS rule_frontier (
  rule_id TEXT PRIMARY KEY REFERENCES rules(rule_id) ON DELETE CASCADE,
  last_cluster_size INT,
  pending_new_articles INT DEFAULT 0,
  last_resynth_ts TIMESTAMPTZ
);