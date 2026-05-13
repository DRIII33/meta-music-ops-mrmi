import os

# Define the base directory (already established)
BASE_DIR = 'meta-music-ops-mrmi'

# Define the content for the config.py file
config_content = """
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
DIM_METADATA_ANOMALIES_CSV = 'data/dim_metadata_anomalies.csv'

# SQL File Paths
SQL_DDL_PATH = 'sql/ddl/create_tables.sql'
SQL_TRANSFORMATIONS_PATH = 'sql/transformations/conflict_resolution.sql'
"""

# Define the path for config.py
config_dir = os.path.join(BASE_DIR, 'src', 'processing')
os.makedirs(config_dir, exist_ok=True) # Ensure directory exists
config_path = os.path.join(config_dir, 'config.py')

print(f"Creating {config_path}...")

# Write the content to the config.py file
with open(config_path, 'w') as f:
    f.write(config_content)

print("config.py created successfully with project constants.")
