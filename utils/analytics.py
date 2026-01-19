"""
Advanced Analytics Utilities for Aadhaar Data Analysis
Provides statistical analysis, correlation analysis, and anomaly detection functions
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')


def univariate_analysis(df, column):
    """
    Perform comprehensive univariate analysis on a numeric column
    
    Returns:
        dict: Statistical summary including mean, median, std, skewness, kurtosis, etc.
    """
    data = df[column].dropna()
    
    return {
        'count': len(data),
        'mean': data.mean(),
        'median': data.median(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'q25': data.quantile(0.25),
        'q75': data.quantile(0.75),
        'iqr': data.quantile(0.75) - data.quantile(0.25),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data),
        'coefficient_of_variation': (data.std() / data.mean()) * 100 if data.mean() != 0 else 0
    }


def bivariate_correlation(df, col1, col2, method='pearson'):
    """
    Perform bivariate correlation analysis
    
    Args:
        df: DataFrame
        col1, col2: Column names
        method: 'pearson', 'spearman', or 'kendall'
    
    Returns:
        dict: Correlation coefficient, p-value, and interpretation
    """
    data = df[[col1, col2]].dropna()
    
    if len(data) < 3:
        return {
            'correlation': np.nan,
            'p_value': np.nan,
            'interpretation': 'Insufficient data'
        }
    
    corr, p_value = stats.pearsonr(data[col1], data[col2]) if method == 'pearson' else \
                    stats.spearmanr(data[col1], data[col2]) if method == 'spearman' else \
                    stats.kendalltau(data[col1], data[col2])
    
    # Interpretation
    abs_corr = abs(corr)
    if abs_corr < 0.3:
        strength = 'Weak'
    elif abs_corr < 0.7:
        strength = 'Moderate'
    else:
        strength = 'Strong'
    
    direction = 'Positive' if corr > 0 else 'Negative'
    significance = 'Significant' if p_value < 0.05 else 'Not Significant'
    
    return {
        'correlation': corr,
        'p_value': p_value,
        'strength': strength,
        'direction': direction,
        'significance': significance,
        'interpretation': f'{strength} {direction.lower()} correlation ({significance.lower()})'
    }


def trivariate_analysis(df, x_col, y_col, z_col):
    """
    Perform trivariate analysis to understand relationships between three variables
    
    Returns:
        dict: Multiple correlation coefficients and partial correlations
    """
    data = df[[x_col, y_col, z_col]].dropna()
    
    if len(data) < 3:
        return {'error': 'Insufficient data'}
    
    # Pairwise correlations
    corr_xy = data[x_col].corr(data[y_col])
    corr_xz = data[x_col].corr(data[z_col])
    corr_yz = data[y_col].corr(data[z_col])
    
    # Partial correlation: correlation between x and y controlling for z
    # r_xy.z = (r_xy - r_xz * r_yz) / sqrt((1 - r_xz^2) * (1 - r_yz^2))
    partial_xy_z = (corr_xy - corr_xz * corr_yz) / \
                   np.sqrt((1 - corr_xz**2) * (1 - corr_yz**2)) if \
                   (1 - corr_xz**2) * (1 - corr_yz**2) > 0 else np.nan
    
    return {
        'correlation_xy': corr_xy,
        'correlation_xz': corr_xz,
        'correlation_yz': corr_yz,
        'partial_correlation_xy_given_z': partial_xy_z,
        'interpretation': 'Partial correlation shows relationship between X and Y after controlling for Z'
    }


def detect_anomalies_isolation_forest(df, columns, contamination=0.1):
    """
    Detect anomalies using Isolation Forest algorithm
    
    Args:
        df: DataFrame
        columns: List of columns to use for anomaly detection
        contamination: Expected proportion of anomalies
    
    Returns:
        DataFrame with anomaly flags
    """
    data = df[columns].dropna()
    
    if len(data) < 10:
        return df.assign(is_anomaly=False)
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    anomalies = iso_forest.fit_predict(scaled_data)
    
    result_df = df.copy()
    result_df['is_anomaly'] = False
    result_df.loc[data.index, 'is_anomaly'] = (anomalies == -1)
    
    return result_df


def detect_statistical_anomalies(df, column, method='iqr', threshold=3):
    """
    Detect statistical anomalies using IQR or Z-score method
    
    Args:
        df: DataFrame
        column: Column name
        method: 'iqr' or 'zscore'
        threshold: Z-score threshold (for zscore method) or multiplier (for iqr)
    
    Returns:
        DataFrame with anomaly flags
    """
    data = df[column].dropna()
    
    result_df = df.copy()
    result_df['is_anomaly'] = False
    
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        anomalies = (data < lower_bound) | (data > upper_bound)
    else:  # zscore
        z_scores = np.abs(stats.zscore(data))
        anomalies = z_scores > threshold
    
    result_df.loc[data.index[anomalies], 'is_anomaly'] = True
    
    return result_df


def calculate_gini_coefficient(values):
    """
    Calculate Gini coefficient to measure inequality/distribution
    
    Args:
        values: Array-like of numeric values
    
    Returns:
        float: Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    """
    values = np.array(values)
    values = values[values >= 0]  # Remove negative values
    
    if len(values) == 0 or np.sum(values) == 0:
        return 0
    
    sorted_values = np.sort(values)
    n = len(sorted_values)
    index = np.arange(1, n + 1)
    
    gini = (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n
    
    return gini


def calculate_concentration_ratio(values, top_n=3):
    """
    Calculate concentration ratio (share of top N entities)
    
    Args:
        values: Array-like of numeric values
        top_n: Number of top entities to consider
    
    Returns:
        float: Concentration ratio (0-1)
    """
    values = np.array(values)
    total = np.sum(values)
    
    if total == 0:
        return 0
    
    sorted_values = np.sort(values)[::-1]
    top_sum = np.sum(sorted_values[:top_n])
    
    return top_sum / total


def perform_trend_analysis(series, window=3):
    """
    Perform trend analysis on time series data
    
    Args:
        series: Time series data (pandas Series with datetime index)
        window: Moving average window
    
    Returns:
        dict: Trend metrics including slope, direction, and strength
    """
    if len(series) < 2:
        return {'error': 'Insufficient data'}
    
    # Calculate moving average
    ma = series.rolling(window=min(window, len(series))).mean()
    
    # Linear regression for trend
    x = np.arange(len(series))
    y = series.values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Determine trend direction
    if slope > 0:
        direction = 'Increasing'
    elif slope < 0:
        direction = 'Decreasing'
    else:
        direction = 'Stable'
    
    # Trend strength
    if abs(r_value) < 0.3:
        strength = 'Weak'
    elif abs(r_value) < 0.7:
        strength = 'Moderate'
    else:
        strength = 'Strong'
    
    return {
        'slope': slope,
        'r_squared': r_value**2,
        'p_value': p_value,
        'direction': direction,
        'strength': strength,
        'interpretation': f'{strength} {direction.lower()} trend'
    }


