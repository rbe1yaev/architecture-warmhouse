CREATE DATABASE IF NOT EXISTS telemetry;

CREATE TABLE IF NOT EXISTS telemetry.telemetry (
    device_id String,
    timestamp DateTime64(3),
    metrics String,
    metadata String
) ENGINE = MergeTree()
ORDER BY (device_id, timestamp)
PARTITION BY toYYYYMM(timestamp);

CREATE TABLE IF NOT EXISTS telemetry.telemetry_aggregated (
    device_id String,
    metric_name String,
    interval_start DateTime,
    interval_end DateTime,
    avg_value Float64,
    min_value Float64,
    max_value Float64,
    count UInt64
) ENGINE = SummingMergeTree()
ORDER BY (device_id, metric_name, interval_start);

CREATE TABLE IF NOT EXISTS telemetry.anomalies (
    device_id String,
    metric_name String,
    timestamp DateTime64(3),
    value Float64,
    expected_value Float64,
    deviation Float64,
    anomaly_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (device_id, timestamp);