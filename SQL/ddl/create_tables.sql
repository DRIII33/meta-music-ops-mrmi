CREATE OR REPLACE TABLE `driiiportfolio.meta_music.dim_suppliers` (
    `supplier_id` STRING,
    `supplier_name` STRING,
    `trust_score` FLOAT64,
    `region` STRING
) ;

CREATE OR REPLACE TABLE `driiiportfolio.meta_music.dim_music_catalog` (
    `track_id` STRING NOT NULL,
    `isrc` STRING,
    `title` STRING,
    `artist_id` STRING,
    `supplier_id` STRING,
    `is_spatial_ready` BOOL,
    `ddex_version` STRING,
    `license_expiry` TIMESTAMP
) ;

CREATE OR REPLACE TABLE `driiiportfolio.meta_music.fct_ingestion_log` (
    `ingestion_id` STRING NOT NULL,
    `track_id` STRING,
    `supplier_id` STRING,
    `timestamp` TIMESTAMP,
    `status` STRING,
    `latency_seconds` FLOAT64,
    `sla_breach_flag` BOOL
) ;

CREATE OR REPLACE TABLE `driiiportfolio.meta_music.dim_metadata_anomalies` (
    `issue_id` STRING NOT NULL,
    `track_id` STRING,
    `issue_code` STRING,
    `severity` STRING,
    `detected_timestamp` TIMESTAMP
) ;