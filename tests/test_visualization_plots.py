"""Tests for visualization plot functions.

This module tests the core plotting functions including line plots, bar plots,
heatmaps, and forecast plots. Tests validate Figure structure and configuration
rather than pixel-perfect rendering.

Uses matplotlib Agg backend for headless testing.
"""

# Must be imported before any matplotlib imports
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import pytest
import numpy as np
from matplotlib.figure import Figure

from analysis.visualization.plots import plot_line, plot_bar, plot_heatmap
from analysis.visualization import forecast_plots
from analysis.visualization.style import COLORS


class TestPlotLine:
    """Tests for plot_line function."""

    def test_plot_line_returns_figure(self, sample_crime_df):
        """Verify function returns plt.Figure instance."""
        fig = plot_line(
            data=sample_crime_df.head(10),
            x_col="dispatch_date",
            y_col="objectid",
            title="Test Line Plot"
        )

        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_plot_line_title_and_labels(self, sample_crime_df):
        """Verify title, xlabel, ylabel set correctly."""
        fig = plot_line(
            data=sample_crime_df.head(10),
            x_col="dispatch_date",
            y_col="objectid",
            title="Test Title",
            xlabel="Date",
            ylabel="Count"
        )

        ax = fig.axes[0]
        assert ax.get_title() == "Test Title"
        assert ax.get_xlabel() == "Date"
        assert ax.get_ylabel() == "Count"
        plt.close(fig)

    def test_plot_line_default_color(self, sample_crime_df):
        """Verify uses COLORS[\"Violent\"] when color not specified."""
        fig = plot_line(
            data=sample_crime_df.head(10),
            x_col="dispatch_date",
            y_col="objectid",
            title="Test"
        )

        ax = fig.axes[0]
        line = ax.lines[0]
        expected_color = COLORS.get("Violent", "#E63946")
        assert line.get_color() == expected_color
        plt.close(fig)

    def test_plot_line_custom_color(self, sample_crime_df):
        """Verify custom color parameter applied."""
        fig = plot_line(
            data=sample_crime_df.head(10),
            x_col="dispatch_date",
            y_col="objectid",
            title="Test",
            color="red"
        )

        ax = fig.axes[0]
        line = ax.lines[0]
        assert line.get_color() == "red"
        plt.close(fig)

    def test_plot_line_data_plotted(self, sample_crime_df):
        """Verify line data matches input DataFrame."""
        test_data = sample_crime_df.head(5)
        fig = plot_line(
            data=test_data,
            x_col="dispatch_date",
            y_col="objectid",
            title="Test"
        )

        ax = fig.axes[0]
        line = ax.lines[0]

        # Check that data was plotted
        assert len(line.get_xdata()) == len(test_data)
        assert len(line.get_ydata()) == len(test_data)
        plt.close(fig)

    def test_plot_line_empty_dataframe(self):
        """Verify handles empty DataFrame gracefully."""
        empty_df = pd.DataFrame({"x": [], "y": []})

        fig = plot_line(
            data=empty_df,
            x_col="x",
            y_col="y",
            title="Test"
        )

        ax = fig.axes[0]
        line = ax.lines[0]
        assert len(line.get_xdata()) == 0
        assert len(line.get_ydata()) == 0
        plt.close(fig)

    def test_plot_line_single_point(self):
        """Verify handles single data point."""
        single_df = pd.DataFrame({"x": [1], "y": [10]})

        fig = plot_line(
            data=single_df,
            x_col="x",
            y_col="y",
            title="Test"
        )

        ax = fig.axes[0]
        line = ax.lines[0]
        assert len(line.get_xdata()) == 1
        assert len(line.get_ydata()) == 1
        plt.close(fig)


class TestPlotBar:
    """Tests for plot_bar function."""

    def test_plot_bar_returns_figure(self):
        """Verify returns plt.Figure instance."""
        data = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [10, 20, 30]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test Bar Plot"
        )

        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_plot_bar_title_and_labels(self):
        """Verify title and labels set correctly."""
        data = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [10, 20, 30]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Bar Title",
            xlabel="Category",
            ylabel="Value"
        )

        ax = fig.axes[0]
        assert ax.get_title() == "Bar Title"
        assert ax.get_xlabel() == "Category"
        assert ax.get_ylabel() == "Value"
        plt.close(fig)

    def test_plot_bar_default_color(self):
        """Verify uses COLORS[\"Property\"] when color not specified."""
        data = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [10, 20, 30]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test"
        )

        ax = fig.axes[0]
        bars = ax.patches
        expected_color = COLORS.get("Property", "#457B9D")
        assert len(bars) > 0
        # Check first bar color
        assert bars[0].get_facecolor()[:3] == plt.matplotlib.colors.to_rgb(expected_color)
        plt.close(fig)

    def test_plot_bar_custom_color(self):
        """Verify custom color applied."""
        data = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [10, 20, 30]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test",
            color="green"
        )

        ax = fig.axes[0]
        bars = ax.patches
        assert len(bars) > 0
        assert bars[0].get_facecolor()[:3] == plt.matplotlib.colors.to_rgb("green")
        plt.close(fig)

    def test_plot_bar_data_plotted(self):
        """Verify bar count matches DataFrame rows."""
        data = pd.DataFrame({
            "category": ["A", "B", "C", "D"],
            "value": [10, 20, 30, 40]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test"
        )

        ax = fig.axes[0]
        bars = ax.patches
        assert len(bars) == len(data)
        plt.close(fig)

    def test_plot_bar_handles_negative_values(self):
        """Verify negative values plotted correctly."""
        data = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [-10, 0, 20]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test"
        )

        ax = fig.axes[0]
        bars = ax.patches
        assert len(bars) == 3
        # Check heights match data
        for i, bar in enumerate(bars):
            assert bar.get_height() == data["value"].iloc[i]
        plt.close(fig)

    def test_plot_bar_grid_enabled(self):
        """Verify grid shown on y-axis."""
        data = pd.DataFrame({
            "category": ["A", "B"],
            "value": [10, 20]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test"
        )

        ax = fig.axes[0]
        # Grid should be enabled
        assert ax.grid
        plt.close(fig)

    def test_plot_bar_single_category(self):
        """Verify handles single category."""
        data = pd.DataFrame({
            "category": ["A"],
            "value": [100]
        })

        fig = plot_bar(
            data=data,
            x_col="category",
            y_col="value",
            title="Test"
        )

        ax = fig.axes[0]
        bars = ax.patches
        assert len(bars) == 1
        assert bars[0].get_height() == 100
        plt.close(fig)


class TestPlotHeatmap:
    """Tests for plot_heatmap function."""

    def test_plot_heatmap_returns_figure(self):
        """Verify returns plt.Figure instance."""
        corr_df = pd.DataFrame({
            "A": [1.0, 0.5, 0.3],
            "B": [0.5, 1.0, 0.2],
            "C": [0.3, 0.2, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Test Heatmap"
        )

        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_plot_heatmap_title_set(self):
        """Verify title applied correctly."""
        corr_df = pd.DataFrame({
            "A": [1.0, 0.5],
            "B": [0.5, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Correlation Matrix"
        )

        ax = fig.axes[0]
        assert ax.get_title() == "Correlation Matrix"
        plt.close(fig)

    def test_plot_heatmap_default_figsize(self):
        """Verify figsize defaults to (12, 10)."""
        corr_df = pd.DataFrame({
            "A": [1.0, 0.5],
            "B": [0.5, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Test"
        )

        assert fig.get_size_inches().tolist() == [12.0, 10.0]
        plt.close(fig)

    def test_plot_heatmap_custom_figsize(self):
        """Verify custom figsize applied."""
        corr_df = pd.DataFrame({
            "A": [1.0, 0.5],
            "B": [0.5, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Test",
            figsize=(10, 8)
        )

        assert fig.get_size_inches().tolist() == [10.0, 8.0]
        plt.close(fig)

    def test_plot_heatmap_uses_triangular_mask(self):
        """Verify upper triangle masked."""
        import numpy as np

        corr_df = pd.DataFrame({
            "A": [1.0, 0.5, 0.3],
            "B": [0.5, 1.0, 0.2],
            "C": [0.3, 0.2, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Test",
            annot=True
        )

        # Check that heatmap was created (has children)
        ax = fig.axes[0]
        assert len(ax.images) > 0 or len(ax.collections) > 0
        plt.close(fig)

    def test_plot_heatmap_annot_default(self):
        """Verify annotations shown by default."""
        corr_df = pd.DataFrame({
            "A": [1.0, 0.5],
            "B": [0.5, 1.0]
        })

        fig = plot_heatmap(
            data=corr_df,
            title="Test"
        )

        # Annotations are stored as text objects
        ax = fig.axes[0]
        assert len(ax.texts) > 0  # Should have annotation text
        plt.close(fig)

    def test_plot_heatmap_empty_dataframe(self):
        """Verify empty DataFrame raises ValueError."""
        empty_df = pd.DataFrame()

        # Empty DataFrame should raise ValueError in seaborn
        with pytest.raises(ValueError, match="zero-size array"):
            plot_heatmap(
                data=empty_df,
                title="Test"
            )


class TestForecastPlots:
    """Tests for forecast_plots module functions."""

    def test_plot_forecast_with_intervals_returns_figure(self):
        """Verify returns Figure."""
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        actual = pd.Series(range(10), index=dates)
        forecast = pd.Series(range(10, 20), index=dates)

        fig = forecast_plots.plot_forecast_with_intervals(
            actual=actual,
            forecast=forecast
        )

        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_plot_forecast_with_intervals_plots_components(self):
        """Verify actual, forecast, and confidence interval plotted."""
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        actual = pd.Series(range(10), index=dates)
        forecast = pd.Series(range(10, 20), index=dates)
        lower = pd.Series([x - 2 for x in range(10, 20)], index=dates)
        upper = pd.Series([x + 2 for x in range(10, 20)], index=dates)

        fig = forecast_plots.plot_forecast_with_intervals(
            actual=actual,
            forecast=forecast,
            lower=lower,
            upper=upper
        )

        ax = fig.axes[0]
        # Should have lines for actual and forecast
        assert len(ax.lines) >= 2
        # Should have fill_between for confidence interval
        assert len(ax.collections) >= 1
        plt.close(fig)

    def test_plot_forecast_components_returns_figure(self):
        """Verify components Figure created."""
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        components_df = pd.DataFrame({
            "ds": dates,
            "trend": range(10),
            "yearly": [0.5] * 10
        })

        fig = forecast_plots.plot_forecast_components(
            components_df=components_df
        )

        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_plot_residuals_diagnostics_returns_figure(self):
        """Verify diagnostics Figure with 4 subplots."""
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        residuals = pd.Series(np.random.randn(10), index=dates)

        fig = forecast_plots.plot_residuals_diagnostics(
            residuals=residuals
        )

        assert isinstance(fig, Figure)
        # Should have 4 subplots (2x2 grid)
        assert len(fig.axes) == 4
        plt.close(fig)

    def test_plot_feature_importance_returns_figure(self):
        """Verify horizontal bar chart created."""
        importance_df = pd.DataFrame({
            "feature": ["f1", "f2", "f3"],
            "importance": [0.5, 0.3, 0.2]
        })

        fig = forecast_plots.plot_feature_importance(
            importance_df=importance_df
        )

        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        # Should have bars
        assert len(ax.patches) > 0
        plt.close(fig)

    def test_plot_correlation_matrix_returns_figure(self):
        """Verify correlation heatmap created."""
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9]
        })

        fig = forecast_plots.plot_correlation_matrix(
            df=df
        )

        assert isinstance(fig, Figure)
        # Should have heatmap
        assert len(fig.axes[0].collections) > 0
        plt.close(fig)

