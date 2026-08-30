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
