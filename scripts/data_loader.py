import pandas as pd
import pandera as pa
from pandera import errors
from pandera.typing import DataFrame, Series
import scripts.config as config

# Define the schema using Pandera
# We validate against the renamed columns (lat/lng) and standardized types
Schema = pa.DataFrameSchema(
    {
        config.COL_ID: pa.Column(int, required=True, unique=True, title="CartoDB ID"),
        config.COL_DATE: pa.Column(
            pd.DatetimeTZDtype(unit="ns", tz="UTC"),
            required=True,
            title="Dispatch Date/Time",
        ),
        config.COL_DISTRICT: pa.Column(int, required=True, title="District"),
        config.COL_PSA: pa.Column(
            str, nullable=True, required=False, title="Police Service Area"
        ),
        config.COL_UCR_GENERAL: pa.Column(int, required=True, title="UCR General Code"),
        config.COL_TEXT_GENERAL: pa.Column(
            str, nullable=True, required=False, title="Text General Code"
        ),
        config.COL_BLOCK: pa.Column(
            str, nullable=True, required=False, title="Location Block"
        ),
        config.COL_LAT: pa.Column(
            float, nullable=True, required=False, title="Latitude"
        ),
        config.COL_LON: pa.Column(
            float, nullable=True, required=False, title="Longitude"
        ),
    },
    strict=False,  # Allow extra columns like 'hour', 'objectid' etc that we haven't strictly defined yet but might exist
    coerce=True,
)


def load_raw_data(filepath=config.INPUT_FILE_PATH, validate=True):
    """
    Load raw crime incidents data from parquet file.
    Renames point_y -> lat, point_x -> lng to match config.
    Optionally validates schema using Pandera.
    """
    print(f"Loading data from {filepath}...")
    df = pd.read_parquet(filepath, engine="pyarrow")

    # Rename coordinates to match config
    rename_map = {
        "point_y": config.COL_LAT,
        "point_x": config.COL_LON,
        # Ensure other columns match config if needed, but they seem to match based on inspection
        # 'dc_dist': config.COL_DISTRICT (matches)
        # 'dispatch_date_time': config.COL_DATE (matches)
    }
    df = df.rename(columns=rename_map)

    # Ensure types for key columns (parquet usually handles this well, but being explicit helps)
    # Convert categoricals to strings for text columns if they are categories
    if (
        "text_general_code" in df.columns
        and df["text_general_code"].dtype.name == "category"
    ):
        df["text_general_code"] = df["text_general_code"].astype(str)
    if "location_block" in df.columns and df["location_block"].dtype.name == "category":
        df["location_block"] = df["location_block"].astype(str)
    if "psa" in df.columns and df["psa"].dtype.name == "category":
        df["psa"] = df["psa"].astype(str)

    # Handle 'None' or 'nan' strings in categorical conversions if necessary
    # (Not strictly implementing complex cleaning here, just loading)

    if validate:
        print("Validating schema...")
        try:
            # Lazy validation: report all errors
            df = Schema.validate(df, lazy=True)
            print("Schema validation passed.")
        except errors.SchemaErrors as err:
            print("Schema validation failed. Errors found:")
            print(err.failure_cases)

            # We raise so the notebook can catch it or we can decide to return the invalid df
            # For this task, we want to report errors but maybe return the df anyway for inspection?
            # The instructions say "Allow 'lazy' validation (report all errors, don't crash on first)"
            # Schema.validate(lazy=True) raises SchemaErrors containing all errors.
            # We will re-raise so the caller knows, but maybe catch in notebook.
            raise err

    return df
