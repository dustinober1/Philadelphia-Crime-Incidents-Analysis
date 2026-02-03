"""
Classification Model Utilities for Crime Analysis

This module provides utilities for classification model training, time-aware
validation, and feature importance extraction.

All imports use absolute paths via __file__ to ensure modules work regardless
of working directory.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# Ensure absolute path resolution
MODULE_DIR = Path(__file__).parent.absolute()
REPO_ROOT = MODULE_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def create_time_aware_split(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, ensure_sorted: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Create time-aware train/test split (no shuffling).

    Args:
        X: Feature DataFrame (must have datetime index or be pre-sorted)
        y: Target Series
        test_size: Fraction of data to use for testing
        ensure_sorted: Sort by index before splitting

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    if ensure_sorted:
        X = X.sort_index()
        y = y.loc[X.index]

    split_idx = int(len(X) * (1 - test_size))

    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]

    return X_train, X_test, y_train, y_test


def get_time_series_cv(
    n_splits: int = 5, max_train_size: Optional[int] = None
) -> TimeSeriesSplit:
    """
    Get time series cross-validator for hyperparameter tuning.

    Args:
        n_splits: Number of splits
        max_train_size: Maximum size for training set (None = unlimited)

    Returns:
        TimeSeriesSplit object
    """
    return TimeSeriesSplit(n_splits=n_splits, max_train_size=max_train_size)


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    max_depth: int = 10,
    min_samples_split: int = 5,
    min_samples_leaf: int = 2,
    random_state: int = 42,
    scale_features: bool = True,
) -> Tuple[Any, Optional[StandardScaler]]:
    """
    Train Random Forest classifier with sensible defaults.

    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees
        max_depth: Maximum tree depth
        min_samples_split: Minimum samples to split node
        min_samples_leaf: Minimum samples in leaf
        random_state: Random seed for reproducibility
        scale_features: Whether to scale features before training

    Returns:
        Tuple of (trained_model, scaler) where scaler is None if scale_features=False
    """
    from sklearn.ensemble import RandomForestClassifier

    scaler = None
    X_train_processed = X_train

    if scale_features:
        scaler = StandardScaler()
        X_train_processed = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=-1,
    )

    model.fit(X_train_processed, y_train)

    return model, scaler


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    max_depth: int = 6,
    learning_rate: float = 0.1,
    random_state: int = 42,
    scale_features: bool = False,
) -> Tuple[Any, Optional[StandardScaler]]:
    """
    Train XGBoost classifier with sensible defaults.

    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of boosting rounds
        max_depth: Maximum tree depth
        learning_rate: Learning rate (eta)
        random_state: Random seed
        scale_features: Whether to scale features (usually not needed for XGBoost)

    Returns:
        Tuple of (trained_model, scaler) where scaler is None if scale_features=False
    """
    import xgboost as xgb

    scaler = None
    X_train_processed = X_train

    if scale_features:
        scaler = StandardScaler()
        X_train_processed = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )

    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=random_state,
        n_jobs=-1,
        eval_metric="logloss",
    )

    model.fit(X_train_processed, y_train)

    return model, scaler


def extract_feature_importance(
    model: Any, feature_names: List[str], top_n: Optional[int] = None
) -> pd.DataFrame:
    """
    Extract and rank feature importances from trained model.

    Args:
        model: Trained sklearn model with feature_importances_ attribute
        feature_names: List of feature names
        top_n: Return only top N features (None = all)

    Returns:
        DataFrame with features and importances, sorted descending
    """
    importance_df = pd.DataFrame(
        {"feature": feature_names, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)

    if top_n is not None:
        importance_df = importance_df.head(top_n)

    return importance_df.reset_index(drop=True)


def compute_shap_values(
    model: Any, X: pd.DataFrame, sample_size: Optional[int] = 100
) -> Any:
    """
    Compute SHAP values for model interpretability.

    Args:
        model: Trained tree-based model
        X: Feature data to explain
        sample_size: Number of samples to use (None = all, can be slow)

    Returns:
        SHAP values object
    """
    import shap

    X_sample = (
        X
        if sample_size is None
        else X.sample(min(sample_size, len(X)), random_state=42)
    )

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    return shap_values


def evaluate_classifier(
    y_true: pd.Series,
    y_pred: pd.Series,
    y_prob: Optional[pd.Series] = None,
    target_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Evaluate classification model with comprehensive metrics.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Predicted probabilities for positive class (for ROC-AUC)
        target_names: Names for classes in report

    Returns:
        Dictionary with classification metrics
    """
    results = {
        "confusion_matrix": confusion_matrix(y_true, y_pred),
        "classification_report": classification_report(
            y_true, y_pred, target_names=target_names, output_dict=True
        ),
    }

    # Add ROC-AUC if probabilities provided
    if y_prob is not None:
        try:
            results["roc_auc"] = roc_auc_score(y_true, y_prob)
        except ValueError:
            # Binary classification issue or single class
            results["roc_auc"] = None

    return results


def handle_class_imbalance(y_train: pd.Series) -> Dict[int, float]:
    """
    Calculate class weights for imbalanced datasets.

    Args:
        y_train: Training labels

    Returns:
        Dictionary mapping class labels to weights
    """
    from sklearn.utils.class_weight import compute_class_weight

    classes = np.unique(y_train)
    weights = compute_class_weight("balanced", classes=classes, y=y_train)

    return dict(zip(classes, weights))
