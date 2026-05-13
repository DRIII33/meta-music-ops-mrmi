-- View: v_rights_conflict_resolution
-- Logic: If multiple suppliers provide the same ISRC, prioritize by Supplier Trust Score.
-- This view identifies the 'master' record for each ISRC based on trust score and license expiry.
CREATE OR REPLACE VIEW `driiiportfolio.meta_music.v_rights_conflict_resolution` AS
WITH Track_Rankings AS (
    SELECT
        c.isrc,
        c.track_id,
        c.supplier_id,
        s.trust_score,
        c.ddex_version,
        c.license_expiry,
        ROW_NUMBER() OVER(
            PARTITION BY c.isrc
            ORDER BY s.trust_score DESC, c.license_expiry DESC
        ) as master_record_rank
    FROM `driiiportfolio.meta_music.dim_music_catalog` c
    JOIN `driiiportfolio.meta_music.dim_suppliers` s ON c.supplier_id = s.supplier_id
)
SELECT
    isrc,
    track_id,
    supplier_id as primary_rights_holder,
    trust_score,
    ddex_version,
    license_expiry
FROM Track_Rankings
WHERE master_record_rank = 1;

-- View: v_supplier_sla_breach_report
-- Logic: Identify suppliers with average ingestion latency > 30s or failure rates > 10%.
-- This view aggregates ingestion log data to assess supplier performance against SLAs.
CREATE OR REPLACE VIEW `driiiportfolio.meta_music.v_supplier_sla_breach_report` AS
SELECT
    s.supplier_id,
    s.supplier_name,
    s.region,
    COUNT(l.ingestion_id) as total_submissions,
    ROUND(AVG(l.latency_seconds), 2) as avg_latency_seconds,
    COUNTIF(l.status = 'FAIL') as total_failed_submissions,
    SAFE_DIVIDE(
        COUNTIF(l.status = 'FAIL'),
        COUNT(l.ingestion_id)
    ) * 100 as failure_rate_percentage,
    COUNTIF(l.sla_breach_flag) as total_sla_breaches,
    CASE
        WHEN AVG(l.latency_seconds) > 30 THEN 'LATENCY_BREACH'
        WHEN SAFE_DIVIDE(COUNTIF(l.status = 'FAIL'), COUNT(l.ingestion_id)) > 0.10 THEN 'QUALITY_BREACH'
        ELSE 'COMPLIANT'
    END as overall_sla_status
FROM `driiiportfolio.meta_music.fct_ingestion_log` l
JOIN `driiiportfolio.meta_music.dim_music_catalog` c ON l.track_id = c.track_id
JOIN `driiiportfolio.meta_music.dim_suppliers` s ON c.supplier_id = s.supplier_id
GROUP BY 1, 2, 3
HAVING total_submissions > 10
ORDER BY overall_sla_status DESC, failure_rate_percentage DESC;

-- View: v_spatial_audio_readiness_audit
-- Logic: Identify tracks missing spatial metadata despite being flagged for spatial audio.
-- This helps ensure compliance with Meta's 2026 requirement for spatial metadata (ERN 4.3).
CREATE OR REPLACE VIEW `driiiportfolio.meta_music.v_spatial_audio_readiness_audit` AS
/**
 * SANITIZED Optimized Spatial Audio Audit View
 */
SELECT 
    a.issue_id,
    a.severity AS technical_severity,
    c.track_id,
    c.isrc,
    c.title,
    c.ddex_version,
    c.is_spatial_ready,
    a.detected_timestamp
FROM `driiiportfolio.meta_music.dim_metadata_anomalies` a
JOIN `driiiportfolio.meta_music.dim_music_catalog` c 
  -- TRIM and LOWER handle hidden CSV artifacts
  ON TRIM(LOWER(a.track_id)) = TRIM(LOWER(c.track_id))
WHERE a.issue_code = 'SPATIAL_VERSION_MISMATCH'
ORDER BY a.severity ASC;
