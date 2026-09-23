-- Run from the deployed app's service-principal connection so it owns the schema.
-- Gold remains the source of analytical amounts and scores; this table stores actions.
CREATE SCHEMA IF NOT EXISTS cockpit;

CREATE TABLE IF NOT EXISTS cockpit.contract_actions (
    contract_id TEXT PRIMARY KEY,
    source_snapshot_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'needs_review'
        CHECK (status IN ('needs_review', 'in_progress', 'reviewed', 'closed')),
    assigned_to TEXT,
    next_action TEXT,
    notes TEXT,
    last_reviewed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS contract_actions_status_idx
    ON cockpit.contract_actions (status, updated_at DESC);
