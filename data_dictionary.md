
## Data Dictionary for MRMI System

This data dictionary provides a detailed overview of the tables within the Music Rights & Metadata Integrity (MRMI) System. It includes schema information derived from both the Python data generation scripts and the BigQuery DDL, ensuring consistency and clarity for each field.

### 1. `dim_suppliers`

This dimension table stores information about the music suppliers or labels involved in the system.

| Column Name   | Data Type (BigQuery) | Description                                                              |
|:--------------|:---------------------|:-------------------------------------------------------------------------|
| `supplier_id` | STRING               | Unique identifier for each music supplier (Primary Key).                 |
| `supplier_name`| STRING               | Human-readable name of the supplier.                                     |
| `trust_score` | FLOAT64              | A numerical score indicating the reliability or trust level of the supplier. |
| `region`      | STRING               | The geographic region where the supplier operates (e.g., US, EMEA, APAC, LATAM). |

### 2. `dim_music_catalog`

This dimension table serves as the asset master, containing the 'ground truth' for all music tracks.

| Column Name        | Data Type (BigQuery) | Description                                                              |
|:-------------------|:---------------------|:-------------------------------------------------------------------------|
| `track_id`         | STRING (NOT NULL)    | Unique identifier for each music track (Primary Key).                  |
| `isrc`             | STRING               | International Standard Recording Code (ISRC) for the track.              |
| `title`            | STRING               | Title of the music track.                                                |
| `artist_id`        | STRING               | Unique identifier for the artist(s) associated with the track.           |
| `supplier_id`      | STRING               | Foreign Key referencing `dim_suppliers.supplier_id`, indicating the supplier of the track. |
| `is_spatial_ready` | BOOL                 | Boolean flag indicating if the track is ready for spatial audio.         |
| `ddex_version`     | STRING               | The DDEX ERN standard version used for the track's metadata (e.g., ERN 3.8, ERN 4.2, ERN 4.3). |
| `license_expiry`   | TIMESTAMP            | The expiration date and time of the track's license.                     |

### 3. `fct_ingestion_log`

This fact table tracks the operational health of the asset ingestion pipeline, logging each submission attempt.

| Column Name       | Data Type (BigQuery) | Description                                                              |
|:------------------|:---------------------|:-------------------------------------------------------------------------|
| `ingestion_id`    | STRING (NOT NULL)    | Unique identifier for each ingestion event (Primary Key).                |
| `track_id`        | STRING               | Foreign Key referencing `dim_music_catalog.track_id`, indicating the track being ingested. |
| `supplier_id`     | STRING               | Foreign Key referencing `dim_suppliers.supplier_id`, indicating the supplier making the submission. |
| `timestamp`       | TIMESTAMP            | The date and time when the ingestion event occurred.                     |
| `status`          | STRING               | The outcome of the ingestion event (e.g., 'SUCCESS', 'FAIL', 'CONFLICT'). |
| `latency_seconds` | FLOAT64              | The time taken for the ingestion process in seconds.                     |
| `sla_breach_flag` | BOOL                 | Boolean flag indicating if the ingestion event breached SLA (e.g., due to high latency). |

### 4. `dim_metadata_anomalies`

This dimension table captures details about detected metadata quality issues for triage and remediation.

| Column Name        | Data Type (BigQuery) | Description                                                              |
|:-------------------|:---------------------|:-------------------------------------------------------------------------|
| `issue_id`         | STRING (NOT NULL)    | Unique identifier for each detected anomaly (Primary Key).               |
| `track_id`         | STRING               | Foreign Key referencing `dim_music_catalog.track_id`, indicating the track with the anomaly. |
| `issue_code`       | STRING               | A code categorizing the type of metadata issue (e.g., MISSING_ISRC, DUPLICATE_ENTRY, LICENSE_EXPIRED). |
| `severity`         | STRING               | The severity level of the anomaly (e.g., P0, P1, P2, P3).                |
| `detected_timestamp`| TIMESTAMP            | The date and time when the anomaly was detected.                         |
