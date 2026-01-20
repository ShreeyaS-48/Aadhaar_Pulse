import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats
from utils.data_loader import load_aadhaar_data
from utils.analytics import (
    univariate_analysis, bivariate_correlation,
)

# Page Config
st.set_page_config(page_title="Comprehensive Analysis", layout="wide", initial_sidebar_state="expanded")

st.title("Comprehensive Analysis")
st.divider()

# Load data
df, df_demo, df_bio = load_aadhaar_data()

# Prepare temporal data
df['month'] = df['date'].dt.to_period('M')
df_demo['month'] = df_demo['date'].dt.to_period('M')
df_bio['month'] = df_bio['date'].dt.to_period('M')

df['month_num'] = df['date'].dt.month
df_demo['month_num'] = df_demo['date'].dt.month
df_bio['month_num'] = df_bio['date'].dt.month

df['weekday'] = df['date'].dt.day_name()
df_demo['weekday'] = df_demo['date'].dt.day_name()
df_bio['weekday'] = df_bio['date'].dt.day_name()

month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

tab1, tab2, tab3 = st.tabs(["Enrolment Analysis", "Demographic Updates", "Biometric Updates"])

def create_trend_analysis(data, data_type_name, value_col, state_col, district_col):
    """Create trend analysis section"""
    col1, col2 = st.columns([3, 1])
    # National Trend
    monthly = data.groupby('month')[value_col].sum().sort_index()
    monthly.index = monthly.index.to_timestamp()
    rolling_avg = monthly.rolling(window=3).mean()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly.index, y=monthly.values,
        name="Monthly Value", mode="lines+markers"
    ))
    fig_trend.add_trace(go.Scatter(
        x=rolling_avg.index, y=rolling_avg.values,
        name="3-Month Avg", mode="lines",
        line=dict(dash="dash", color="#f59e0b")
    ))
    fig_trend.update_layout(
        title=f"National {data_type_name} Trend",
        xaxis_title="Month", yaxis_title=data_type_name,
        hovermode="x unified", height=400
    )
    with col1:
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Month-on-Month Growth
    st.subheader("Month-on-Month Growth")
    mom_growth = monthly.pct_change() * 100
    growth_df = mom_growth.dropna().reset_index()
    growth_df.columns = ["Month", "MoM Growth (%)"]
    
    col_mom1, col_mom2 = st.columns([3, 1])
    
    with col_mom1:
        fig_mom = px.bar(
            growth_df,
            x="Month",
            y="MoM Growth (%)",
            title="Month-on-Month Growth Rate",
            labels={'Month': 'Month', 'MoM Growth (%)': 'Growth %'}
        )
        fig_mom.add_hline(y=0, line_dash="dash", line_color="#dc2626")
        fig_mom.update_xaxes(tickangle=45)
        st.plotly_chart(fig_mom, use_container_width=True)
    
    with col_mom2:
        if len(mom_growth) > 0:
            latest_growth = mom_growth.iloc[-1]
            st.metric("Latest MoM Growth", f"{latest_growth:.1f}%",
                     delta=f"{latest_growth:.1f}%")
            st.metric("Avg MoM Growth", f"{mom_growth.mean():.1f}%")
    
    # Seasonality
    st.subheader("Seasonality Patterns")
    monthly_avg = data.groupby('month_num')[value_col].mean()
    peak_month = month_names[monthly_avg.idxmax() - 1]
    fig_season = px.bar(
        x=[month_names[m-1] for m in monthly_avg.index],
        y=monthly_avg.values,
        title="Average by Month",
        labels={'x': 'Month', 'y': f'Avg {data_type_name}'}
    )
    st.plotly_chart(fig_season, use_container_width=True)
    st.info(f"**Peak Enrolment Month:** {peak_month} (Average: {monthly_avg.max():,.0f})")
    # Geographic Trends
    st.subheader("Geographic Trends")
    # Get geographic data
    state_total = data.groupby(state_col)[value_col].sum().sort_values(ascending=False)
    district_total = data.groupby(district_col)[value_col].sum().sort_values(ascending=False)
    # Metrics row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total States", len(state_total))
    top5_share = (state_total.head(5).sum() / state_total.sum()) * 100
    col_m2.metric("Top 5 States Share", f"{top5_share:.1f}%")
    col_m3.metric("Total Districts", len(district_total))
    top5_dist_share = (district_total.head(5).sum() / district_total.sum()) * 100
    col_m4.metric("Top 5 Districts Share", f"{top5_dist_share:.1f}%")
    
    col_g1, col_g2 = st.columns(2)
    
    # States
    fig_state = px.bar(
        x=state_total.head(15).index, y=state_total.head(15).values,
        title=f"Top 15 States by {data_type_name}",
        labels={'x': 'State', 'y': data_type_name}
    )
    fig_state.update_xaxes(tickangle=45)
    with col_g1:
        st.plotly_chart(fig_state, use_container_width=True)
    
    # Districts
    fig_district = px.bar(
        x=district_total.head(15).index, y=district_total.head(15).values,
        title=f"Top 15 Districts by {data_type_name}",
        labels={'x': 'District', 'y': data_type_name}
    )
    fig_district.update_xaxes(tickangle=45)
    with col_g2:
        st.plotly_chart(fig_district, use_container_width=True)
    
    return monthly, mom_growth
def create_univariate_analysis(data, col_name, var_name):
    """Create univariate analysis section"""
    st.subheader("Statistical Univariate Analysis")   
    # Prepare data
    data_values = data[col_name].dropna()
    data_df = pd.DataFrame({col_name: data_values.values})
    # Perform analysis
    stats_result = univariate_analysis(data_df, col_name)
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean", f"{stats_result['mean']:,.0f}")
    col2.metric("Median", f"{stats_result['median']:,.0f}")
    col3.metric("Std Dev", f"{stats_result['std']:,.0f}")
    col4.metric("CV", f"{stats_result['coefficient_of_variation']:.2f}%")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Min", f"{stats_result['min']:,.0f}")
    col6.metric("Max", f"{stats_result['max']:,.0f}")
    col7.metric("Skewness", f"{stats_result['skewness']:.3f}")
    col8.metric("Kurtosis", f"{stats_result['kurtosis']:.3f}")
    
    # Distribution interpretation
    skew_text = "Right-skewed" if stats_result['skewness'] > 0.5 else \
                "Left-skewed" if stats_result['skewness'] < -0.5 else "Symmetric"
    kurt_text = "Heavy-tailed" if stats_result['kurtosis'] > 0 else "Light-tailed"
    
    st.info(f"**Distribution:** {skew_text}, {kurt_text}")
    
    # Visualizations
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        fig_hist = px.histogram(
            data_df, x=col_name, nbins=50,
            title=f"Distribution of {var_name}",
            labels={col_name: var_name}
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_v2:
        fig_box = px.box(
            data_df, y=col_name,
            title=f"Box Plot: {var_name}",
            labels={col_name: var_name}
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Q-Q Plot
    sample_data = data_values.sample(min(1000, len(data_values)))
    qq_data = scipy_stats.probplot(sample_data, dist="norm")
    
    fig_qq = go.Figure()
    fig_qq.add_trace(go.Scatter(
        x=qq_data[0][0], y=qq_data[0][1],
        mode='markers', name='Sample Quantiles'
    ))
    fig_qq.add_trace(go.Scatter(
        x=qq_data[0][0],
        y=qq_data[1][1] + qq_data[1][0] * qq_data[0][0],
        mode='lines', name='Theoretical'
    ))
    fig_qq.update_layout(
        title="Q-Q Plot (Normality Check)",
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles",
        height=400
    )
    st.plotly_chart(fig_qq, use_container_width=True)

with tab1:
    st.header("Enrolment Analysis")
    
    st.markdown("### Trend")
    monthly_enrol, mom_growth_enrol = create_trend_analysis(
        df, "Total Enrolments", "total_enrolments", "state", "district"
    )
    
    st.divider()
    
    # Advanced Analytics
    analysis_option = st.radio(
        "Analysis Type",
        ["Univariate Analysis", "Bivariate Correlation"],
        horizontal=True, key="enrol_analysis"
    )
    
    if analysis_option == "Univariate Analysis":
        create_univariate_analysis(
            df.groupby('date').agg({
                'total_enrolments': 'sum',
                'age_0_5': 'sum',
                'age_5_17': 'sum',
                'age_18_greater': 'sum'
            }).reset_index(),
            'total_enrolments', 'Daily Enrolments'
        )
    
    elif analysis_option == "Bivariate Correlation":
        st.subheader("Correlation Analysis (Pearson)")
        
        daily_enrol = df.groupby('date').agg({
            'total_enrolments': 'sum',
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum'
        })
        
        col1, col2 = st.columns(2)
        with col1:
            var1 = st.selectbox("Variable 1", 
                              ["Total Enrolments", "Age 0-5", "Age 5-17", "Age 18+"],
                              key="enrol_var1")
        with col2:
            var2 = st.selectbox("Variable 2",
                              ["Age 0-5", "Age 5-17", "Age 18+", "Total Enrolments"],
                              key="enrol_var2")
        
        var_map = {
            "Total Enrolments": "total_enrolments",
            "Age 0-5": "age_0_5",
            "Age 5-17": "age_5_17",
            "Age 18+": "age_18_greater"
        }
        
        corr_data = daily_enrol[[var_map[var1], var_map[var2]]].dropna()
        
        if len(corr_data) >= 3:
            corr_result = bivariate_correlation(
                corr_data, var_map[var1], var_map[var2],
                method="pearson"
            )
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Correlation", f"{corr_result['correlation']:.4f}")
            col_m2.metric("P-value", f"{corr_result['p_value']:.4f}")
            col_m3.metric("Significance", corr_result['significance'])
            
            st.info(f"**Interpretation:** {corr_result['interpretation']}")
            
            fig_scatter = px.scatter(
                corr_data, x=var_map[var1], y=var_map[var2],
                title=f"{var1} vs {var2}", trendline="ols"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.header("Demographic Updates Analysis")
    
    st.markdown("### Trend")
    monthly_demo, mom_growth_demo = create_trend_analysis(
        df_demo, "Demographic Updates", "total_updates", "state", "district"
    )
    
    st.divider()
    
    analysis_option = st.radio(
        "Analysis Type",
        ["Univariate Analysis", "Bivariate Correlation"],
        horizontal=True, key="demo_analysis"
    )
    
    if analysis_option == "Univariate Analysis":
        create_univariate_analysis(
            df_demo.groupby('date').agg({
                'total_updates': 'sum'
            }).reset_index(),
            'total_updates', 'Daily Updates'
        )
    
    elif analysis_option == "Bivariate Correlation":
        st.subheader("Correlation Analysis (Pearson)")
        
        daily_demo = df_demo.groupby('date').agg({
            'total_updates': 'sum',
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum'
        })
        
        col1, col2 = st.columns(2)
        with col1:
            var1 = st.selectbox("Variable 1",
                              ["Total Updates", "Age 5-17 Updates", "Age 17+ Updates"],
                              key="demo_var1")
        with col2:
            var2 = st.selectbox("Variable 2",
                              ["Age 5-17 Updates", "Age 17+ Updates", "Total Updates"],
                              key="demo_var2")
        
        var_map = {
            "Total Updates": "total_updates",
            "Age 5-17 Updates": "demo_age_5_17",
            "Age 17+ Updates": "demo_age_17_"
        }
        
        corr_data = daily_demo[[var_map[var1], var_map[var2]]].dropna()
        
        if len(corr_data) >= 3:
            corr_result = bivariate_correlation(
                corr_data, var_map[var1], var_map[var2],
                method="pearson"
            )
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Correlation", f"{corr_result['correlation']:.4f}")
            col_m2.metric("P-value", f"{corr_result['p_value']:.4f}")
            col_m3.metric("Significance", corr_result['significance'])
            
            st.info(f"**Interpretation:** {corr_result['interpretation']}")
            
            fig_scatter = px.scatter(
                corr_data, x=var_map[var1], y=var_map[var2],
                title=f"{var1} vs {var2}", trendline="ols"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.header("Biometric Updates Analysis")
    
    st.markdown("### Trend")
    monthly_bio, mom_growth_bio = create_trend_analysis(
        df_bio, "Biometric Updates", "total_updates", "state", "district"
    )
    
    st.divider()
    
    analysis_option = st.radio(
        "Analysis Type",
        ["Univariate Analysis", "Bivariate Correlation"],
        horizontal=True, key="bio_analysis"
    )
    
    if analysis_option == "Univariate Analysis":
        create_univariate_analysis(
            df_bio.groupby('date').agg({
                'total_updates': 'sum'
            }).reset_index(),
            'total_updates', 'Daily Updates'
        )
    
    elif analysis_option == "Bivariate Correlation":
        st.subheader("Correlation Analysis (Pearson)")
        
        daily_bio = df_bio.groupby('date').agg({
            'total_updates': 'sum',
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum'
        })
        
        col1, col2 = st.columns(2)
        with col1:
            var1 = st.selectbox("Variable 1",
                              ["Total Updates", "Age 5-17 Updates", "Age 17+ Updates"],
                              key="bio_var1")
        with col2:
            var2 = st.selectbox("Variable 2",
                              ["Age 5-17 Updates", "Age 17+ Updates", "Total Updates"],
                              key="bio_var2")
        
        var_map = {
            "Total Updates": "total_updates",
            "Age 5-17 Updates": "bio_age_5_17",
            "Age 17+ Updates": "bio_age_17_"
        }
        
        corr_data = daily_bio[[var_map[var1], var_map[var2]]].dropna()
        
        if len(corr_data) >= 3:
            corr_result = bivariate_correlation(
                corr_data, var_map[var1], var_map[var2],
                method="pearson"
            )
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Correlation", f"{corr_result['correlation']:.4f}")
            col_m2.metric("P-value", f"{corr_result['p_value']:.4f}")
            col_m3.metric("Significance", corr_result['significance'])
            
            st.info(f"**Interpretation:** {corr_result['interpretation']}")
            
            fig_scatter = px.scatter(
                corr_data, x=var_map[var1], y=var_map[var2],
                title=f"{var1} vs {var2}", trendline="ols"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

