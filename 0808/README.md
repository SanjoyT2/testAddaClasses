# 🏦 Loan Company Analytics Dashboard

A comprehensive interactive dashboard built with Streamlit for loan companies to analyze customer data, assess risk, and identify loan opportunities.

## 📊 Dashboard Features

### 1. Executive Summary
- Key performance metrics (total customers, loan penetration, portfolio value)
- Loan portfolio distribution by type
- Monthly customer acquisition trends
- High-level insights and highlights

### 2. Customer Analysis
- Demographic breakdowns (age, education, employment)
- Income vs credit score analysis
- Regional customer distribution
- Customer segmentation summary

### 3. Loan Portfolio Analysis
- Portfolio metrics and performance indicators
- Loan amount and interest rate distributions
- EMI analysis by loan type
- Detailed portfolio breakdown

### 4. Risk Assessment
- Risk category distribution and metrics
- Credit score analysis
- Risk factors correlation analysis
- High-risk customer profiling

### 5. Loan Recommendations
- Loan eligibility scoring for potential customers
- Top prospects identification
- Recommended loan products by customer segment
- Growth opportunity analysis

## 🚀 How to Run the Dashboard

### Method 1: Using the Batch File (Windows)
1. Double-click `run_dashboard.bat`
2. Wait for installation to complete
3. The dashboard will open automatically in your browser

### Method 2: Manual Installation
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the dashboard:
   ```bash
   streamlit run loan_company_dashboard.py
   ```

3. Open your browser and go to: `http://localhost:8501`

## 📋 Requirements

- Python 3.7 or higher
- Required packages (automatically installed):
  - streamlit
  - pandas
  - numpy
  - plotly
  - seaborn
  - matplotlib

## 📁 File Structure

```
├── loan_company_dashboard.py      # Main dashboard application
├── synthetic_personal_finance_dataset.csv  # Data source
├── requirements.txt               # Python dependencies
├── run_dashboard.bat             # Windows batch file to run dashboard
└── README.md                     # This file
```

## 🎯 Dashboard Capabilities

### Interactive Filters
- Date range selection
- Regional filtering
- Age group filtering
- Income bracket filtering
- Loan status filtering

### Key Metrics Tracked
- **Customer Metrics**: Total customers, demographics, regional distribution
- **Loan Metrics**: Portfolio value, penetration rates, average amounts
- **Risk Metrics**: Credit scores, debt-to-income ratios, risk categories
- **Performance Metrics**: EMI amounts, interest rates, loan terms

### Advanced Analytics
- **Risk Scoring**: Multi-factor risk assessment algorithm
- **Eligibility Scoring**: Loan recommendation scoring system
- **Customer Segmentation**: Demographic and financial profiling
- **Trend Analysis**: Time-based performance tracking

## 💡 Business Use Cases

1. **Loan Origination**: Identify and qualify potential borrowers
2. **Risk Management**: Monitor and assess portfolio risk
3. **Customer Segmentation**: Target specific customer groups
4. **Performance Monitoring**: Track key business metrics
5. **Strategic Planning**: Data-driven decision making

## 🔧 Customization

The dashboard can be customized by modifying:
- Risk scoring algorithms in the `calculate_risk_score()` function
- Loan eligibility criteria in the `calculate_loan_eligibility_score()` function
- Visual themes and layouts in the Streamlit configuration
- Additional metrics and KPIs as needed

## 📞 Support

For technical support or feature requests, please refer to the Streamlit documentation or modify the code as needed for your specific requirements.

---

**Built with ❤️ using Streamlit and Python**
