import pandas as pd


class DataProfiler:
    """
    Encapsulates data profiling logic for quality checks, type inspection,
    and basic statistical analysis.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataProfiler with a pandas DataFrame.

        Args:
            df (pd.DataFrame): The dataset to profile.
        """
        self.df = df

    def get_summary(self) -> dict:
        """
        Returns a high-level summary of the dataset.

        Returns:
            dict: Dictionary containing shape, columns, memory usage,
                  and basic numerical statistics.
        """
        numeric_cols = self.df.select_dtypes(include=["number"])
        stats = {}
        if not numeric_cols.empty:
            # Get min, max, mean for numeric columns
            stats = numeric_cols.describe().loc[["min", "max", "mean"]].to_dict()

        return {
            "shape": self.df.shape,
            "columns": self.df.columns.tolist(),
            "memory_usage": int(self.df.memory_usage(deep=True).sum()),
            "numerical_stats": stats,
        }

    def check_types(self) -> pd.Series:
        """
        Returns the data types of the columns.

        Returns:
            pd.Series: Series containing dtypes of each column.
        """
        return self.df.dtypes

    def check_missing_values(self) -> pd.DataFrame:
        """
        Calculates the count and percentage of missing values per column.

        Returns:
            pd.DataFrame: DataFrame with columns 'missing_count' and 'missing_percentage'.
        """
        missing_count = self.df.isnull().sum()
        missing_percentage = (missing_count / len(self.df)) * 100
        return pd.DataFrame(
            {"missing_count": missing_count, "missing_percentage": missing_percentage}
        )

    def check_duplicates(self) -> int:
        """
        Returns the number of duplicate rows in the dataset.

        Returns:
            int: Count of duplicate rows.
        """
        return self.df.duplicated().sum()
