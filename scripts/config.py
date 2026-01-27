from pathlib import Path
import seaborn as sns

# =============================================================================
# Paths
# =============================================================================
# Root directory based on this file's location
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = (
    DATA_DIR / "raw"
)  # Conceptually raw, though we might start with the parquet file in data/
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# The main input file path
# Note: Based on project state, the file is currently at data/crime_incidents_combined.parquet
INPUT_FILE_PATH = DATA_DIR / "crime_incidents_combined.parquet"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
for path in [PROCESSED_DATA_DIR, FIGURES_DIR, TABLES_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Coordinate Reference Systems (CRS)
# =============================================================================
CRS_LATLON = "EPSG:4326"  # Standard Lat/Lon
CRS_PHILLY = "EPSG:2272"  # PA South State Plane (ft) - Projected for Philly


# =============================================================================
# Visual Settings
# =============================================================================
# Color palettes
PALETTE_CATEGORICAL = sns.color_palette("deep")
PALETTE_SEQUENTIAL = sns.color_palette("viridis")
PALETTE_DIVERGING = sns.color_palette("coolwarm")

# Plot sizing standard (width, height) in inches
FIG_SIZE_FULL = (12, 8)
FIG_SIZE_HALF = (8, 6)


# =============================================================================
# Column Mappings & Constants
# =============================================================================
# Standard column names to ensure consistency across analysis
COL_ID = "cartodb_id"
COL_DATE = "dispatch_date_time"
COL_DISTRICT = "dc_dist"
COL_PSA = "psa"
COL_UCR_GENERAL = "ucr_general"
COL_TEXT_GENERAL = "text_general_code"
COL_BLOCK = "location_block"
COL_LAT = "lat"
COL_LON = "lng"
# Note: 'coordinates' in original might need parsing if it's a string,
# typically we want lat/lon geometry.

# UCR Codes (General)
UCR_VIOLENT = [100, 200, 300, 400]  # Example placeholders, to be refined
UCR_PROPERTY = [500, 600, 700]  # Example placeholders
