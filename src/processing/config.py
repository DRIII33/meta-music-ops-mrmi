
# BigQuery Project Configuration
BIGQUERY_PROJECT_ID = 'driiiportfolio'
BIGQUERY_DATASET_NAME = 'meta_music'

# Data Generation Constants
TOTAL_TRACKS = 35000
TOTAL_LOGS = 45000
SUPPLIER_COUNT = 500

# Anomaly Injection
METADATA_ERROR_RATE = 0.05

# File Paths (relative to BASE_DIR from the main script)
DIM_SUPPLIERS_CSV = 'data/dim_suppliers.csv'
DIM_MUSIC_CATALOG_CSV = 'data/dim_music_catalog.csv'
FCT_INGESTION_LOG_CSV = 'data/fct_ingestion_log.csv'

# SQL File Paths
SQL_DDL_PATH = 'sql/ddl/create_tables.sql'
SQL_TRANSFORMATIONS_PATH = 'sql/transformations/conflict_resolution.sql'
