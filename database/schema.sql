-- Parakh MySQL schema reference.
-- The backend creates these tables automatically via SQLAlchemy on startup
-- (see backend/app/database.py + backend/app/models.py). This file is a
-- human-readable reference of that schema and can also be run directly
-- against a fresh MySQL database if you prefer manual provisioning.

CREATE DATABASE IF NOT EXISTS parakh CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE parakh;

CREATE TABLE IF NOT EXISTS claims (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    original_text     TEXT NOT NULL,
    normalized_claim  TEXT NOT NULL,
    verdict           VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED',   -- VERIFIED | FALSE | MISLEADING | UNVERIFIED
    evidence_strength VARCHAR(16) NOT NULL DEFAULT 'LOW',          -- LOW | MEDIUM | HIGH
    explanation       TEXT NOT NULL,
    category          VARCHAR(64) NOT NULL DEFAULT 'Other',
    input_type        VARCHAR(16) NOT NULL DEFAULT 'text',         -- text | image | url | voice
    source_url        VARCHAR(1024) NULL,
    embedding         JSON NULL,                                   -- semantic vector, list[float]
    check_count       INT NOT NULL DEFAULT 1,
    created_at        DATETIME NOT NULL,
    updated_at        DATETIME NOT NULL,
    INDEX idx_verdict (verdict),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS evidence_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    claim_id     INT NOT NULL,
    source_name  VARCHAR(256) NOT NULL,
    source_url   VARCHAR(1024) NOT NULL,
    snippet      TEXT NOT NULL,
    reliability  VARCHAR(16) NOT NULL DEFAULT 'LOW',                -- HIGH | MEDIUM | LOW
    created_at   DATETIME NOT NULL,
    INDEX idx_claim_id (claim_id),
    CONSTRAINT fk_evidence_claim FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS verification_history (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    claim_id         INT NOT NULL,
    raw_input        TEXT NOT NULL,
    input_type       VARCHAR(16) NOT NULL,
    matched_existing TINYINT(1) NOT NULL DEFAULT 0,
    created_at       DATETIME NOT NULL,
    INDEX idx_claim_id (claim_id),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_history_claim FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
) ENGINE=InnoDB;
