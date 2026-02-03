# Phase 4: Forecasting & Predictive Modeling - Research

**Researched:** Mon Feb 02 2026
**Domain:** Time Series Forecasting, Machine Learning Classification, Statistical Analysis
**Confidence:** HIGH

## Summary

Phase 4 involves three main components: time series forecasting using Prophet/ARIMA, classification modeling using scikit-learn/XGBoost, and statistical analysis of heat-crime relationships. The research covers standard libraries for each component, recommended architectures, and common implementation pitfalls. The primary focus is on building reproducible models with proper validation, interpretability, and forecast horizons as specified in the requirements.

**Primary recommendation:** Use Prophet for time series forecasting with seasonal components, Random Forest/XGBoost for violence classification, and scipy.stats for hypothesis testing of heat-crime relationships.

## Standard Stack

The established libraries/tools for this domain:

### Core Time Series Forecasting
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| prophet | latest | Time series forecasting with trend/seasonality | Industry standard for business forecasting, handles missing data/seasonality well |
| statsmodels | 0.14+ | ARIMA/SARIMA time series modeling | Well-established statistical methods, transparent parameters |
| scikit-learn | 1.3+ | Model validation and preprocessing | Standard ML library with robust cross-validation tools |

### Core Classification & ML
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| xgboost | 2.0+ | Gradient boosting classifier | High performance, good for structured tabular data |
| scikit-learn | 1.3+ | Random Forest and preprocessing | Interpretable, handles mixed features well |
| lightgbm | 4.0+ | Alternative gradient boosting | Sometimes faster than XGBoost |
| shap | 0.40+ | Feature importance interpretation | Provides SHAP values for model interpretability |

### Statistical Analysis
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scipy | 1.11+ | Statistical tests and distributions | Standard statistical hypothesis testing |
| statsmodels | 0.14+ | Advanced statistical models | Regression diagnostics and inference |
| pingouin | 0.5+ | Simplified statistical analysis | User-friendly statistical functions |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| seaborn | 0.13+ | Statistical visualizations | Correlation matrices, distribution plots |
| matplotlib | 3.8+ | Custom plotting | Publication-quality figures |
| plotly | 5.15+ | Interactive visualizations | Explorable time series plots |

### Installation:
```bash
# For conda environment (as per project rules)
conda install -c conda-forge prophet scikit-learn xgboost shap scipy seaborn plotly
# Additional installation for XGBoost if needed
conda install -c conda-forge xgboost lightgbm pingouin
```

## Architecture Patterns

### Recommended Project Structure
```
notebooks/
├── 04_forecasting_crime_ts.ipynb      # Time series forecasting
├── 04_classification_violence.ipynb   # Violence classification model
└── 04_hypothesis_heat_crime.ipynb     # Heat-crime relationship analysis
src/
├── analysis/models/                    # Model utilities
│   ├── time_series.py                  # Forecasting utilities
│   ├── classification.py               # Classification utilities
│   └── validation.py                   # Cross-validation helpers
└── analysis/visualization/             # Plotting functions
    └── forecast_plots.py               # Forecast visualizations
```

### Pattern 1: Time Series Forecasting Pipeline
**What:** End-to-end forecasting with Prophet including train/validation split and prediction intervals
**When to use:** When implementing FORECAST-01 requirement with 30-60 day horizon
**Example:**
```python
import pandas as pd
from prophet import Prophet
import numpy as np

# Prepare data for Prophet (ds, y columns)
df = df[['date', 'crime_count']].rename(columns={'date': 'ds', 'crime_count': 'y'})

# Split into train and validation sets
train_end = df['ds'].max() - pd.Timedelta(days=30)
train_df = df[df['ds'] <= train_end].copy()

# Initialize and fit model
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    interval_width=0.95,  # 95% confidence intervals
    changepoint_prior_scale=0.05
)
model.fit(train_df)

# Create future dataframe
future = model.make_future_dataframe(periods=60)  # 60-day forecast
forecast = model.predict(future)

# Extract prediction intervals and point forecasts
predictions_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

### Pattern 2: Classification Pipeline with Time-Aware Validation
**What:** Classification model with proper temporal splitting and validation
**When to use:** When implementing FORECAST-02 violence classification requirement
**Example:**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, roc_auc_score
import xgboost as xgb

# Use time series split for validation
tscv = TimeSeriesSplit(n_splits=5)

# Prepare features and target (ensure temporal order maintained)
X = features.sort_index()
y = target[X.index]

# Fit model with time-aware validation
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)

# Fit on entire training set
model.fit(X, y)

# Get feature importances
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

### Pattern 3: Statistical Hypothesis Testing
**What:** Proper statistical testing for heat-crime relationships
**When to use:** When implementing HYP-HEAT requirement
**Example:**
```python
import scipy.stats as stats
import pandas as pd

def correlation_with_significance(x, y, method='pearson'):
    """Calculate correlation with significance testing"""
    corr, p_value = stats.pearsonr(x, y)
    n = len(x)
    
    return {
        'correlation': corr,
        'p_value': p_value,
        'n_obs': n,
        'significant_at_0_05': p_value < 0.05,
        'effect_size': 'large' if abs(corr) > 0.5 else 'medium' if abs(corr) > 0.3 else 'small'
    }

# Test correlation between temperature and violent crimes
temp_crime_corr = correlation_with_significance(df['temperature'], df['violent_crime_count'])
```

### Anti-Patterns to Avoid
- **Using random train/test splits for time series:** Always use time-based splits (no shuffling)
- **Ignoring seasonality in crime data:** Crime typically has strong weekly/seasonal patterns
- **Overfitting to recent patterns:** Validate on holdout periods, especially during unusual events
- **Not accounting for data leakage:** Ensure future information isn't used in feature engineering

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Time series decomposition | Custom STL implementation | Prophet's built-in components | Prophet handles trend, seasonality, holidays robustly |
| Feature selection for RF/XGBoost | Manual recursive elimination | Built-in feature importances | Libraries provide permutation importance and SHAP values |
| Time series cross-validation | Manual date splits | TimeSeriesSplit in sklearn | Properly handles temporal dependencies |
| Prediction intervals | Manual bootstrap | Prophet's built-in intervals | Proper uncertainty quantification |
| Hyperparameter tuning | Grid search loops | sklearn.model_selection tools | Efficient, optimized implementations |
| Statistical significance tests | Manual calculations | scipy.stats functions | Correctly handles degrees of freedom, assumptions |

**Key insight:** Time series and ML libraries implement decades of research in numerical stability, statistical correctness, and computational efficiency. Building custom solutions risks introducing errors and reinventing well-solved problems.

## Common Pitfalls

### Pitfall 1: Temporal Data Leakage
**What goes wrong:** Using future information in training features causing overly optimistic performance estimates
**Why it happens:** Including lagged target variables or rolling statistics that include future observations
**How to avoid:** Always sort data by time, use time-aware cross-validation splits, validate that no future data influences past predictions
**Warning signs:** Unusually high accuracy scores, perfect predictions at certain time points

### Pitfall 2: Non-Stationary Time Series
**What goes wrong:** Trending crime patterns causing unreliable forecasts
**Why it happens:** Crime rates change due to policy, demographics, economic factors
**How to avoid:** Use differencing, detrending, or Prophet's automatic trend handling
**Warning signs:** Forecast intervals getting wider over time, systematic bias in residuals

### Pitfall 3: Overfitting to Seasonal Patterns
**What goes wrong:** Model captures noise instead of true seasonal effects
**Why it happens:** Too complex seasonal components or insufficient regularization
**How to avoid:** Use appropriate regularization, validate on out-of-sample seasons, examine residuals
**Warning signs:** Very complex seasonal curves that don't make domain sense

### Pitfall 4: Imbalanced Class Distribution
**What goes wrong:** Violence classification models biased toward majority class
**Why it happens:** Violent crimes often much less frequent than property crimes
**How to avoid:** Use stratified sampling, class weights, appropriate metrics (precision/recall/F1)
**Warning signs:** High overall accuracy but poor performance on minority class

### Pitfall 5: Ignoring Spatial Dependencies
**What goes wrong:** Treating all locations independently when crime clusters spatially
**Why it happens:** Aggregating across areas without considering spatial autocorrelation
**How to avoid:** Include spatial features, consider space-time models, validate on spatial holdouts
**Warning signs:** Poor performance in specific geographic areas consistently

## Code Examples

Verified patterns from official sources:

### Time Series Forecasting with Prophet
```python
# Source: https://facebook.github.io/prophet/docs/
import pandas as pd
from prophet import Prophet
import numpy as np

# Prepare data in Prophet format
df_prophet = pd.DataFrame({
    'ds': dates,  # datetime column
    'y': values   # numeric values to forecast
})

# Create model with custom seasonality and changepoints
model = Prophet(
    growth='linear',
    n_changepoints=25,
    changepoint_range=0.8,  # 80% of history for changepoints
    yearly_seasonality='auto',
    weekly_seasonality='auto',
    daily_seasonality=False,
    holidays=None,
    seasonality_mode='multiplicative',
    seasonality_prior_scale=10.0,
    changepoint_prior_scale=0.05,
    interval_width=0.95,
    uncertainty_samples=1000
)

# Fit model
model.fit(df_prophet)

# Create future dataframe for forecasting
future = model.make_future_dataframe(
    periods=60,  # 60-day forecast
    freq='D'
)

# Generate forecasts
forecast = model.predict(future)

# Access components
components = model.plot_components(forecast)
```

### Classification with Feature Importance
```python
# Source: https://scikit-learn.org/stable/
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import shap

# Prepare data maintaining temporal order
X_train = X[train_mask]
y_train = y[train_mask] 
X_test = X[test_mask]
y_test = y[test_mask]

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = rf_model.predict(X_test_scaled)
y_prob = rf_model.predict_proba(X_test_scaled)[:, 1]

# Feature importance
importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

# SHAP for interpretability
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_test_scaled[:100])  # Sample for efficiency
```

### Statistical Correlation Testing
```python
# Source: https://docs.scipy.org/doc/scipy/reference/stats.html
import scipy.stats as stats
import numpy as np
import pandas as pd

def analyze_correlation(x, y, x_label='', y_label=''):
    """
    Comprehensive correlation analysis with multiple tests
    """
    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(x, y)
    
    # Spearman rank correlation (robust to outliers)
    spearman_r, spearman_p = stats.spearmanr(x, y)
    
    # Kendall tau (robust to outliers, good for small samples)
    kendall_tau, kendall_p = stats.kendalltau(x, y)
    
    # Linear regression for effect size
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    results = {
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'kendall_tau': kendall_tau,
        'kendall_p': kendall_p,
        'regression_slope': slope,
        'regression_intercept': intercept,
        'regression_r_squared': r_value**2,
        'regression_p_value': p_value,
        'n_observations': len(x),
        'strength': 'negligible' if abs(pearson_r) < 0.1 else 
                   'small' if abs(pearson_r) < 0.3 else 
                   'medium' if abs(pearson_r) < 0.5 else 'large'
    }
    
    return results
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ARIMA-only models | Prophet + ensemble methods | 2017+ | Better handling of trends, holidays, missing data |
| Simple linear classifiers | Tree-based ensembles (RF/XGBoost) | 2015+ | Better handling of non-linear patterns |
| Manual feature selection | Automated importance ranking (SHAP) | 2018+ | More interpretable model decisions |
| Basic statistical tests | Robust correlation measures | 2020+ | Better handling of non-normal distributions |

**Deprecated/outdated:**
- ARIMA without seasonal components for crime data: Seasonal patterns are crucial
- Logistic regression for imbalanced binary classification: Tree-based methods often superior
- Manual hyperparameter tuning: Use sklearn's built-in tools

## Open Questions

Things that couldn't be fully resolved:

1. **Threshold definition for anomalies**
   - What we know: Requirement mentions "clear threshold definition for anomalies"
   - What's unclear: Specific criteria for operational alerts vs. statistical anomalies
   - Recommendation: Define based on business impact and ROC analysis

2. **Weather data integration strategy**
   - What we know: Need to merge hourly weather and crime data
   - What's unclear: Geographic granularity of weather data and optimal temporal aggregation
   - Recommendation: Use closest weather station to crime districts, test various aggregations

## Sources

### Primary (HIGH confidence)
- Facebook Prophet documentation: https://facebook.github.io/prophet/docs/
- Scikit-learn documentation: https://scikit-learn.org/stable/
- XGBoost documentation: https://xgboost.readthedocs.io/
- SciPy statistical functions: https://docs.scipy.org/doc/scipy/reference/stats.html

### Secondary (MEDIUM confidence)
- Time series best practices from literature
- Crime forecasting research papers
- Statistical learning methodology handbooks

### Tertiary (LOW confidence)
- Blog posts on time series forecasting (require verification)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Based on current library documentation
- Architecture: HIGH - Standard industry practices
- Pitfalls: HIGH - Well-documented in literature
- Code examples: HIGH - From official documentation

**Research date:** Mon Feb 02 2026
**Valid until:** Wed Mar 04 2026