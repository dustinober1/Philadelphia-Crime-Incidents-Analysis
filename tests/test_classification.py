"""Tests for crime classification utilities."""

import pandas as pd
import pytest

from analysis.utils.classification import CRIME_CATEGORY_MAP, classify_crime_category


class TestCrimeCategoryMap:
    """Tests for CRIME_CATEGORY_MAP constant."""

    def test_is_dict(self):
        """CRIME_CATEGORY_MAP is a dictionary."""
        assert isinstance(CRIME_CATEGORY_MAP, dict)

    def test_has_expected_keys(self):
        """CRIME_CATEGORY_MAP has Violent and Property keys."""
        assert "Violent" in CRIME_CATEGORY_MAP
        assert "Property" in CRIME_CATEGORY_MAP

    def test_values_are_sets(self):
        """CRIME_CATEGORY_MAP values are sets of integers."""
        for _category, codes in CRIME_CATEGORY_MAP.items():
            assert isinstance(codes, set)
            for code in codes:
                assert isinstance(code, int)

    def test_violent_codes(self):
        """Violent category contains UCR codes 1-4."""
        assert CRIME_CATEGORY_MAP["Violent"] == {1, 2, 3, 4}

    def test_property_codes(self):
        """Property category contains UCR codes 5-7."""
        assert CRIME_CATEGORY_MAP["Property"] == {5, 6, 7}

    def test_categories_are_mutually_exclusive(self):
        """No overlap between Violent and Property categories."""
        violent = CRIME_CATEGORY_MAP["Violent"]
        property_crimes = CRIME_CATEGORY_MAP["Property"]
        assert violent.isdisjoint(property_crimes)


class TestClassifyCrimeCategory:
    """Tests for classify_crime_category function."""

    def test_violent_crimes_100_band(self):
        """UCR codes in 100 band are classified as Violent."""
        df = pd.DataFrame({"ucr_general": [100, 150, 199]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Violent").all()

    def test_violent_crimes_200_band(self):
        """UCR codes in 200 band are classified as Violent."""
        df = pd.DataFrame({"ucr_general": [200, 250, 299]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Violent").all()

    def test_violent_crimes_300_band(self):
        """UCR codes in 300 band are classified as Violent."""
        df = pd.DataFrame({"ucr_general": [300, 350, 399]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Violent").all()

    def test_violent_crimes_400_band(self):
        """UCR codes in 400 band are classified as Violent."""
        df = pd.DataFrame({"ucr_general": [400, 450, 499]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Violent").all()

    def test_property_crimes_500_band(self):
        """UCR codes in 500 band are classified as Property."""
        df = pd.DataFrame({"ucr_general": [500, 550, 599]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Property").all()

    def test_property_crimes_600_band(self):
        """UCR codes in 600 band are classified as Property."""
        df = pd.DataFrame({"ucr_general": [600, 650, 699]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Property").all()

    def test_property_crimes_700_band(self):
        """UCR codes in 700 band are classified as Property."""
        df = pd.DataFrame({"ucr_general": [700, 750, 799]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Property").all()

    def test_other_crimes(self):
        """UCR codes outside 1-7 bands are classified as Other."""
        df = pd.DataFrame({"ucr_general": [800, 900, 999, 1000]})
        result = classify_crime_category(df)
        assert (result["crime_category"] == "Other").all()

    def test_mixed_ucr_codes(self):
        """Mixed UCR codes are classified correctly."""
        df = pd.DataFrame({"ucr_general": [100, 200, 500, 600, 999]})
        result = classify_crime_category(df)
        expected = ["Violent", "Violent", "Property", "Property", "Other"]
        assert result["crime_category"].tolist() == expected

    def test_expanded_ucr_format(self):
        """Expanded UCR codes (100-9999) use hundred-band classification.

        Note: Only single-digit hundred bands (1-7) are classified as
        Violent or Property. Codes outside this range are 'Other'.
        """
        df = pd.DataFrame({"ucr_general": [600, 2600, 3000, 4150, 7999]})
        result = classify_crime_category(df)
        # 600 -> Property (6), 2600 -> Other (26, not in 1-7)
        # 3000 -> Other (30, not in 1-7), 4150 -> Other (41, not in 1-7)
        # 7999 -> Other (79, not in 1-7)
        expected = ["Property", "Other", "Other", "Other", "Other"]
        assert result["crime_category"].tolist() == expected

    def test_edge_case_minimum_codes(self):
        """Minimum codes for each band classified correctly."""
        df = pd.DataFrame({"ucr_general": [100, 200, 300, 400, 500, 600, 700]})
        result = classify_crime_category(df)
        expected = ["Violent", "Violent", "Violent", "Violent", "Property", "Property", "Property"]
        assert result["crime_category"].tolist() == expected

    def test_edge_case_maximum_codes(self):
        """Maximum codes for each band classified correctly."""
        df = pd.DataFrame({"ucr_general": [199, 299, 399, 499, 599, 699, 799]})
        result = classify_crime_category(df)
        expected = ["Violent", "Violent", "Violent", "Violent", "Property", "Property", "Property"]
        assert result["crime_category"].tolist() == expected

    def test_string_ucr_codes(self):
        """String UCR codes are converted and classified correctly."""
        df = pd.DataFrame({"ucr_general": ["100", "200", "500", "999"]})
        result = classify_crime_category(df)
        expected = ["Violent", "Violent", "Property", "Other"]
        assert result["crime_category"].tolist() == expected

    def test_nan_ucr_code(self):
        """NaN UCR codes are classified as Other."""
        df = pd.DataFrame({"ucr_general": [100, None, 500, float("nan")]})
        result = classify_crime_category(df)
        # NaN results in empty ucr_group, which doesn't match any category
        # The function sets crime_category to "Other" by default first
        assert result["crime_category"].tolist() == ["Violent", "Other", "Property", "Other"]

    def test_missing_ucr_general_column_raises(self):
        """Raises ValueError when ucr_general column is missing."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})
        with pytest.raises(ValueError, match="Expected 'ucr_general' column"):
            classify_crime_category(df)

    def test_returns_dataframe(self):
        """Function returns a DataFrame."""
        df = pd.DataFrame({"ucr_general": [100, 200, 300]})
        result = classify_crime_category(df)
        assert isinstance(result, pd.DataFrame)

    def test_returns_copy(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame({"ucr_general": [100]})
        result = classify_crime_category(df)
        result.loc[result.index[0], "crime_category"] = "Modified"
        assert "crime_category" not in df.columns

    def test_preserves_original_columns(self):
        """Preserves all original columns."""
        df = pd.DataFrame(
            {
                "ucr_general": [100, 500],
                "incident_id": ["ABC", "DEF"],
                "date": ["2023-01-01", "2023-01-02"],
            }
        )
        result = classify_crime_category(df)
        assert "incident_id" in result.columns
        assert "date" in result.columns
        assert result["incident_id"].tolist() == ["ABC", "DEF"]

    def test_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"ucr_general": []})
        result = classify_crime_category(df)
        assert len(result) == 0
        assert "crime_category" in result.columns

    def test_single_row(self):
        """Handles single row DataFrame."""
        df = pd.DataFrame({"ucr_general": [100]})
        result = classify_crime_category(df)
        assert len(result) == 1
        assert result["crime_category"].iloc[0] == "Violent"

    def test_crime_category_is_string(self):
        """crime_category column contains string values."""
        df = pd.DataFrame({"ucr_general": [100, 500, 999]})
        result = classify_crime_category(df)
        assert result["crime_category"].dtype == object

    @pytest.mark.parametrize(
        "ucr_code,expected",
        [
            (100, "Violent"),
            (200, "Violent"),
            (300, "Violent"),
            (400, "Violent"),
            (500, "Property"),
            (600, "Property"),
            (700, "Property"),
            (800, "Other"),
            (900, "Other"),
            (999, "Other"),
        ],
    )
    def test_ucr_code_classification(self, ucr_code, expected):
        """Parametrized test for UCR code classification."""
        df = pd.DataFrame({"ucr_general": [ucr_code]})
        result = classify_crime_category(df)
        assert result["crime_category"].iloc[0] == expected
