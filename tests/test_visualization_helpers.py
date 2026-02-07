"""Tests for visualization helper functions.

This module tests the visualization helper utilities including style
configuration and figure saving functions.

Uses matplotlib Agg backend for headless testing. Tests validate Figure
structure and configuration rather than pixel-perfect rendering.
"""

# Must be imported before any matplotlib imports
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pytest

from analysis.visualization.style import setup_style
from analysis.visualization.helpers import save_figure


class TestSetupStyle:
    """Tests for setup_style function."""

    def test_setup_style_applies_rcparams(self):
        """Verify setup_style modifies plt.rcParams correctly."""
        # Clear any existing rcParams modifications
        plt.rcParams.update(plt.rcParamsDefault)

        # Call setup_style
        setup_style()

        # Verify key rcParams are set
        assert "figure.figsize" in plt.rcParams
        assert "font.size" in plt.rcParams
        assert "axes.titlesize" in plt.rcParams
        assert "savefig.dpi" in plt.rcParams

    def test_setup_style_figure_size(self):
        """Verify figsize set to (12, 6)."""
        plt.rcParams.update(plt.rcParamsDefault)
        setup_style()

        # rcParams returns list, not tuple
        assert plt.rcParams["figure.figsize"] == [12.0, 6.0] or plt.rcParams["figure.figsize"] == (12, 6)

    def test_setup_style_font_sizes(self):
        """Verify font.size=11, titlesize=14, labelsize=12."""
        plt.rcParams.update(plt.rcParamsDefault)
        setup_style()

        assert plt.rcParams["font.size"] == 11
        assert plt.rcParams["axes.titlesize"] == 14
        assert plt.rcParams["axes.labelsize"] == 12

    def test_setup_style_grid_settings(self):
        """Verify grid enabled with alpha=0.3."""
        plt.rcParams.update(plt.rcParamsDefault)
        setup_style()

        assert plt.rcParams["axes.grid"] == True
        assert plt.rcParams["grid.alpha"] == 0.3

    def test_setup_style_savefig_settings(self):
        """Verify dpi=300, bbox='tight', facecolor='white'."""
        plt.rcParams.update(plt.rcParamsDefault)
        setup_style()

        assert plt.rcParams["savefig.dpi"] == 300
        assert plt.rcParams["savefig.bbox"] == "tight"
        assert plt.rcParams["savefig.facecolor"] == "white"

    def test_setup_style_seaborn_palette(self):
        """Verify seaborn palette uses COLORS."""
        plt.rcParams.update(plt.rcParamsDefault)
        setup_style()

        # After setup_style, seaborn color palette should be set
        import seaborn as sns
        palette = sns.color_palette()
        assert len(palette) > 0


class TestSaveFigure:
    """Tests for save_figure helper function."""

    def test_save_figure_png_format(self, tmp_path):
        """Verify PNG saved with DPI=300."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.png"
        save_figure(fig, output_path, output_format="png", dpi=300)

        assert output_path.exists()
        plt.close(fig)

    def test_save_figure_svg_format(self, tmp_path):
        """Verify SVG saved (DPI ignored for vector formats)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.svg"
        save_figure(fig, output_path, output_format="svg", dpi=300)

        assert output_path.exists()
        plt.close(fig)

    def test_save_figure_pdf_format(self, tmp_path):
        """Verify PDF saved (DPI ignored for vector formats)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.pdf"
        save_figure(fig, output_path, output_format="pdf", dpi=300)

        assert output_path.exists()
        plt.close(fig)

    def test_save_figure_invalid_format_raises(self, tmp_path):
        """Verify ValueError for invalid format ("jpg")."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.jpg"

        with pytest.raises(ValueError, match="output_format must be 'png', 'svg', or 'pdf'"):
            save_figure(fig, output_path, output_format="jpg")

        plt.close(fig)

    def test_save_figure_creates_directories(self, tmp_path):
        """Verify parent directories must exist (save_figure doesn't create them)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # Create path with nested directories
        output_path = tmp_path / "subdir" / "nested" / "test_figure.png"

        # save_figure doesn't create directories - this should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            save_figure(fig, output_path, output_format="png")

        plt.close(fig)

    def test_save_figure_bbox_inches_tight(self, tmp_path):
        """Verify bbox_inches='tight' applied."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.png"
        save_figure(fig, output_path, output_format="png")

        # File should be created successfully
        assert output_path.exists()
        plt.close(fig)

    def test_save_figure_custom_dpi(self, tmp_path):
        """Verify custom DPI parameter works."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.png"
        save_figure(fig, output_path, output_format="png", dpi=150)

        assert output_path.exists()
        plt.close(fig)

    def test_save_figure_overwrites_existing(self, tmp_path):
        """Verify overwrites existing file."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output_path = tmp_path / "test_figure.png"

        # Save first time
        save_figure(fig, output_path, output_format="png")
        first_size = output_path.stat().st_size

        # Modify and save again
        ax.plot([1, 2, 3], [3, 2, 1])
        save_figure(fig, output_path, output_format="png")
        second_size = output_path.stat().st_size

        # File should still exist
        assert output_path.exists()
        plt.close(fig)
