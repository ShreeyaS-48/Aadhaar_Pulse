import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

"""
    Simple linear regression-based forecasting
    
    Args:
        series: Time series data (pandas Series)
        periods: Number of periods to forecast ahead
    
    Returns:
        dict: Forecast values and confidence intervals
"""

def simple_linear_forecast(series, periods=3):
    if len(series) < 3:
        return {'error': 'Insufficient data for forecasting'}
    
    # Prepare data
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    
    # Fit model
    model = LinearRegression()
    model.fit(X, y)
    
    # Forecast
    future_X = np.arange(len(series), len(series) + periods).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    # Calculate confidence intervals (simplified)
    residuals = y - model.predict(X)
    std_error = np.std(residuals)
    confidence_interval = 1.96 * std_error  # 95% CI
    
    return {
        'forecast': forecast,
        'lower_bound': forecast - confidence_interval,
        'upper_bound': forecast + confidence_interval,
        'model_type': 'Linear Regression',
        'r_squared': model.score(X, y)
    }

"""
    Moving average-based forecasting
    
    Args:
        series: Time series data
        window: Moving average window size
        periods: Number of periods to forecast
    
    Returns:
        dict: Forecast values
"""

def moving_average_forecast(series, window=3, periods=3):
    if len(series) < window:
        return {'error': 'Insufficient data for forecasting'}
    
    ma = series.rolling(window=window).mean()
    last_ma = ma.iloc[-1]
    
    # Simple forecast: use last moving average value
    forecast = np.full(periods, last_ma)
    
    return {
        'forecast': forecast,
        'model_type': f'Moving Average (window={window})'
    }

"""
    Exponential smoothing forecasting
    
    Args:
        series: Time series data
        periods: Number of periods to forecast
        alpha: Smoothing parameter (0-1)
    
    Returns:
        dict: Forecast values
"""

def exponential_smoothing_forecast(series, periods=3, alpha=0.3):
    if len(series) < 3:
        return {'error': 'Insufficient data for forecasting'}
    
    # Simple exponential smoothing
    forecast_values = []
    last_value = series.iloc[-1]
    
    # Use weighted average of recent values
    weights = np.array([alpha * (1 - alpha)**i for i in range(min(10, len(series)))])
    weights = weights / weights.sum()
    
    recent_values = series.iloc[-len(weights):].values
    smoothed_value = np.sum(weights * recent_values)
    
    # Forecast: use smoothed value
    forecast = np.full(periods, smoothed_value)
    
    return {
        'forecast': forecast,
        'model_type': f'Exponential Smoothing (alpha={alpha})'
    }
"""
    Ensemble forecasting using multiple methods
    
    Args:
        series: Time series data
        periods: Number of periods to forecast
    
    Returns:
        dict: Ensemble forecast and individual model forecasts
"""

def ensemble_forecast(series, periods=3):
    forecasts = {}
    # Try different methods
    linear = simple_linear_forecast(series, periods)
    if 'forecast' in linear:
        forecasts['linear'] = linear['forecast']
    ma = moving_average_forecast(series, window=3, periods=periods)
    if 'forecast' in ma:
        forecasts['moving_average'] = ma['forecast']
    es = exponential_smoothing_forecast(series, periods=periods)
    if 'forecast' in es:
        forecasts['exponential_smoothing'] = es['forecast']
    if not forecasts:
        return {'error': 'No forecasting methods succeeded'}
    # Ensemble: simple average
    forecast_array = np.array(list(forecasts.values()))
    ensemble_forecast = np.mean(forecast_array, axis=0)
    
    return {
        'forecast': ensemble_forecast,
        'individual_forecasts': forecasts,
        'model_type': 'Ensemble (Average)',
        'methods_used': list(forecasts.keys())
    }

"""
    Evaluate forecast accuracy metrics
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        dict: Accuracy metrics
"""
def evaluate_forecast_accuracy(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted)
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100 if np.any(actual != 0) else np.nan
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'MAPE': mape
    }


