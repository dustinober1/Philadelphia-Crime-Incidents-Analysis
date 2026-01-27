import pandas as pd
from src.utils.config import load_config, PROJECT_ROOT


def load_crime_data(filename: str = "crime_incidents_combined.parquet") -> pd.DataFrame:
    """
    Load the processed crime data from parquet file.

    Args:
        filename (str): Name of the parquet file. Defaults to "crime_incidents_combined.parquet".

    Returns:
        pd.DataFrame: The crime data loaded with pyarrow backend.

    Raises:
        FileNotFoundError: If the data file does not exist.
    """
    config = load_config()
    processed_path = config["data_paths"]["processed_data_path"]
    file_path = PROJECT_ROOT / processed_path / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found at {file_path}. "
            "Please ensure the data processing step has been run."
        )

    try:
        return pd.read_parquet(file_path, engine="pyarrow", dtype_backend="pyarrow")
    except Exception as e:
        raise RuntimeError(f"Failed to load crime data: {e}") from e
