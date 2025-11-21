-- Article Eater v18.4 Security Schema
-- Per-user API keys with encryption-at-rest + audit logging
-- Date: 2025-11-14

-- ===== USER API KEYS TABLE =====

CREATE TABLE IF NOT EXISTS user_api_keys (
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,  -- 'openai', 'anthropic', 'google'
    encrypted_key TEXT NOT NULL,  -- Base64-encoded Fernet-encrypted key
    created_at TEXT NOT NULL,  -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,  -- ISO 8601 timestamp
    last_used_at TEXT,  -- ISO 8601 timestamp, updated on each use
    usage_count INTEGER DEFAULT 0,  -- Incremented on each use
    PRIMARY KEY (user_id, provider),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_keys_last_used 
ON user_api_keys(last_used_at);

-- ===== AUDIT LOG TABLE =====

CREATE TABLE IF NOT EXISTS audit_log (
    event_id TEXT PRIMARY KEY,  -- UUID
    timestamp TEXT NOT NULL,  -- ISO 8601 timestamp
    user_id TEXT,  -- NULL for anonymous requests
    method TEXT NOT NULL,  -- GET, POST, PUT, DELETE
    path TEXT NOT NULL,  -- Request path (no query params)
    status_code INTEGER NOT NULL,  -- HTTP status code
    duration_ms REAL,  -- Request duration in milliseconds
    client_ip TEXT,  -- Anonymized IP address (last octet zeroed)
    user_agent TEXT,  -- Truncated to 100 chars
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
ON audit_log(timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_user 
ON audit_log(user_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_path 
ON audit_log(path, timestamp);

-- ===== PROCESSING QUEUE SCHEMA EXTENSION =====
-- Extend existing processing_queue table with additional fields

-- Note: SQLite doesn't support ALTER TABLE ADD COLUMN IF NOT EXISTS
-- Run these only if columns don't exist

-- Add created_at if not exists
-- ALTER TABLE processing_queue ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add started_at if not exists
-- ALTER TABLE processing_queue ADD COLUMN started_at TEXT;

-- Add completed_at if not exists
-- ALTER TABLE processing_queue ADD COLUMN completed_at TEXT;

-- Add error if not exists
-- ALTER TABLE processing_queue ADD COLUMN error TEXT;

-- ===== COMMENTS =====

-- user_api_keys:
--   - user_id: References users table
--   - provider: API provider name (lowercase)
--   - encrypted_key: Never store plaintext keys
--   - created_at: When key was first added
--   - updated_at: When key was last updated (rotation)
--   - last_used_at: When key was last retrieved for use
--   - usage_count: Number of times key has been used

-- audit_log:
--   - event_id: Unique identifier for each request
--   - timestamp: When request occurred
--   - user_id: Who made the request (NULL if anonymous)
--   - method: HTTP verb
--   - path: URL path without query string (no PII)
--   - status_code: Response status
--   - duration_ms: How long request took
--   - client_ip: Anonymized for GDPR/privacy
--   - user_agent: Browser/client info (truncated)

-- ===== INITIAL DATA =====

-- Create test user if not exists
INSERT OR IGNORE INTO users (user_id, email) 
VALUES ('test-user-1', 'test@example.com');

-- ===== SECURITY NOTES =====

-- 1. Never SELECT encrypted_key without immediately decrypting
-- 2. Always mask keys when returning to user (first 10 + last 4 chars)
-- 3. Audit log excludes request bodies (may contain PII)
-- 4. IP addresses anonymized per GDPR Article 32
-- 5. Master key (MASTER_KEY env var) must be 32-byte Fernet key
-- 6. Rotate master key annually; re-encrypt all keys on rotation

-- ===== EXAMPLE QUERIES =====

-- Get user's providers:
-- SELECT provider, created_at, last_used_at, usage_count 
-- FROM user_api_keys 
-- WHERE user_id = ? 
-- ORDER BY provider;

-- Audit trail for user:
-- SELECT timestamp, method, path, status_code, duration_ms
-- FROM audit_log
-- WHERE user_id = ?
-- ORDER BY timestamp DESC
-- LIMIT 100;

-- Most active users (by API key usage):
-- SELECT user_id, SUM(usage_count) as total_uses
-- FROM user_api_keys
-- GROUP BY user_id
-- ORDER BY total_uses DESC
-- LIMIT 10;
