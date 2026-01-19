"""
Time Series Forecasting Utilities for Aadhaar Data
Provides predictive modeling capabilities using various time series methods
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def simple_linear_forecast(series, periods=3):
    """
    Simple linear regression-based forecasting
    
    Args:
        series: Time series data (pandas Series)
        periods: Number of periods to forecast ahead
    
    Returns:
        dict: Forecast values and confidence intervals
    """
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


def moving_average_forecast(series, window=3, periods=3):
    """
    Moving average-based forecasting
    
    Args:
        series: Time series data
        window: Moving average window size
        periods: Number of periods to forecast
    
    Returns:
        dict: Forecast values
    """
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


def exponential_smoothing_forecast(series, periods=3, alpha=0.3):
    """
    Exponential smoothing forecasting
    
    Args:
        series: Time series data
        periods: Number of periods to forecast
        alpha: Smoothing parameter (0-1)
    
    Returns:
        dict: Forecast values
    """
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


def arima_forecast(series, periods=3, order=(1, 1, 1)):
    """
    ARIMA forecasting (if statsmodels is available)
    
    Args:
        series: Time series data
        periods: Number of periods to forecast
        order: ARIMA order (p, d, q)
    
    Returns:
        dict: Forecast values
    """
    if not STATSMODELS_AVAILABLE:
        return {'error': 'statsmodels not available'}
    
    if len(series) < 5:
        return {'error': 'Insufficient data for ARIMA'}
    
    try:
        model = ARIMA(series, order=order)
        fitted_model = model.fit()
        forecast = fitted_model.forecast(steps=periods)
        conf_int = fitted_model.get_forecast(steps=periods).conf_int()
        
        return {
            'forecast': forecast.values,
            'lower_bound': conf_int.iloc[:, 0].values,
            'upper_bound': conf_int.iloc[:, 1].values,
            'model_type': f'ARIMA{order}',
            'aic': fitted_model.aic
        }
    except Exception as e:
        return {'error': f'ARIMA fitting failed: {str(e)}'}


def ensemble_forecast(series, periods=3):
    """
    Ensemble forecasting using multiple methods
    
    Args:
        series: Time series data
        periods: Number of periods to forecast
    
    Returns:
        dict: Ensemble forecast and individual model forecasts
    """
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


def evaluate_forecast_accuracy(actual, predicted):
    """
    Evaluate forecast accuracy metrics
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        dict: Accuracy metrics
    """
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


