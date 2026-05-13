import os
import pandas as pd
import numpy as np
import uuid
import random
from datetime import datetime, timedelta
import importlib # Import importlib for module reloading

# Import constants from the generated config.py
# We'll need to add the project's root to the Python path temporarily
import sys
# Assuming this script is run from the root of the Colab environment
sys.path.insert(0, os.path.abspath('meta-music-ops-mrmi/src/processing'))

try:
    import config
    importlib.reload(config) # Force reload to ensure latest config is used
except ModuleNotFoundError:
    print("Error: config.py not found. Ensure it was generated correctly.")
    # Fallback to hardcoded values for demonstration if config fails
    class ConfigFallback:
        TOTAL_TRACKS = 35000
        TOTAL_LOGS = 45000
        SUPPLIER_COUNT = 500
        METADATA_ERROR_RATE = 0.05
        DIM_SUPPLIERS_CSV = 'data/dim_suppliers.csv'
        DIM_MUSIC_CATALOG_CSV = 'data/dim_music_catalog.csv'
        FCT_INGESTION_LOG_CSV = 'data/fct_ingestion_log.csv'
        DIM_METADATA_ANOMALIES_CSV = 'data/dim_metadata_anomalies.csv'
    config = ConfigFallback()


# Define the base directory (already established)
BASE_DIR = 'meta-music-ops-mrmi'

class MRMIDataGenerator:
    def __init__(self):
        np.random.seed(42)
        random.seed(42)
        self.total_tracks = config.TOTAL_TRACKS
        self.total_logs = config.TOTAL_LOGS
        self.supplier_count = config.SUPPLIER_COUNT
        self.metadata_error_rate = config.METADATA_ERROR_RATE

    def generate_suppliers(self):
        print("Generating dim_suppliers...")
        suppliers_df = pd.DataFrame({
            'supplier_id': [f"SUPP_{i:04d}" for i in range(self.supplier_count)],
            'supplier_name': [f"Label_Group_{i}" for i in range(self.supplier_count)],
            'trust_score': np.random.uniform(0.6, 1.0, self.supplier_count).round(2),
            'region': np.random.choice(['US', 'EMEA', 'APAC', 'LATAM'], self.supplier_count)
        })
        return suppliers_df

    def generate_music_catalog(self, suppliers_df):
        print("Generating dim_music_catalog...")
        # Ensure we have enough supplier_ids for random choice
        if suppliers_df.empty:
            raise ValueError("Suppliers DataFrame is empty. Cannot generate catalog.")

        catalog_df = pd.DataFrame({
            'track_id': [str(uuid.uuid4())[:18] for _ in range(self.total_tracks)],
            'isrc': [f"US-MT1-26-{i:05d}" for i in range(self.total_tracks)],
            'title': [f"Track_Alpha_{i}" for i in range(self.total_tracks)],
            'artist_id': [f"ART_{np.random.randint(1000, 5000)}" for _ in range(self.total_tracks)],
            'supplier_id': np.random.choice(suppliers_df['supplier_id'].values, self.total_tracks),
            'is_spatial_ready': np.random.choice([True, False], self.total_tracks, p=[0.3, 0.7]),
            'ddex_version': np.random.choice(['ERN 3.8', 'ERN 4.2', 'ERN 4.3'], self.total_tracks),
            'license_expiry': [datetime.now() + timedelta(days=np.random.randint(-100, 1000)) for _ in range(self.total_tracks)]
        })

        # Inject some duplicate ISRCs to simulate conflicts for testing
        num_duplicates = int(self.total_tracks * 0.01) # 1% duplicates
        duplicate_indices = np.random.choice(catalog_df.index, num_duplicates, replace=False)
        if num_duplicates > 0:
            # Take existing ISRCs and assign them to different track_ids/suppliers
            isrcs_to_duplicate = catalog_df.loc[np.random.choice(catalog_df.index, num_duplicates), 'isrc'].values
            catalog_df.loc[duplicate_indices, 'isrc'] = isrcs_to_duplicate
            catalog_df.loc[duplicate_indices, 'supplier_id'] = np.random.choice(suppliers_df['supplier_id'].values, num_duplicates)
            catalog_df.loc[duplicate_indices, 'track_id'] = [str(uuid.uuid4())[:18] for _ in range(num_duplicates)] # New track_ids for duplicates

        return catalog_df

    def generate_ingestion_logs(self, catalog_df, suppliers_df):
        print("Generating fct_ingestion_log...")
        if catalog_df.empty:            raise ValueError("Catalog DataFrame is empty. Cannot generate ingestion logs.")

        # Define probabilities for status based on METADATA_ERROR_RATE
        # Aim for METADATA_ERROR_RATE of 'FAIL' and the rest split between 'SUCCESS' and 'CONFLICT'
        p_fail = self.metadata_error_rate
        p_conflict = 0.05 # Keep a small fixed rate for conflicts
        p_success = 1.0 - p_fail - p_conflict

        if p_success < 0:
            # Adjust if p_fail + p_conflict exceeds 1, prioritizing fail and conflict
            p_success = 0
            p_conflict = 1 - p_fail
            if p_conflict < 0: # Should not happen if p_fail is realistic
                p_fail = 1
                p_conflict = 0

        statuses = np.random.choice(['SUCCESS', 'FAIL', 'CONFLICT'], self.total_logs, p=[p_success, p_fail, p_conflict])
        print(f"DEBUG: Probabilities used for statuses: p_success={p_success:.2f}, p_fail={p_fail:.2f}, p_conflict={p_conflict:.2f}")

        ingestion_logs_df = pd.DataFrame({
            'ingestion_id': [f"INGEST_{i:06d}" for i in range(self.total_logs)],
            'track_id': np.random.choice(catalog_df['track_id'].values, self.total_logs),
            'supplier_id': np.random.choice(suppliers_df['supplier_id'].values, self.total_logs),
            'timestamp': [datetime.now() - timedelta(minutes=np.random.randint(0, 100000)) for _ in range(self.total_logs)],
            'status': statuses,
            'latency_seconds': np.random.gamma(shape=2, scale=10, size=self.total_logs).round(2)
        })

        # Removed redundant anomaly injection that was causing inflated failure rates.

        # Simulate SLA breaches based on latency
        sla_breach_mask = ingestion_logs_df['latency_seconds'] > 30 # Example: latency over 30s is a breach
        ingestion_logs_df['sla_breach_flag'] = sla_breach_mask.astype(bool)

        return ingestion_logs_df

    def generate_metadata_anomalies(self, catalog_df):
        print("Generating dim_metadata_anomalies...")
        # Identify Anomalies (Spatial Audio Readiness Discrepancies)
        # Target: Tracks marked ready for spatial but using legacy DDEX versions
        discrepancy_mask = (
            (catalog_df['is_spatial_ready'] == True) &
            (catalog_df['ddex_version'] != 'ERN 4.3')
        )

        anomalies_raw = catalog_df[discrepancy_mask].copy()

        if anomalies_raw.empty:
            print("No spatial audio discrepancies found.")
            return pd.DataFrame() # Return empty DataFrame if no anomalies

        # Apply Severity Logic (P0-P2)
        # ERN 3.8 = High Risk (P0) due to lack of spatial schema support
        # ERN 4.2 = Medium Risk (P1) due to incomplete immersive metadata blocks
        def map_severity(version):
            if version == 'ERN 3.8':
                return 'P0 - HIGH'
            elif version == 'ERN 4.2':
                return 'P1 - MEDIUM'
            else:
                return 'P2 - LOW' # Default to low if other versions are present and not explicitly P0/P1

        anomalies_df = pd.DataFrame({
            'issue_id': [f"ISS_QC_{uuid.uuid4().hex[:8].upper()}" for _ in range(len(anomalies_raw))],
            'track_id': anomalies_raw['track_id'].values,
            'issue_code': 'SPATIAL_VERSION_MISMATCH',
            'severity': anomalies_raw['ddex_version'].apply(map_severity),
            'detected_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"Generated {len(anomalies_df)} metadata anomalies.")
        return anomalies_df


    def generate_all_datasets(self):
        print("Initiating Music Rights Data Generation...")

        suppliers_df = self.generate_suppliers()
        catalog_df = self.generate_music_catalog(suppliers_df)
        ingestion_logs_df = self.generate_ingestion_logs(catalog_df, suppliers_df)
        dim_metadata_anomalies_df = self.generate_metadata_anomalies(catalog_df) # Generate anomalies here

        # Define save paths
        data_dir = os.path.join(BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Explicitly remove old CSVs to ensure fresh data
        for filename in [config.DIM_SUPPLIERS_CSV, config.DIM_MUSIC_CATALOG_CSV, config.FCT_INGESTION_LOG_CSV, config.DIM_METADATA_ANOMALIES_CSV]:
            file_path = os.path.join(data_dir, os.path.basename(filename))
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed existing file: {file_path}")

        # Save to CSV using paths from config
        suppliers_df.to_csv(os.path.join(data_dir, os.path.basename(config.DIM_SUPPLIERS_CSV)), index=False)
        catalog_df.to_csv(os.path.join(data_dir, os.path.basename(config.DIM_MUSIC_CATALOG_CSV)), index=False)
        ingestion_logs_df.to_csv(os.path.join(data_dir, os.path.basename(config.FCT_INGESTION_LOG_CSV)), index=False)
        dim_metadata_anomalies_df.to_csv(os.path.join(data_dir, os.path.basename(config.DIM_METADATA_ANOMALIES_CSV)), index=False) # Save anomalies

        print(f"Success: Generated {len(catalog_df)} Tracks, {len(ingestion_logs_df)} Logs, {len(suppliers_df)} Suppliers, and {len(dim_metadata_anomalies_df)} Metadata Anomalies.")
        print(f"CSV files saved to: {data_dir}/")

        return suppliers_df, catalog_df, ingestion_logs_df, dim_metadata_anomalies_df


# Script execution
if __name__ == '__main__':
    # Create the directory if it doesn't exist
    output_dir = os.path.join(BASE_DIR, 'src', 'data_gen')
    os.makedirs(output_dir, exist_ok=True)

    # Define the path for generator.py
    generator_path = os.path.join(output_dir, 'generator.py')

    # Save this code into generator.py for modularity
    # Note: In a real scenario, this block would be part of the agent's logic for generating files,
    # not directly in the self-generating code. For Colab, we simulate by writing this cell's content.
    # However, for now, we're just executing it to generate the dataframes and CSVs.

    # Instantiate and run the generator
    generator = MRMIDataGenerator()
    suppliers_df, catalog_df, ingestion_logs_df, dim_metadata_anomalies_df = generator.generate_all_datasets()

    # Remove the temporary path modification
    sys.path.pop(0)

    # Display head of generated dataframes as a check
    print("\n--- Sample of dim_suppliers ---")
    print(suppliers_df.head())
    print("\n--- Sample of dim_music_catalog ---")
    print(catalog_df.head())
    print("\n--- Sample of fct_ingestion_log ---")
    print(ingestion_logs_df.head())
    print("\n--- Sample of dim_metadata_anomalies ---")
    print(dim_metadata_anomalies_df.head())
