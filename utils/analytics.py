import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

"""
    Perform comprehensive univariate analysis on a numeric column
    
    Returns:
        dict: Statistical summary including mean, median, std, skewness, kurtosis, etc.
"""
def univariate_analysis(df, column):
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
"""
    Perform bivariate correlation analysis
    
    Args:
        df: DataFrame
        col1, col2: Column names
        method: 'pearson', 'spearman', or 'kendall'
    
    Returns:
        dict: Correlation coefficient, p-value, and interpretation
"""
def bivariate_correlation(df, col1, col2, method='pearson'):
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
"""
    Detect anomalies using Isolation Forest algorithm
    
    Args:
        df: DataFrame
        columns: List of columns to use for anomaly detection
        contamination: Expected proportion of anomalies
    
    Returns:
        DataFrame with anomaly flags
"""
def detect_anomalies_isolation_forest(df, columns, contamination=0.1):
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
