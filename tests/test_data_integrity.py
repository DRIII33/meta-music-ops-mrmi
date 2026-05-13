import os
import pandas as pd
import pytest
import pandas.api.types as pd_types

# Add the processing directory to the Python path to import config
import sys
sys.path.insert(0, os.path.abspath('meta-music-ops-mrmi/src/processing'))

try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found. Ensure it was generated correctly.")
    class ConfigFallback:
        DIM_SUPPLIERS_CSV = 'data/dim_suppliers.csv'
        DIM_MUSIC_CATALOG_CSV = 'data/dim_music_catalog.csv'
        FCT_INGESTION_LOG_CSV = 'data/fct_ingestion_log.csv'
        DIM_METADATA_ANOMALIES_CSV = 'data/dim_metadata_anomalies.csv'
        METADATA_ERROR_RATE = 0.05
        TOTAL_LOGS = 45000
    config = ConfigFallback()

sys.path.pop(0)

BASE_DIR = 'meta-music-ops-mrmi'

# Define paths for the generated CSV files
DIM_SUPPLIERS_PATH = os.path.join(BASE_DIR, config.DIM_SUPPLIERS_CSV)
DIM_MUSIC_CATALOG_PATH = os.path.join(BASE_DIR, config.DIM_MUSIC_CATALOG_CSV)
FCT_INGESTION_LOG_PATH = os.path.join(BASE_DIR, config.FCT_INGESTION_LOG_CSV)
DIM_METADATA_ANOMALIES_PATH = os.path.join(BASE_DIR, config.DIM_METADATA_ANOMALIES_CSV)

# --- Fixtures to load data ---
@pytest.fixture(scope='module')
def dim_suppliers_df():
    return pd.read_csv(DIM_SUPPLIERS_PATH)

@pytest.fixture(scope='module')
def dim_music_catalog_df():
    df = pd.read_csv(DIM_MUSIC_CATALOG_PATH, parse_dates=['license_expiry'])
    return df

@pytest.fixture(scope='module')
def fct_ingestion_log_df():
    df = pd.read_csv(FCT_INGESTION_LOG_PATH, parse_dates=['timestamp'])
    return df

@pytest.fixture(scope='module')
def dim_metadata_anomalies_df():
    df = pd.read_csv(DIM_METADATA_ANOMALIES_PATH, parse_dates=['detected_timestamp'])
    return df

# --- Test Functions (as a multi-line string to be written to file) ---
test_code_content = """
import pandas as pd
import numpy as np
import pytest
import os
import pandas.api.types as pd_types

# Assume config is available or define a minimal fallback for testing environment
try:
    # This path setup is needed if tests are run independently
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'processing')))
    import config
    sys.path.pop(0)
except ModuleNotFoundError:
    class ConfigFallback:
        DIM_SUPPLIERS_CSV = os.path.join('data', 'dim_suppliers.csv')
        DIM_MUSIC_CATALOG_CSV = os.path.join('data', 'dim_music_catalog.csv')
        FCT_INGESTION_LOG_CSV = os.path.join('data', 'fct_ingestion_log.csv')
        DIM_METADATA_ANOMALIES_CSV = os.path.join('data', 'dim_metadata_anomalies.csv')
        METADATA_ERROR_RATE = 0.05
        TOTAL_LOGS = 45000
    config = ConfigFallback()

# Base directory for the project, assuming tests are run from the project root
# or that data files are available relative to the tests directory
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DIM_SUPPLIERS_PATH = os.path.join(_base_dir, config.DIM_SUPPLIERS_CSV)
DIM_MUSIC_CATALOG_PATH = os.path.join(_base_dir, config.DIM_MUSIC_CATALOG_CSV)
FCT_INGESTION_LOG_PATH = os.path.join(_base_dir, config.FCT_INGESTION_LOG_CSV)
DIM_METADATA_ANOMALIES_PATH = os.path.join(_base_dir, config.DIM_METADATA_ANOMALIES_CSV)

@pytest.fixture(scope='module')
def dim_suppliers_df():
    return pd.read_csv(DIM_SUPPLIERS_PATH)

@pytest.fixture(scope='module')
def dim_music_catalog_df():
    df = pd.read_csv(DIM_MUSIC_CATALOG_PATH, parse_dates=['license_expiry'])
    return df

@pytest.fixture(scope='module')
def fct_ingestion_log_df():
    df = pd.read_csv(FCT_INGESTION_LOG_PATH, parse_dates=['timestamp'])
    return df

@pytest.fixture(scope='module')
def dim_metadata_anomalies_df():
    df = pd.read_csv(DIM_METADATA_ANOMALIES_PATH, parse_dates=['detected_timestamp'])
    return df

def test_dim_suppliers_schema(dim_suppliers_df):
    expected_columns = {
        'supplier_id': np.dtype('object'),
        'supplier_name': np.dtype('object'),
        'trust_score': np.dtype('float64'),
        'region': np.dtype('object')
    }
    assert set(dim_suppliers_df.columns) == set(expected_columns.keys())
    for col, expected_type in expected_columns.items():
        if expected_type == np.dtype('object'):
            assert pd_types.is_string_dtype(dim_suppliers_df[col]), f"Column {col} expected string type, got {dim_suppliers_df[col].dtype}"
        else:
            assert dim_suppliers_df[col].dtype == expected_type, f"Column {col} expected {expected_type}, got {dim_suppliers_df[col].dtype}"

def test_dim_suppliers_pk_uniqueness(dim_suppliers_df):
    assert dim_suppliers_df['supplier_id'].is_unique

def test_dim_music_catalog_schema(dim_music_catalog_df):
    expected_columns = {
        'track_id': np.dtype('object'),
        'isrc': np.dtype('object'),
        'title': np.dtype('object'),
        'artist_id': np.dtype('object'),
        'supplier_id': np.dtype('object'),
        'is_spatial_ready': np.dtype('bool'),
        'ddex_version': np.dtype('object'),
        'license_expiry': np.dtype('<M8[ns]')
    }
    assert set(dim_music_catalog_df.columns) == set(expected_columns.keys())
    for col, expected_type in expected_columns.items():
        if expected_type == np.dtype('object'):
            assert pd_types.is_string_dtype(dim_music_catalog_df[col]), f"Column {col} expected string type, got {dim_music_catalog_df[col].dtype}"
        elif expected_type == np.dtype('<M8[ns]'):
            assert pd_types.is_datetime64_any_dtype(dim_music_catalog_df[col]), f"Column {col} expected datetime type, got {dim_music_catalog_df[col].dtype}"
        else:
            assert dim_music_catalog_df[col].dtype == expected_type, f"Column {col} expected {expected_type}, got {dim_music_catalog_df[col].dtype}"

def test_dim_music_catalog_pk_uniqueness(dim_music_catalog_df):
    assert dim_music_catalog_df['track_id'].is_unique

def test_fct_ingestion_log_schema(fct_ingestion_log_df):
    expected_columns = {
        'ingestion_id': np.dtype('object'),
        'track_id': np.dtype('object'),
        'supplier_id': np.dtype('object'),
        'timestamp': np.dtype('<M8[ns]'),
        'status': np.dtype('object'),
        'latency_seconds': np.dtype('float64'),
        'sla_breach_flag': np.dtype('bool')
    }
    assert set(fct_ingestion_log_df.columns) == set(expected_columns.keys())
    for col, expected_type in expected_columns.items():
        if expected_type == np.dtype('object'):
            assert pd_types.is_string_dtype(fct_ingestion_log_df[col]), f"Column {col} expected string type, got {fct_ingestion_log_df[col].dtype}"
        elif expected_type == np.dtype('<M8[ns]'):
            assert pd_types.is_datetime64_any_dtype(fct_ingestion_log_df[col]), f"Column {col} expected datetime type, got {fct_ingestion_log_df[col].dtype}"
        else:
            assert fct_ingestion_log_df[col].dtype == expected_type, f"Column {col} expected {expected_type}, got {fct_ingestion_log_df[col].dtype}"

def test_fct_ingestion_log_pk_uniqueness(fct_ingestion_log_df):
    assert fct_ingestion_log_df['ingestion_id'].is_unique

def test_fct_ingestion_log_fk_track_id(dim_music_catalog_df, fct_ingestion_log_df):
    assert fct_ingestion_log_df['track_id'].isin(dim_music_catalog_df['track_id']).all()

def test_fct_ingestion_log_fk_supplier_id(dim_suppliers_df, fct_ingestion_log_df):
    assert fct_ingestion_log_df['supplier_id'].isin(dim_suppliers_df['supplier_id']).all()

def test_dim_music_catalog_fk_supplier_id(dim_suppliers_df, dim_music_catalog_df):
    assert dim_music_catalog_df['supplier_id'].isin(dim_suppliers_df['supplier_id']).all()

def test_dim_metadata_anomalies_schema(dim_metadata_anomalies_df):
    expected_columns = {
        'issue_id': np.dtype('object'),
        'track_id': np.dtype('object'),
        'issue_code': np.dtype('object'),
        'severity': np.dtype('object'),
        'detected_timestamp': np.dtype('<M8[ns]')
    }
    assert set(dim_metadata_anomalies_df.columns) == set(expected_columns.keys())
    for col, expected_type in expected_columns.items():
        if expected_type == np.dtype('object'):
            assert pd_types.is_string_dtype(dim_metadata_anomalies_df[col]), f"Column {col} expected string type, got {dim_metadata_anomalies_df[col].dtype}"
        elif expected_type == np.dtype('<M8[ns]'):
            assert pd_types.is_datetime64_any_dtype(dim_metadata_anomalies_df[col]), f"Column {col} expected datetime type, got {dim_metadata_anomalies_df[col].dtype}"
        else:
            assert dim_metadata_anomalies_df[col].dtype == expected_type, f"Column {col} expected {expected_type}, got {dim_metadata_anomalies_df[col].dtype}"

def test_dim_metadata_anomalies_pk_uniqueness(dim_metadata_anomalies_df):
    assert dim_metadata_anomalies_df['issue_id'].is_unique

def test_dim_metadata_anomalies_fk_track_id(dim_music_catalog_df, dim_metadata_anomalies_df):
    assert dim_metadata_anomalies_df['track_id'].isin(dim_music_catalog_df['track_id']).all()

def test_critical_columns_not_null(dim_suppliers_df, dim_music_catalog_df, fct_ingestion_log_df, dim_metadata_anomalies_df):
    assert not dim_suppliers_df['supplier_id'].isnull().any()
    assert not dim_music_catalog_df['track_id'].isnull().any()
    assert not fct_ingestion_log_df['ingestion_id'].isnull().any()
    assert not dim_metadata_anomalies_df['issue_id'].isnull().any()
    assert not dim_metadata_anomalies_df['track_id'].isnull().any()

def test_sla_breach_logic(fct_ingestion_log_df):
    recalculated_breach = (fct_ingestion_log_df['latency_seconds'] > 30) # Example: latency over 30s is a breach
    assert (fct_ingestion_log_df['sla_breach_flag'] == recalculated_breach).all()

def test_anomaly_rate_simulation(fct_ingestion_log_df):
    fail_count = fct_ingestion_log_df[fct_ingestion_log_df['status'] == 'FAIL'].shape[0]
    expected_fail_count = config.TOTAL_LOGS * config.METADATA_ERROR_RATE
    # Using a 25% tolerance for the anomaly rate, as it seems to be the intended tolerance.
    assert abs(fail_count - expected_fail_count) / expected_fail_count < 0.25, f"Anomaly rate mismatch: Expected ~{expected_fail_count} FAILs ({(config.METADATA_ERROR_RATE)*100:.1f}%), got {fail_count} FAILs ({fail_count/config.TOTAL_LOGS*100:.1f}%)"
"""

# Define the path for test_data_integrity.py
tests_dir = os.path.join(BASE_DIR, 'tests')
os.makedirs(tests_dir, exist_ok=True) # Ensure directory exists
test_file_path = os.path.join(tests_dir, 'test_data_integrity.py')

print(f"Creating {test_file_path}...")

# Write the content to the test_data_integrity.py file with explicit flush and close
with open(test_file_path, 'w') as f:
    f.write(test_code_content)
    f.flush()
    os.fsync(f.fileno()) # Ensure data is written to disk

print("test_data_integrity.py created successfully.")
