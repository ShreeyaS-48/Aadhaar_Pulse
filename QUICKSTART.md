# Quick Start Guide

## Installation in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Data Files
Ensure the following files are in the `data/` directory:
- `api_data_aadhar_enrolment_*.csv` (3 files)
- `api_data_aadhar_demographic_*.csv` (5 files)
- `api_data_aadhar_biometric_*.csv` (4 files)


### Step 3: Run the Application
```bash
streamlit run Aadhaar_Pulse.py
```

The application will open automatically in your browser at `http://localhost:8501`

## First-Time User Guide

### Recommended Navigation Path

1. **Start Here:** Open `Aadhaar_Pulse.py` (Home page)
   - Read the introduction
   - Understand the platform capabilities

2. **Explore Core Data:** Navigate to `1_Enrolment_Overview`
   - View national statistics
   - Understand overall patterns

3. **Drill Down:** Go to `2_Enrolment_State_Drilldown`
   - Select a state from sidebar
   - Explore state-specific insights

4. **Advanced Analysis:** Try `10_Advanced_Analytics`
   - Start with Univariate Analysis
   - Explore Bivariate correlations
   - Try Trivariate analysis

5. **Detect Anomalies:** Check `11_Anomaly_Detection`
   - Use Isolation Forest method
   - Identify at-risk states/districts

6. **Forecast Trends:** Use `12_Predictive_Analytics`
   - Select National level
   - Choose Ensemble forecasting
   - View forecast for next 3 months

7. **Societal Insights:** Explore `13_Societal_Trends`
   - Geographic Patterns
   - Temporal Trends
   - Digital Inclusion indicators

## Key Features to Explore

### Advanced Analytics
- **Univariate:** Distribution analysis with Q-Q plots
- **Bivariate:** Correlation analysis with scatter plots
- **Trivariate:** 3D scatter plots with partial correlations

### Anomaly Detection
- **Isolation Forest:** ML-based anomaly detection
- **Statistical Methods:** IQR and Z-Score based detection
- **Risk Assessment:** Comparative analysis against benchmarks

### Predictive Analytics
- **Multiple Methods:** Linear, MA, Exponential Smoothing, Ensemble
- **Model Evaluation:** Accuracy metrics (MAE, RMSE, MAPE)
- **Forecast Visualization:** Interactive time series plots

### Societal Trends
- **Geographic Patterns:** State-wise distribution analysis
- **Temporal Trends:** Seasonality and growth patterns
- **Digital Inclusion:** Update activity as engagement proxy

## Troubleshooting

### Issue: "Module not found"
**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Data file not found"
**Solution:** Verify all CSV and Excel files are in the `data/` directory

### Issue: "Forecast not working"
**Solution:** Ensure at least 3 data points are available for the selected level

### Issue: "Slow loading"
**Solution:** The first load caches data. Subsequent loads will be faster.

## Performance Tips

1. **First Load:** May take 30-60 seconds to load and cache data
2. **Subsequent Loads:** Much faster due to Streamlit caching
3. **Large Datasets:** The app handles millions of records efficiently

## Getting Help

- Check the comprehensive `README.md` for detailed documentation
- Review code comments in utility modules
- Explore each page's help text and captions

## Next Steps

After exploring the platform:
1. Try different analysis combinations
2. Export insights for your use case
3. Customize visualizations as needed
4. Use forecasts for planning purposes

---

**Happy analyzing.**


