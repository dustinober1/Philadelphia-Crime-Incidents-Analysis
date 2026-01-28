"""
Unit tests for Phase 2: Core Analysis deliverables
Verifies that all notebooks, figures, and tables from the core analysis phase were properly created
"""

import unittest
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json


class TestPhase2CoreAnalysis(unittest.TestCase):
    """Test suite for Phase 2 Core Analysis deliverables"""

    def setUp(self):
        """Set up test paths and constants"""
        self.project_root = Path.cwd()  # Use current working directory
        self.notebooks_dir = self.project_root / "notebooks"
        self.output_dir = self.project_root / "output"

        # Analysis files created in Phase 2
        self.notebook_files = [
            "02_exploratory_analysis.ipynb",
            "03_temporal_analysis.ipynb",
            "04_geographic_analysis.ipynb",
            "05_offense_breakdown.ipynb",
            "06_disparity_analysis.ipynb",
            "07_cross_factor_analysis.ipynb",
        ]

        # Expected output directories
        self.figure_dirs = [
            "output/figures/exploratory",
            "output/figures/temporal",
            "output/figures/geographic",
            "output/figures/offense",
            "output/figures/disparity",
            "output/figures/cross_factor",
        ]

        self.table_dirs = [
            "output/tables/exploratory",
            "output/tables/temporal",
            "output/tables/geographic",
            "output/tables/offense",
            "output/tables/disparity",
            "output/tables/cross_factor",
        ]

    def test_notebooks_exist(self):
        """Test that all analysis notebooks were created"""
        for notebook in self.notebook_files:
            notebook_path = self.notebooks_dir / notebook
            self.assertTrue(
                notebook_path.exists(), f"Notebook {notebook} does not exist"
            )

            # Verify it's a valid JSON notebook file
            with open(notebook_path, "r", encoding="utf-8") as f:
                try:
                    notebook_content = json.load(f)
                    self.assertIsInstance(notebook_content, dict)
                    self.assertIn("cells", notebook_content)
                    self.assertIn("metadata", notebook_content)
                except json.JSONDecodeError:
                    self.fail(f"{notebook} is not a valid JSON notebook file")

    def test_exploratory_analysis_outputs(self):
        """Test specific outputs from exploratory analysis (02_exploratory_analysis.ipynb)"""
        # Check figures directory exists
        fig_dir = self.output_dir / "figures" / "exploratory"
        self.assertTrue(
            fig_dir.exists(), "Exploratory figures directory does not exist"
        )

        # Check expected figure files
        expected_figures = [
            "temporal_distributions.png",
            "district_distribution.png",
            "offense_distributions.png",
            "missing_values_heatmap.png",
            "bivariate_analysis.png",
            "correlation_matrix.png",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(
                fig_path.exists(), f"Exploratory figure {fig} does not exist"
            )
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Exploratory figure {fig} is empty"
            )

        # Check tables directory exists
        table_dir = self.output_dir / "tables" / "exploratory"
        self.assertTrue(
            table_dir.exists(), "Exploratory tables directory does not exist"
        )

        # Check expected table files
        expected_tables = [
            "summary_stats.csv",
            "correlation_matrix.csv",
            "missing_value_summary.csv",
            "hypotheses.csv",
            "cross_tab_district_offense.csv",
            "district_summary.csv",
            "ucr_distribution.csv",
            "top_offenses.csv",
            "hour_day_crosstab.csv",
            "year_offense_crosstab.csv",
            "strong_correlations.csv",
            "data_quality_flags.csv",
        ]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Exploratory table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Exploratory table {table} is empty")

    def test_temporal_analysis_outputs(self):
        """Test specific outputs from temporal analysis (03_temporal_analysis.ipynb)"""
        fig_dir = self.output_dir / "figures" / "temporal"
        self.assertTrue(fig_dir.exists(), "Temporal figures directory does not exist")

        expected_figures = [
            "stl_decomposition_overall.png",
            "seasonal_factors_by_type.png",
            "trend_comparison_by_type.png",
            "day_of_week_patterns.png",
            "hour_of_day_patterns.png",
            "hour_day_heatmap.png",
            "crime_type_trends_20yr.png",
            "recent_trends_5yr.png",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(fig_path.exists(), f"Temporal figure {fig} does not exist")
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Temporal figure {fig} is empty"
            )

        table_dir = self.output_dir / "tables" / "temporal"
        self.assertTrue(table_dir.exists(), "Temporal tables directory does not exist")

        expected_tables = [
            "seasonal_factors.csv",
            "trend_statistics.csv",
            "monthly_timeseries.csv",
            "temporal_summary_stats.csv",
        ]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Temporal table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Temporal table {table} is empty")

    def test_geographic_analysis_outputs(self):
        """Test specific outputs from geographic analysis (04_geographic_analysis.ipynb)"""
        fig_dir = self.output_dir / "figures" / "geographic"
        self.assertTrue(fig_dir.exists(), "Geographic figures directory does not exist")

        expected_figures = [
            "kde_hotspot_overall.png",
            "kde_hotspot_overall.pdf",
            "kde_hotspot_violent.png",
            "kde_hotspot_property.png",
            "hexbin_density.png",
            "hexbin_density.pdf",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(
                fig_path.exists(), f"Geographic figure {fig} does not exist"
            )
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Geographic figure {fig} is empty"
            )

        table_dir = self.output_dir / "tables" / "geographic"
        self.assertTrue(
            table_dir.exists(), "Geographic tables directory does not exist"
        )

        expected_tables = ["district_profiles.csv", "hotspot_coordinates.csv"]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Geographic table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Geographic table {table} is empty")

    def test_offense_analysis_outputs(self):
        """Test specific outputs from offense breakdown analysis (05_offense_breakdown.ipynb)"""
        fig_dir = self.output_dir / "figures" / "offense"
        self.assertTrue(fig_dir.exists(), "Offense figures directory does not exist")

        expected_figures = [
            "ucr_distribution_top20.png",
            "ucr_category_pie.png",
            "text_general_code_top20.png",
            "severity_distribution.png",
            "severity_by_district_stacked.png",
            "severity_trends_20yr.png",
            "severity_by_hour_heatmap.png",
            "offense_diversity_map.png",
            "offense_trends_by_category.png",
            "top_offenses_trends.png",
            "offense_composition_stacked_area.png",
            "offense_change_diverging.png",
            "seasonality_by_offense.png",
            "offense_correlation_heatmap.png",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(fig_path.exists(), f"Offense figure {fig} does not exist")
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Offense figure {fig} is empty"
            )

        table_dir = self.output_dir / "tables" / "offense"
        self.assertTrue(table_dir.exists(), "Offense tables directory does not exist")

        expected_tables = [
            "ucr_distribution.csv",
            "severity_by_district.csv",
            "severity_by_year.csv",
            "severity_by_hour.csv",
            "offense_diversity_by_district.csv",
            "offense_trends.csv",
            "offense_composition_by_year.csv",
            "offense_change_2006_2025.csv",
            "seasonality_by_offense.csv",
            "offense_correlation_matrix.csv",
        ]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Offense table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Offense table {table} is empty")

    def test_disparity_analysis_outputs(self):
        """Test specific outputs from disparity analysis (06_disparity_analysis.ipynb)"""
        fig_dir = self.output_dir / "figures" / "disparity"
        self.assertTrue(fig_dir.exists(), "Disparity figures directory does not exist")

        expected_figures = [
            "total_incidents_by_district.png",
            "crime_rates_by_district.png",
            "effect_sizes_forest_plot.png",
            "disparity_trends_over_time.png",
            "districts_significance_bar_chart.png",
            "statistical_significance_heatmap.png",
            "district_categories_boxplot.png",
            "offense_distribution_heatmap.png",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(fig_path.exists(), f"Disparity figure {fig} does not exist")
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Disparity figure {fig} is empty"
            )

        table_dir = self.output_dir / "tables" / "disparity"
        self.assertTrue(table_dir.exists(), "Disparity tables directory does not exist")

        expected_tables = [
            "district_comparison_stats.csv",
            "district_profiles_detailed.csv",
            "district_metrics_raw.csv",
        ]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Disparity table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Disparity table {table} is empty")

    def test_cross_factor_analysis_outputs(self):
        """Test specific outputs from cross-factor analysis (07_cross_factor_analysis.ipynb)"""
        fig_dir = self.output_dir / "figures" / "cross_factor"
        self.assertTrue(
            fig_dir.exists(), "Cross-factor figures directory does not exist"
        )

        expected_figures = [
            "correlation_matrix_pearson.png",
            "correlation_matrix_spearman.png",
            "day_offense_heatmap.png",
            "district_category_offense.png",
            "district_day_heatmap.png",
            "district_hour_heatmap.png",
            "district_offense_stacked.png",
            "district_season_heatmap.png",
            "district_trends_comparison.png",
            "hotspot_offense_comparison.png",
            "hour_offense_heatmap.png",
            "season_offense_heatmap.png",
            "temporal_acf.png",
            "three_way_interaction_faceted.png",
            "year_offense_trends.png",
        ]

        for fig in expected_figures:
            fig_path = fig_dir / fig
            self.assertTrue(
                fig_path.exists(), f"Cross-factor figure {fig} does not exist"
            )
            self.assertGreater(
                fig_path.stat().st_size, 0, f"Cross-factor figure {fig} is empty"
            )

        table_dir = self.output_dir / "tables" / "cross_factor"
        self.assertTrue(
            table_dir.exists(), "Cross-factor tables directory does not exist"
        )

        expected_tables = [
            "interaction_tests.csv",
            "correlation_matrix.csv",
            "correlation_matrix_pearson.csv",
            "correlation_matrix_spearman.csv",
        ]

        for table in expected_tables:
            table_path = table_dir / table
            self.assertTrue(
                table_path.exists(), f"Cross-factor table {table} does not exist"
            )
            df = pd.read_csv(table_path)
            self.assertGreater(len(df), 0, f"Cross-factor table {table} is empty")

    def test_all_outputs_directories_exist(self):
        """Test that all expected output directories exist"""
        for fig_dir in self.figure_dirs:
            path = self.project_root / fig_dir
            self.assertTrue(path.exists(), f"Figure directory {fig_dir} does not exist")

        for table_dir in self.table_dirs:
            path = self.project_root / table_dir
            self.assertTrue(
                path.exists(), f"Table directory {table_dir} does not exist"
            )

    def test_statistical_rigor_requirements(self):
        """Test that statistical rigor requirements from Phase 2 were met"""
        # Check that statistical outputs include p-values and confidence intervals
        # by examining key tables

        # Temporal trend statistics should include p-values
        trend_table = self.output_dir / "tables" / "temporal" / "trend_statistics.csv"
        if trend_table.exists():
            df = pd.read_csv(trend_table)
            self.assertIn(
                "p_value", df.columns, "Trend statistics should include p-values"
            )
            # Check for trend coefficient/annual change column (instead of 'slope')
            has_trend_col = any(
                col
                for col in df.columns
                if "change" in col.lower()
                or "slope" in col.lower()
                or "coefficient" in col.lower()
            )
            self.assertTrue(
                has_trend_col, "Trend statistics should include annual change estimates"
            )

        # Disparity analysis should include effect sizes
        comparison_table = (
            self.output_dir / "tables" / "disparity" / "district_comparison_stats.csv"
        )
        if comparison_table.exists():
            df = pd.read_csv(comparison_table)
            # May not have exact column name, but should have effect size measure
            has_effect_size = any(
                col
                for col in df.columns
                if "effect" in col.lower()
                or "cohen" in col.lower()
                or "d_" in col.lower()
            )
            self.assertTrue(
                has_effect_size,
                "Disparity analysis should include effect sizes (Cohen's d)",
            )

        # Cross-factor analysis should include corrected p-values
        interaction_table = (
            self.output_dir / "tables" / "cross_factor" / "interaction_tests.csv"
        )
        if interaction_table.exists():
            df = pd.read_csv(interaction_table)
            has_corrected_p = any(
                col
                for col in df.columns
                if "corrected" in col.lower()
                or "bonferroni" in col.lower()
                or "_adj" in col.lower()
            )
            self.assertTrue(
                has_corrected_p,
                "Cross-factor analysis should include corrected p-values for multiple comparisons",
            )


def run_tests():
    """Run the Phase 2 analysis validation tests"""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase2CoreAnalysis)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"PHASE 2 CORE ANALYSIS VALIDATION RESULTS")
    print(f"{'=' * 60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print(f"\nFAILURES:")
        for test, trace in result.failures:
            print(f"- {test}: {trace.split('AssertionError: ')[-1].strip()}")

    if result.errors:
        print(f"\nERRORS:")
        for test, trace in result.errors:
            print(
                f"- {test}: {trace.split('Traceback')[-1].split('AssertionError: ')[-1].strip()}"
            )

    if not result.failures and not result.errors:
        print(f"\n✓ All Phase 2 Core Analysis deliverables validated successfully!")
        print(
            f"✓ All notebooks, figures, and tables from the analysis phase are present and correct"
        )

    return result


if __name__ == "__main__":
    run_tests()
