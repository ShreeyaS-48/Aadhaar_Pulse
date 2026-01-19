"""
Aadhaar Enrolment & Update Intelligence System
Comprehensive analytics platform for Aadhaar data analysis
"""

import streamlit as st

st.set_page_config(
    page_title="Aadhaar Pulse",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced professional styling
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1f4ed8;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    /* Tagline */
    .tagline {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Hero Section */
    .hero-section {
        padding: 2rem;
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 2px solid #1f4ed8;
    }
    
    .hero-text {
        color: #1f2937;
        font-size: 1.1rem;
        line-height: 1.7;
        margin-bottom: 0;
    }
    
    /* Feature Cards */
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .feature-card:hover {
        border-color: #1f4ed8;
        box-shadow: 0 4px 12px rgba(31, 78, 216, 0.15);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #1f4ed8;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1f4ed8;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        color: #6b7280;
        line-height: 1.6;
    }
    
    /* Section Header */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
    }
    
    /* Capability Box */
    .capability-box {
        background-color: #f9fafb;
        padding: 1.2rem;
        border-radius: 8px;
        border: 2px solid #1f4ed8;
        margin-bottom: 0.8rem;
    }
    
    .capability-title {
        font-weight: 600;
        color: #1f4ed8;
        margin-bottom: 0.3rem;
    }
    
    .capability-text {
        color: #6b7280;
        font-size: 0.95rem;
    }
    
    /* CTA Section */
    .cta-section {
        background: linear-gradient(135deg, #1f4ed8 0%, #1e40af 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .cta-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .cta-text {
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background-color: #f0f4f8;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #1f4ed8;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #1f4ed8;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Footer */
    .footer-section {
        background-color: #f9fafb;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
    }
    
    .footer-title {
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .footer-text {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">Aadhaar Pulse</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Data-Driven Insights for Enrolment, Updates & Planning</p>', unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <p class="hero-text">
        <strong>Aadhaar Pulse</strong> is a platform that transforms raw Aadhaar data into 
        actionable insights. Leveraging advanced analytics, predictive modeling, and anomaly detection, we empower 
        policymakers and administrators to make data-driven decisions with confidence.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Platform Capabilities Section
st.markdown('<h2 class="section-header">Platform Capabilities</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="capability-box">
        <div class="capability-title">Comprehensive Analysis</div>
        <div class="capability-text">
            Multi-dimensional analysis across enrolment, demographic updates, and biometric trends 
            with state and district-level drilldown capabilities.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="capability-box">
        <div class="capability-title">Predictive Analytics</div>
        <div class="capability-text">
            Advanced time-series forecasting with ensemble methods, scenario analysis, and confidence intervals 
            for accurate future trend predictions.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="capability-box">
        <div class="capability-title">Anomaly Detection</div>
        <div class="capability-text">
            Isolation Forest-based anomaly detection at state, district, and temporal levels to identify 
            outliers and potential risk patterns in real-time.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="capability-box">
        <div class="capability-title">Trend Analysis</div>
        <div class="capability-text">
            Deep insights into historical trends, growth rates, seasonal patterns, and comparative metrics 
            across geographic regions and demographic segments.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Call to Action Section
st.markdown("""
<div class="cta-section">
    <div class="cta-title">Get Started Today</div>
    <div class="cta-text">
        Select an analysis page from the sidebar to explore deep insights into Aadhaar enrolment and update patterns
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer-section">
    <div class="footer-title">Data Sources</div>
    <div class="footer-text">
        <strong>Data Sources:</strong> UIDAI Aadhaar Enrolment Dataset | UIDAI Aadhaar Demographic Update Dataset | UIDAI Aadhaar Biometric Update Dataset
    </div>
    <div class="footer-text">
        <strong>Intended Users:</strong> Policymakers | UIDAI Officials | State & District Administrators | Researchers & Analysts
    </div>
</div>
""", unsafe_allow_html=True)
