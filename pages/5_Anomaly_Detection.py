import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_aadhaar_data
from utils.analytics import (
    detect_anomalies_isolation_forest
)

st.set_page_config(page_title="Anomaly Detection", layout="wide", initial_sidebar_state="expanded")
st.title("Anomaly Detection and Risk Assessment")
st.markdown("**Identify outliers, anomalies, and potential risk patterns in Aadhaar enrolment and update data**")
st.divider()

[df, df_demo, df_bio] = load_aadhaar_data()

# Sidebar configuration
st.sidebar.header("Detection Configuration")
contamination = st.sidebar.slider("Expected Anomaly Rate", 0.05, 0.3, 0.1, 0.05)

analysis_level = st.sidebar.selectbox(
    "Analysis Level",
    ["State Level", "District Level", "Temporal (Daily)"]
)

st.header("Isolation Forest Anomaly Detection")
if analysis_level == "State Level":
    state_data = df.groupby('state').agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()

    state_data['child_ratio'] = (
        state_data['age_0_5'] + state_data['age_5_17']
    ) / state_data['total_enrolments']
    
    # Detect anomalies
    anomaly_df = detect_anomalies_isolation_forest(
        state_data,
        ['total_enrolments', 'child_ratio'],
        contamination=contamination
    )
    
    anomalies = anomaly_df[anomaly_df['is_anomaly'] == True]

    st.subheader("Detected Anomalies")
    st.metric("Number of Anomalous States", len(anomalies))

    if len(anomalies) > 0:
        st.dataframe(
            anomalies[['state', 'total_enrolments', 'child_ratio']],
            use_container_width=True
        )

        # Visualization
        fig = px.scatter(
            anomaly_df,
            x='total_enrolments',
            y='child_ratio',
            color='is_anomaly',
            hover_data=['state', 'total_enrolments'],
            title="Anomaly Detection: State-level Patterns",
            labels={
                'total_enrolments': 'Total Enrolments',
                'child_ratio': 'Child Enrolment Ratio',
                'is_anomaly': 'Anomaly'
            },
            color_discrete_map={True: '#dc2626', False: '#1f4ed8'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No anomalies detected at this contamination level.")

elif analysis_level == "District Level":
    district_data = df.groupby(['state', 'district']).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    district_data['child_ratio'] = (
        (district_data['age_0_5'] + district_data['age_5_17']) / 
        district_data['total_enrolments']
    )
    
    anomaly_df = detect_anomalies_isolation_forest(
        district_data,
        ['total_enrolments', 'child_ratio'],
        contamination=contamination
    )
    
    anomalies = anomaly_df[anomaly_df['is_anomaly'] == True]

    st.subheader("Detected Anomalies")
    st.metric("Number of Anomalous Districts", len(anomalies))

    if len(anomalies) > 0:
        st.dataframe(
            anomalies[['state', 'district', 'total_enrolments', 'child_ratio']].head(20),
            use_container_width=True
        )

else:  # Temporal
    daily_data = df.groupby('date').agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    daily_data['child_ratio'] = (
        (daily_data['age_0_5'] + daily_data['age_5_17']) / 
        daily_data['total_enrolments']
    )
    daily_data['day_of_week'] = pd.to_datetime(daily_data['date']).dt.dayofweek
    
    anomaly_df = detect_anomalies_isolation_forest(
        daily_data,
        ['total_enrolments', 'child_ratio'],
        contamination=contamination
    )
    
    anomalies = anomaly_df[anomaly_df['is_anomaly'] == True]

    st.subheader("Detected Anomalies")
    st.metric("Number of Anomalous Days", len(anomalies))

    if len(anomalies) > 0:
        # Plot using anomaly_df which contains is_anomaly flag
        fig = px.scatter(
            anomaly_df,
            x='date',
            y='total_enrolments',
            color='is_anomaly',
            title="Temporal Anomaly Detection",
            labels={'total_enrolments': 'Total Enrolments', 'date': 'Date'},
            color_discrete_map={True: '#dc2626', False: '#1f4ed8'}
        )
        st.plotly_chart(fig, use_container_width=True)
