
import os
from pathlib import Path

# Get the project root directory (assuming this file is in src/config.py)
# src/config.py -> src -> uidai_hackathon -> PROJECT_ROOT (aadhaar_biometric)
# The user seems to have "aadhaar_biometric" as the base download folder.
# And "uidai_hackathon" is the project folder inside it?
# Let's adjust based on where the scripts run.

# If we run from "aadhaar_biometric" folder:
# Current working directory usage is safer for interactive running if clearly defined.
# But `__file__` based resolution is most robust.

SRC_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SRC_DIR.parent.parent # uidai_hackathon -> aadhaar_biometric

# Data Paths
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RAW_DATA_DIR = DATA_DIR / "raw"

RAW_DATA_PATH = RAW_DATA_DIR / "aadhaar_biometric.csv"
ENROLMENT_DATA_PATH = RAW_DATA_DIR / "aadhaar_enrolment.csv"
DEMO_DATA_PATH = RAW_DATA_DIR / "aadhaar_demo_monthly_update.csv"

MASTER_DATA_PATH = PROCESSED_DATA_DIR / "master_biometric.csv"
MASTER_ENROLMENT_PATH = PROCESSED_DATA_DIR / "master_enrolment.csv"
MASTER_DEMO_PATH = PROCESSED_DATA_DIR / "master_demo.csv"

MAPPING_PATH = DATA_DIR / "mappings" / "aadhaar_biometric_state_mapping.csv"

# Output Paths
OUTPUT_DIR = PROJECT_ROOT / "uidai_hackathon" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"
ANOMALY_OUTPUT_PATH = FIGURES_DIR / "anomalies_detected.csv"
CLUSTERING_OUTPUT_PATH = FIGURES_DIR / "district_clusters.csv"
FORECAST_IMG_PATH = FIGURES_DIR / "forecast_holt_winters.png"
CLUSTER_IMG_PATH = FIGURES_DIR / "cluster_scatter.png"

# GeoJSON Paths
GEOJSON_DIR = DATA_DIR / "geojson"

# Ensure directories exist
for path in [PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR, GEOJSON_DIR]:
    os.makedirs(path, exist_ok=True)

# Feature Flags or Constants
RANDOM_SEED = 42
IsoForest_CONTAMINATION = 0.05
