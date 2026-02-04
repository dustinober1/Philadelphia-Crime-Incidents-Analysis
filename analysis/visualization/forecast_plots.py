"""
Forecast Visualization Utilities for Crime Analysis

This module provides visualization functions for time series forecasts,
classification models, and statistical analysis.

All functions return matplotlib/plotly objects suitable for embedding in notebooks.
Uses absolute path resolution via __file__ for consistency.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Ensure absolute path resolution
MODULE_DIR = Path(__file__).parent.absolute()
REPO_ROOT = MODULE_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Set default style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def plot_forecast_with_intervals(
    actual: pd.Series,
    forecast: pd.Series,
    lower: pd.Series | None = None,
    upper: pd.Series | None = None,
    title: str = "Crime Forecast",
    xlabel: str = "Date",
    ylabel: str = "Incidents",
    figsize: tuple[int, int] = (14, 7),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot time series forecast with confidence intervals.

    Args:
        actual: Actual values (historical + future if available)
        forecast: Forecasted values
        lower: Lower bound of prediction interval
        upper: Upper bound of prediction interval
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot actual values
    ax.plot(
        actual.index,
        actual.values,
        "o-",
        label="Actual",
        color="black",
        markersize=3,
        alpha=0.7,
    )

    # Plot forecast
    ax.plot(
        forecast.index,
        forecast.values,
        "-",
        label="Forecast",
        color="steelblue",
        linewidth=2,
    )

    # Plot confidence intervals
    if lower is not None and upper is not None:
        ax.fill_between(
            forecast.index,
            lower.values,
            upper.values,
            alpha=0.2,
            color="steelblue",
            label="95% Confidence Interval",
        )

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_forecast_components(
    components_df: pd.DataFrame,
    title: str = "Forecast Components",
    figsize: tuple[int, int] = (14, 10),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot decomposed forecast components (trend, seasonality, etc.).

    Args:
        components_df: DataFrame with trend, yearly, weekly, etc. columns
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    component_cols = [
        col
        for col in components_df.columns
        if col not in ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]

    n_components = len(component_cols)
    fig, axes = plt.subplots(n_components, 1, figsize=figsize, sharex=True)

    if n_components == 1:
        axes = [axes]

    for ax, col in zip(axes, component_cols):
        ax.plot(components_df["ds"], components_df[col], color="steelblue", linewidth=1.5)
        ax.set_ylabel(col.replace("_", " ").title(), fontsize=10)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Date", fontsize=12)
    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.00)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_residuals_diagnostics(
    residuals: pd.Series,
    title: str = "Residuals Diagnostics",
    figsize: tuple[int, int] = (14, 8),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Create diagnostic plots for forecast residuals.

    Args:
        residuals: Series of residuals (actual - predicted)
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # Residuals over time
    axes[0, 0].plot(residuals.index, residuals.values, "o-", alpha=0.6)
    axes[0, 0].axhline(y=0, color="red", linestyle="--", alpha=0.5)
    axes[0, 0].set_xlabel("Date")
    axes[0, 0].set_ylabel("Residuals")
    axes[0, 0].set_title("Residuals Over Time")
    axes[0, 0].grid(True, alpha=0.3)

    # Histogram of residuals
    axes[0, 1].hist(residuals.dropna(), bins=30, edgecolor="black", alpha=0.7)
    axes[0, 1].axvline(x=0, color="red", linestyle="--", alpha=0.5)
    axes[0, 1].set_xlabel("Residual Value")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title("Distribution of Residuals")
    axes[0, 1].grid(True, alpha=0.3)

    # Q-Q plot
    from scipy import stats

    stats.probplot(residuals.dropna(), dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title("Q-Q Plot")
    axes[1, 0].grid(True, alpha=0.3)

    # ACF plot
    from pandas.plotting import autocorrelation_plot

    autocorrelation_plot(residuals.dropna(), ax=axes[1, 1])
    axes[1, 1].set_title("Autocorrelation of Residuals")
    axes[1, 1].grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_feature_importance(
    importance_df: pd.DataFrame,
    top_n: int = 20,
    title: str = "Feature Importance",
    figsize: tuple[int, int] = (10, 8),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot feature importance from classification model.

    Args:
        importance_df: DataFrame with 'feature' and 'importance' columns
        top_n: Number of top features to display
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Take top N features
    plot_df = importance_df.head(top_n).sort_values("importance")

    # Create horizontal bar plot
    ax.barh(plot_df["feature"], plot_df["importance"], color="steelblue", alpha=0.8)
    ax.set_xlabel("Importance", fontsize=12)
    ax.set_ylabel("Feature", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_shap_summary(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    title: str = "SHAP Feature Importance",
    max_display: int = 20,
    figsize: tuple[int, int] = (10, 8),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot SHAP summary for model interpretability.

    Args:
        shap_values: SHAP values array
        X: Feature DataFrame
        title: Plot title
        max_display: Maximum number of features to display
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    import shap

    fig, ax = plt.subplots(figsize=figsize)

    # For binary classification, use values for positive class
    values = shap_values[1] if isinstance(shap_values, list) else shap_values

    shap.summary_plot(values, X, max_display=max_display, show=False)
    plt.title(title, fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_correlation_matrix(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    title: str = "Correlation Matrix",
    figsize: tuple[int, int] = (12, 10),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot correlation matrix heatmap.

    Args:
        df: DataFrame with numeric columns
        columns: Specific columns to include (None = all numeric)
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Select columns
    if columns is None:
        corr_df = df.select_dtypes(include=[np.number])
    else:
        corr_df = df[columns]

    # Compute correlation
    corr = corr_df.corr()

    # Create heatmap
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_anomaly_detection(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    anomaly_col: str,
    title: str = "Anomaly Detection",
    figsize: tuple[int, int] = (14, 7),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot time series with anomalies highlighted.

    Args:
        df: DataFrame with time series and anomaly indicators
        date_col: Name of date column
        value_col: Name of value column
        anomaly_col: Name of boolean anomaly column
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot normal points
    normal = df[~df[anomaly_col]]
    ax.plot(
        normal[date_col],
        normal[value_col],
        "o-",
        label="Normal",
        color="steelblue",
        markersize=3,
        alpha=0.7,
    )

    # Highlight anomalies
    anomalies = df[df[anomaly_col]]
    ax.scatter(
        anomalies[date_col],
        anomalies[value_col],
        color="red",
        s=100,
        marker="X",
        label="Anomaly",
        zorder=5,
    )

    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(value_col, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: list[str] | None = None,
    title: str = "Confusion Matrix",
    figsize: tuple[int, int] = (8, 6),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot confusion matrix heatmap.

    Args:
        cm: Confusion matrix array
        class_names: Names for classes (optional)
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Normalize for percentages
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    # Create heatmap
    sns.heatmap(
        cm_norm,
        annot=True,
        fmt=".2%",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )

    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_roc_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    title: str = "ROC Curve",
    figsize: tuple[int, int] = (8, 6),
    save_path: str | None = None,
) -> plt.Figure:
    """
    Plot ROC curve for binary classification.

    Args:
        y_true: True binary labels
        y_prob: Predicted probabilities for positive class
        title: Plot title
        figsize: Figure size tuple
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    from sklearn.metrics import auc, roc_curve

    fig, ax = plt.subplots(figsize=figsize)

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    ax.plot(fpr, tpr, color="steelblue", lw=2, label=f"ROC curve (AUC = {roc_auc:.2f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Random")

    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig
