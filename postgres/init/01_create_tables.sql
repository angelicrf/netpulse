CREATE TABLE IF NOT EXISTS network_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    region VARCHAR(100) NOT NULL,
    pop VARCHAR(100) NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL,
    packet_loss_pct DOUBLE PRECISION NOT NULL,
    status VARCHAR(50) NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_network_metrics_time
    ON network_metrics (timestamp DESC);

CREATE TABLE IF NOT EXISTS root_cause_analyses (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    region VARCHAR(100) NOT NULL,
    pop VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT 'AI Root-Cause Analysis',
    subtitle VARCHAR(300) NOT NULL DEFAULT 'Network anomaly assessment',
    summary TEXT NOT NULL,
    suspected_issue TEXT NOT NULL,
    prediction TEXT,
    workaround TEXT,
    evidence TEXT,
    confidence DOUBLE PRECISION,
    source VARCHAR(120) NOT NULL DEFAULT 'fallback-rule-based',
    model VARCHAR(100) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_root_cause_time
    ON root_cause_analyses (timestamp DESC);
