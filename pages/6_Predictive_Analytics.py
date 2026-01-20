import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_loader import load_aadhaar_data
from utils.forecasting import (
    ensemble_forecast, evaluate_forecast_accuracy
)

st.set_page_config(page_title="Predictive Analytics", layout="wide", initial_sidebar_state="expanded")

st.title("Predictive Analytics and Forecasting")
st.markdown("**Time series forecasting and predictive modeling for Aadhaar enrolment and update trends**")
st.divider()

[df, df_demo, df_bio] = load_aadhaar_data()

# Sidebar configuration
st.sidebar.header("Forecasting Configuration")
forecast_type = st.sidebar.selectbox(
    "Forecast Type",
    ["Enrolments", "Demographic Updates", "Biometric Updates"]
)
forecast_level = st.sidebar.selectbox(
    "Forecast Level",
    ["National", "State", "District"]
)
forecast_periods = st.sidebar.slider("Forecast Periods (Months)", 1, 12, 3)
df['month'] = df['date'].dt.to_period('M')
df_demo['month'] = df_demo['date'].dt.to_period('M')
df_bio['month'] = df_bio['date'].dt.to_period('M')
if forecast_level == "National":
    if forecast_type == "Enrolments":
        time_series = df.groupby('month')['total_enrolments'].sum().sort_index()
    elif forecast_type == "Demographic Updates":
        time_series = df_demo.groupby('month')['total_updates'].sum().sort_index()
    else:
        time_series = df_bio.groupby('month')['total_updates'].sum().sort_index()
    location_name = "India"
elif forecast_level == "State":
    state = st.sidebar.selectbox("Select State", sorted(df['state'].unique()))
    if forecast_type == "Enrolments":
        time_series = df[df['state'] == state].groupby('month')['total_enrolments'].sum().sort_index()
    elif forecast_type == "Demographic Updates":
        time_series = df_demo[df_demo['state'] == state].groupby('month')['total_updates'].sum().sort_index()
    else:
        time_series = df_bio[df_bio['state'] == state].groupby('month')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).sort_index()
    location_name = state
else:  # District
    state = st.sidebar.selectbox("Select State", sorted(df['state'].unique()))
    district = st.sidebar.selectbox(
        "Select District",
        sorted(df[df['state'] == state]['district'].unique())
    )
    if forecast_type == "Enrolments":
        time_series = df[(df['state'] == state) & (df['district'] == district)].groupby('month')['total_enrolments'].sum().sort_index()
    elif forecast_type == "Demographic Updates":
        time_series = df_demo[(df_demo['state'] == state) & (df_demo['district'] == district)].groupby('month')['total_updates'].sum().sort_index()
    else:
        time_series = df_bio[(df_bio['state'] == state) & (df_bio['district'] == district)].groupby('month')['total_updates'].sum().sort_index()
    location_name = f"{district}, {state}"
st.sidebar.subheader("Scenario Forecasting")
optimistic_adjustment = st.sidebar.slider(
    "Optimistic Scenario Adjustment (%)",
    0, 30, 10
)
pessimistic_adjustment = st.sidebar.slider(
    "Pessimistic Scenario Adjustment (%)",
    -30, 0, -10
)
time_series.index = time_series.index.to_timestamp()
if len(time_series) < 3:
    st.error("Insufficient historical data for forecasting. Need at least 3 data points.")
    st.stop()
st.header(f"Forecast for {location_name}")
# Display historical summary
col_sum1, col_sum2, col_sum3 = st.columns(3)
col_sum1.metric("Historical Data Points", len(time_series))
col_sum2.metric("Total Historical Value", f"{time_series.sum():,.0f}")
col_sum3.metric("Average Monthly Value", f"{time_series.mean():,.0f}")
col_met1, col_met2 = st.columns([1,3])
col_met1.metric("Forecast Period", f"{forecast_periods} months")
col_met2.metric("Model Type", "Ensemble")
# Perform forecasting
forecast_result = ensemble_forecast(time_series, periods=forecast_periods)
if 'error' in forecast_result:
    st.error(f"Forecasting error: {forecast_result['error']}")
    st.stop()
baseline_forecast = forecast_result['forecast']
optimistic_forecast = baseline_forecast * (1 + optimistic_adjustment / 100)
pessimistic_forecast = baseline_forecast * (1 + pessimistic_adjustment / 100)
# Generate forecast dates
last_date = time_series.index[-1]
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_periods, freq='MS')
# Create visualization
fig = go.Figure()
# Historical data
fig.add_trace(go.Scatter(
    x=time_series.index,
    y=time_series.values,
    mode='lines+markers',
    name='Historical Data',
    line=dict(color='#1f4ed8', width=2)
))
# Forecast
fig.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_result['forecast'],
    mode='lines+markers',
    name='Forecast',
    line=dict(color='#1f4ed8', width=2, dash='dash')
))
if optimistic_adjustment != 0:
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=optimistic_forecast,
        mode='lines',
        name='Optimistic Scenario',
        line=dict(color='#16a34a', dash='dot')
    ))
if pessimistic_adjustment != 0:
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=pessimistic_forecast,
        mode='lines',
        name='Pessimistic Scenario',
        line=dict(color='#f59e0b', dash='dot')
    ))
# Confidence intervals if available
if 'lower_bound' in forecast_result and 'upper_bound' in forecast_result:
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_result['upper_bound'],
        mode='lines',
        name='Upper Bound (95% CI)',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_result['lower_bound'],
        mode='lines',
        name='Lower Bound (95% CI)',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(31, 78, 216, 0.1)',
        showlegend=True
    ))
fig.update_layout(
    title=f"{forecast_type} Forecast for {location_name}",
    xaxis_title="Date",
    yaxis_title=forecast_type,
    hovermode='x unified',
    height=500
)
st.plotly_chart(fig, use_container_width=True)
col1, col2, col3 = st.columns(3)
col1.metric("Ave Baseline Forecast", f"{forecast_result['forecast'].mean():,.0f}")
if optimistic_adjustment != 0:
    col2.metric("Avg Optimistic Forecast", f"{optimistic_forecast.mean():,.0f}")
if pessimistic_adjustment != 0:
    col3.metric("Avg Pessimistic Forecast", f"{pessimistic_forecast.mean():,.0f}")
if optimistic_adjustment != 0 or pessimistic_adjustment != 0:
    scenario_df = pd.DataFrame({
        "Date": forecast_dates,
        "Baseline Forecast": baseline_forecast,
        "Optimistic Forecast": optimistic_forecast,
        "Pessimistic Forecast": pessimistic_forecast
    })
    st.subheader("Scenario Forecast Comparison")
    st.dataframe(scenario_df, use_container_width=True)
if optimistic_adjustment == 0 and pessimistic_adjustment == 0:
    st.subheader("Forecast Summary")
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast': forecast_result['forecast'],
    })
    if 'lower_bound' in forecast_result:
        forecast_df['Lower Bound'] = forecast_result['lower_bound']
        forecast_df['Upper Bound'] = forecast_result['upper_bound']
    st.dataframe(forecast_df, use_container_width=True)
if len(time_series) >= 6:
    st.subheader("Model Evaluation")
    # Split data for evaluation
    train_size = int(len(time_series) * 0.8)
    train_data = time_series.iloc[:train_size]
    test_data = time_series.iloc[train_size:]
    # Forecast on test period
    eval_forecast = ensemble_forecast(train_data, periods=len(test_data))
    if 'forecast' in eval_forecast:
        accuracy = evaluate_forecast_accuracy(test_data.values, eval_forecast['forecast'])
        col_acc1, col_acc2, col_acc3, col_acc4 = st.columns(4)
        col_acc1.metric("MAE", f"{accuracy['MAE']:,.0f}")
        col_acc2.metric("RMSE", f"{accuracy['RMSE']:,.0f}")
        if not np.isnan(accuracy['MAPE']):
            col_acc3.metric("MAPE", f"{accuracy['MAPE']:.2f}%")
        st.info("**Note:** Lower values indicate better forecast accuracy.")
st.subheader("Forecast Insights")
st.markdown(f"""
- **Forecast Method:** {forecast_result.get('model_type', 'N/A')}
- **Forecast Horizon:** {forecast_periods} periods ahead
- **Trend Direction:** {'Increasing' if forecast_result['forecast'][-1] > time_series.iloc[-1] else 'Decreasing' if forecast_result['forecast'][-1] < time_series.iloc[-1] else 'Stable'}
- **Expected Change:** {((forecast_result['forecast'][-1] / time_series.iloc[-1] - 1) * 100):.2f}% by end of forecast period
""")
if optimistic_adjustment != 0 or pessimistic_adjustment != 0:
    st.subheader("Scenario Implications")
    st.markdown(f"""
    - **Baseline scenario** reflects expected demand based on historical trends.
    - **Optimistic scenario (+{optimistic_adjustment}%)** represents increased enrolment due to outreach, digitisation, or policy push.
    - **Pessimistic scenario ({pessimistic_adjustment}%)** reflects potential slowdowns due to saturation or operational constraints.
    This enables proactive capacity planning under uncertainty.
    """)
st.subheader("Decision Implications")
change_pct = (forecast_result['forecast'][-1] / time_series.iloc[-1] - 1) * 100
if change_pct > 10:
    st.success("High demand growth expected. Consider increasing enrolment/update capacity.")
elif change_pct < -10:
    st.warning("Demand decline expected. Resources may be reallocated.")
else:
    st.info("Stable demand expected. Maintain current capacity.")


