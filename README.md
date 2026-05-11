# Meta Music Operations & Rights Metadata Integrity (MRMI) System

## Executive Summary

This repository presents the **Meta Music Operations & Rights Metadata Integrity (MRMI) System**, a production-oriented portfolio project designed to demonstrate advanced data engineering, analytics engineering, and BigQuery workflow design skills. It simulates a critical infrastructure component for Meta's "Creative Audio" division, enabling automated rights management, metadata governance, and operational analytics for the rapidly expanding volume of music assets in Metaverse (AR/VR/Reality Labs) environments.

The MRMI system addresses the challenge of high-volume DDEX ingestion, ensuring metadata integrity, automated compliance, and efficient rights management at Meta-scale. It incorporates synthetic data generation to simulate realistic scenarios, including metadata anomalies, SLA breaches, and ISRC conflicts, providing a robust platform for testing and operational insights.

## Data Entity Relationship Overview

The MRMI system is built around three core BigQuery tables:

*   **`dim_music_catalog` (Asset Master):** Contains the "ground truth" for all music assets.
    *   **Key Fields:** `track_id` (PK), `isrc`, `title`, `artist_id`, `supplier_id`, `is_spatial_ready`, `ddex_version`, `license_expiry`.

*   **`fct_ingestion_log` (Operational Health):** Tracks the lifecycle and status of asset ingestion.
    *   **Key Fields:** `ingestion_id` (PK), `track_id` (FK), `supplier_id`, `status` (Success/Fail/Conflict), `latency_seconds`, `sla_breach_flag`, `timestamp`.

*   **`dim_metadata_anomalies` (Quality Control):** Captures details of detected metadata issues.
    *   **Key Fields:** `issue_id`, `track_id`, `issue_code` (MISSING_ISRC, DUPLICATE_ENTRY, LICENSE_EXPIRED), `severity` (P0-P3), `detected_timestamp`.

## Operational Highlights

The MRMI system incorporates several advanced operational features crucial for managing a modern music catalog:

*   **DDEX ERN 4.3 Integration:** Supports rich rights-assignment metadata and multi-territory licensing logic, essential for the "Horizon" ecosystem. This includes specific validation for spatial audio readiness against `ERN 4.3` standards.
*   **ISRC De-duplication & Conflict Resolution:** Implements sophisticated BigQuery SQL logic using window functions to resolve ownership conflicts (e.g., duplicate ISRCs), prioritizing the `primary_rights_holder` based on `supplier_trust_score` and `license_expiry`.
*   **Supplier SLA Monitoring:** Provides real-time operational health insights through an SLA breach report, identifying suppliers with high ingestion failure rates or excessive latency.
*   **Zero-Trust Metadata & AI Attribution:** Designed to support advanced concepts like quarantining assets with inconsistent ISRC values and tracking AI-assisted vs. human-authored stems for legal compliance and royalty attribution.

## Getting Started

This section outlines the steps to set up and run the MRMI system components.

### 1. Project Setup

First, ensure the project directory structure is in place. This is typically created by a setup script.

```bash
# Example of creating the base directory (already executed in the project setup phase)
# mkdir -p meta-music-ops-mrmi/src/data_gen
# ... and other directories
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r meta-music-ops-mrmi/requirements.txt
```

### 3. Generate Synthetic Data

The `generator.py` script creates the synthetic `dim_suppliers.csv`, `dim_music_catalog.csv`, and `fct_ingestion_log.csv` files. These files are saved in the `data/` directory.

```python
# From the project root, execute the data generator
import sys
sys.path.insert(0, 'meta-music-ops-mrmi/src/data_gen')
from generator import MRMIDataGenerator

generator = MRMIDataGenerator()
suppliers_df, catalog_df, ingestion_logs_df = generator.generate_all_datasets()
print("Synthetic data generated and saved to meta-music-ops-mrmi/data/")
```

### 4. Deploy BigQuery DDL

Before loading data, deploy the BigQuery Data Definition Language (DDL) to create the necessary tables in your BigQuery project (`driiiportfolio.meta_music`).

```bash
# You can view the DDL at:
# cat meta-music-ops-mrmi/sql/ddl/create_tables.sql

# Manually execute the SQL in BigQuery Console or using bq command-line tool:
# bq query --use_legacy_sql=false #    --project_id=driiiportfolio #    "$(cat meta-music-ops-mrmi/sql/ddl/create_tables.sql)"
```

### 5. Load Data to BigQuery

Manually load the generated CSV files from `meta-music-ops-mrmi/data/` into their respective BigQuery tables (`dim_suppliers`, `dim_music_catalog`, `fct_ingestion_log`). Use 'Auto-detect' schema or refer to `create_tables.sql` for types. Ensure 'Header row' is checked.

### 6. Deploy BigQuery Views

Deploy the transformation views for rights conflict resolution, SLA reporting, and spatial audio auditing.

```bash
# You can view the view definitions at:
# cat meta-music-ops-mrmi/sql/transformations/conflict_resolution.sql

# Manually execute the SQL in BigQuery Console or using bq command-line tool:
# bq query --use_legacy_sql=false #    --project_id=driiiportfolio #    "$(cat meta-music-ops-mrmi/sql/transformations/conflict_resolution.sql)"
```

### 7. Run Data Integrity Tests

Execute the `pytest` suite to validate the integrity and schema of the generated data against defined expectations.

```bash
# From the project root:
pytest meta-music-ops-mrmi/tests/test_data_integrity.py -v
```

### 8. Explore Analysis Notebook

Open the generated Jupyter notebook for exploratory data analysis and visualizations.

```bash
# Navigate to:
# meta-music-ops-mrmi/notebooks/01_exploratory_ops_analysis.ipynb
```

---

_This README.md was programmatically generated as part of the Meta Music Operations & Rights Metadata Integrity (MRMI) System project._
