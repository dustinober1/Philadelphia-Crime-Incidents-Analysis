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

    def check_outliers(self, threshold: float = 1.5) -> pd.DataFrame:
        """
        Identifies outliers in numerical columns using the IQR method.

        Args:
            threshold (float): IQR multiplier for outlier detection. Defaults to 1.5.

        Returns:
            pd.DataFrame: Summary of outliers with columns ['column', 'count', 'min_outlier', 'max_outlier'].
        """
        numeric_cols = self.df.select_dtypes(include=["number"])
        outlier_summary = []

        for col in numeric_cols.columns:
            q1 = numeric_cols[col].quantile(0.25)
            q3 = numeric_cols[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - (threshold * iqr)
            upper_bound = q3 + (threshold * iqr)

            outliers = numeric_cols[
                (numeric_cols[col] < lower_bound) | (numeric_cols[col] > upper_bound)
            ][col]

            if not outliers.empty:
                outlier_summary.append(
                    {
                        "column": col,
                        "count": len(outliers),
                        "min_outlier": outliers.min(),
                        "max_outlier": outliers.max(),
                    }
                )

        if not outlier_summary:
            return pd.DataFrame(
                columns=["column", "count", "min_outlier", "max_outlier"]
            )

        return pd.DataFrame(outlier_summary)

    def check_categorical_breakdown(self, top_n: int = 5) -> dict:
        """
        Returns value counts for categorical columns.

        Args:
            top_n (int): Number of top categories to return. Defaults to 5.

        Returns:
            dict: Dictionary where keys are column names and values are dictionaries of value counts.
        """
        cat_cols = self.df.select_dtypes(include=["object", "category"])
        breakdown = {}
        for col in cat_cols.columns:
            breakdown[col] = self.df[col].value_counts().head(top_n).to_dict()
        return breakdown

    def check_correlations(self) -> pd.DataFrame:
        """
        Calculates the correlation matrix for numerical columns.

        Returns:
            pd.DataFrame: Correlation matrix.
        """
        numeric_cols = self.df.select_dtypes(include=["number"])
        if numeric_cols.empty:
            return pd.DataFrame()
        return numeric_cols.corr()

    def analyze_time_series(self, date_col: str, freq: str = "M") -> pd.DataFrame:
        """
        Aggregates data by time frequency.

        Args:
            date_col (str): Name of the datetime column.
            freq (str): Frequency string (e.g., 'D', 'W', 'M', 'Y'). Defaults to 'M'.

        Returns:
            pd.DataFrame: DataFrame with time index and counts.

        Raises:
            ValueError: If date_col does not exist or cannot be converted to datetime.
        """
        if date_col not in self.df.columns:
            raise ValueError(f"Column '{date_col}' not found in DataFrame.")

        # Ensure datetime type
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col])
            except Exception as e:
                raise ValueError(
                    f"Could not convert '{date_col}' to datetime: {e}"
                ) from e

        # Set index and resample
        # using size() to count occurrences in each period
        return self.df.set_index(date_col).resample(freq).size().to_frame(name="count")
