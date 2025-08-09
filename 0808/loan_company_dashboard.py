import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set color palette for grey and blue theme
GREY_BLUE_PALETTE = ['#2E4D6B', '#4A90A4', '#6C7B7F', '#8FA4A8', '#B2C4C7', '#D5E0E2']
GREY_BLUE_CONTINUOUS = ['#F5F7FA', '#E8F1F5', '#D5E0E2', '#B2C4C7', '#8FA4A8', '#6C7B7F', '#4A90A4', '#2E4D6B']

# Configure matplotlib and seaborn for grey-blue theme
plt.style.use('default')
sns.set_palette(GREY_BLUE_PALETTE)
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=GREY_BLUE_PALETTE)

# Page configuration
st.set_page_config(
    page_title="Loan Company Analytics Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for grey and blue theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E4D6B;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #6C7B7F, #2E4D6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #F5F7FA;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4A90A4;
    }
    .highlight {
        background-color: #E8F1F5;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #2E4D6B;
    }
    .stSelectbox > div > div {
        background-color: #F5F7FA;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #6C7B7F;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #8FA4A8;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E4D6B !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    """Load and preprocess the financial dataset"""
    try:
        df = pd.read_csv('synthetic_personal_finance_dataset.csv')
        
        # Data preprocessing
        df['record_date'] = pd.to_datetime(df['record_date'])
        
        # Create derived columns
        df['age_group'] = pd.cut(df['age'], 
                                bins=[0, 25, 35, 45, 55, 65, 100], 
                                labels=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
        
        df['income_bracket'] = pd.cut(df['monthly_income_usd'], 
                                     bins=[0, 2000, 4000, 6000, float('inf')], 
                                     labels=['Low (<$2K)', 'Medium ($2K-$4K)', 'High ($4K-$6K)', 'Very High (>$6K)'])
        
        df['expense_ratio'] = (df['monthly_expenses_usd'] / df['monthly_income_usd']) * 100
        df['has_loan_binary'] = df['has_loan'].map({'Yes': 1, 'No': 0})
        
        # Credit score categories
        df['credit_category'] = pd.cut(df['credit_score'], 
                                      bins=[0, 300, 500, 650, 750, 850], 
                                      labels=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'])
        
        # Risk categories based on multiple factors
        def calculate_risk_score(row):
            risk_score = 0
            
            # Credit score component (40% weight)
            if row['credit_score'] < 500:
                risk_score += 40
            elif row['credit_score'] < 650:
                risk_score += 25
            elif row['credit_score'] < 750:
                risk_score += 10
            
            # Debt-to-income ratio component (30% weight)
            if row['debt_to_income_ratio'] > 3:
                risk_score += 30
            elif row['debt_to_income_ratio'] > 1.5:
                risk_score += 20
            elif row['debt_to_income_ratio'] > 0.5:
                risk_score += 10
            
            # Expense ratio component (20% weight)
            if row['expense_ratio'] > 80:
                risk_score += 20
            elif row['expense_ratio'] > 60:
                risk_score += 12
            elif row['expense_ratio'] > 40:
                risk_score += 6
            
            # Savings ratio component (10% weight)
            if row['savings_to_income_ratio'] < 1:
                risk_score += 10
            elif row['savings_to_income_ratio'] < 3:
                risk_score += 5
            
            return risk_score
        
        df['risk_score'] = df.apply(calculate_risk_score, axis=1)
        df['risk_category'] = pd.cut(df['risk_score'], 
                                    bins=[0, 20, 40, 60, 100], 
                                    labels=['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk'])
        
        return df
    except FileNotFoundError:
        st.error("Dataset file not found. Please make sure 'synthetic_personal_finance_dataset.csv' is in the same directory.")
        return None

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🏦 Loan Company Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[df['record_date'].min().date(), df['record_date'].max().date()],
        min_value=df['record_date'].min().date(),
        max_value=df['record_date'].max().date()
    )
    
    # Regional filter
    regions = ['All'] + list(df['region'].unique())
    selected_region = st.sidebar.selectbox("Select Region", regions)
    
    # Age group filter
    age_groups = ['All'] + list(df['age_group'].unique())
    selected_age_group = st.sidebar.selectbox("Select Age Group", age_groups)
    
    # Income bracket filter
    income_brackets = ['All'] + list(df['income_bracket'].unique())
    selected_income = st.sidebar.selectbox("Select Income Bracket", income_brackets)
    
    # Loan status filter
    loan_status = st.sidebar.selectbox("Loan Status", ['All', 'Yes', 'No'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['record_date'].dt.date >= date_range[0]) & 
            (filtered_df['record_date'].dt.date <= date_range[1])
        ]
    
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    if selected_age_group != 'All':
        filtered_df = filtered_df[filtered_df['age_group'] == selected_age_group]
    
    if selected_income != 'All':
        filtered_df = filtered_df[filtered_df['income_bracket'] == selected_income]
    
    if loan_status != 'All':
        filtered_df = filtered_df[filtered_df['has_loan'] == loan_status]
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Executive Summary", 
        "👥 Customer Analysis", 
        "💰 Loan Portfolio", 
        "⚠️ Risk Assessment", 
        "🔥 Correlation Heatmaps",
        "🎯 Loan Recommendations"
    ])
    
    with tab1:
        executive_summary(filtered_df)
    
    with tab2:
        customer_analysis(filtered_df)
    
    with tab3:
        loan_portfolio_analysis(filtered_df)
    
    with tab4:
        risk_assessment(filtered_df)
    
    with tab5:
        correlation_heatmaps(filtered_df)
    
    with tab6:
        loan_recommendations(filtered_df)

def executive_summary(df):
    """Executive summary with key metrics and insights"""
    st.header("📈 Executive Summary")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_customers = len(df)
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        loan_customers = len(df[df['has_loan'] == 'Yes'])
        loan_penetration = (loan_customers / total_customers) * 100 if total_customers > 0 else 0
        st.metric("Loan Customers", f"{loan_customers:,}", f"{loan_penetration:.1f}%")
    
    with col3:
        total_loan_amount = df[df['has_loan'] == 'Yes']['loan_amount_usd'].sum()
        st.metric("Total Loan Portfolio", f"${total_loan_amount/1e6:.1f}M")
    
    with col4:
        avg_credit_score = df['credit_score'].mean()
        st.metric("Avg Credit Score", f"{avg_credit_score:.0f}")
    
    with col5:
        avg_monthly_income = df['monthly_income_usd'].mean()
        st.metric("Avg Monthly Income", f"${avg_monthly_income:,.0f}")
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Loan portfolio by type
        loan_data = df[df['has_loan'] == 'Yes']
        if not loan_data.empty:
            loan_type_dist = loan_data['loan_type'].value_counts()
            fig = px.pie(values=loan_type_dist.values, names=loan_type_dist.index,
                        title="Loan Portfolio Distribution by Type",
                        color_discrete_sequence=GREY_BLUE_PALETTE)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(title_font_color='#2E4D6B', title_font_size=16)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly trend
        monthly_data = df.groupby(df['record_date'].dt.to_period('M')).agg({
            'user_id': 'count',
            'has_loan_binary': 'sum'
        }).reset_index()
        monthly_data['record_date'] = monthly_data['record_date'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_data['record_date'], y=monthly_data['user_id'],
                               mode='lines+markers', name='Total Customers',
                               line=dict(color='#2E4D6B', width=3),
                               marker=dict(color='#2E4D6B', size=6)))
        fig.add_trace(go.Scatter(x=monthly_data['record_date'], y=monthly_data['has_loan_binary'],
                               mode='lines+markers', name='Loan Customers',
                               line=dict(color='#4A90A4', width=3),
                               marker=dict(color='#4A90A4', size=6)))
        fig.update_layout(title="Customer Acquisition Trend", 
                         xaxis_title="Month", 
                         yaxis_title="Count",
                         title_font_color='#2E4D6B',
                         title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown(f"""
        <div class="highlight">
        <strong>Portfolio Highlights:</strong><br>
        • {loan_penetration:.1f}% loan penetration rate<br>
        • Average loan amount: ${df[df['has_loan'] == 'Yes']['loan_amount_usd'].mean():,.0f}<br>
        • Most popular loan type: {df[df['has_loan'] == 'Yes']['loan_type'].mode().iloc[0] if not df[df['has_loan'] == 'Yes'].empty else 'N/A'}<br>
        • Average loan term: {df[df['has_loan'] == 'Yes']['loan_term_months'].mean():.0f} months
        </div>
        """, unsafe_allow_html=True)
    
    with insights_col2:
        high_risk_pct = (df['risk_category'] == 'Very High Risk').mean() * 100
        st.markdown(f"""
        <div class="highlight">
        <strong>Risk Profile:</strong><br>
        • {high_risk_pct:.1f}% high-risk customers<br>
        • Average debt-to-income ratio: {df['debt_to_income_ratio'].mean():.2f}<br>
        • Top region by volume: {df['region'].mode().iloc[0]}<br>
        • Average customer age: {df['age'].mean():.0f} years
        </div>
        """, unsafe_allow_html=True)

def customer_analysis(df):
    """Customer demographics and behavior analysis"""
    st.header("👥 Customer Analysis")
    
    # Demographics overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Age distribution
        age_dist = df['age_group'].value_counts().sort_index()
        fig = px.bar(x=age_dist.index, y=age_dist.values, 
                    title="Customer Distribution by Age Group",
                    color_discrete_sequence=['#2E4D6B'])
        fig.update_layout(xaxis_title="Age Group", yaxis_title="Count",
                         title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Education level
        edu_dist = df['education_level'].value_counts()
        fig = px.pie(values=edu_dist.values, names=edu_dist.index,
                    title="Education Level Distribution",
                    color_discrete_sequence=GREY_BLUE_PALETTE)
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Employment status
        emp_dist = df['employment_status'].value_counts()
        fig = px.bar(x=emp_dist.values, y=emp_dist.index, orientation='h',
                    title="Employment Status Distribution",
                    color_discrete_sequence=['#4A90A4'])
        fig.update_layout(xaxis_title="Count", yaxis_title="Employment Status",
                         title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    # Income and credit analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Income vs Credit Score
        fig = px.scatter(df, x='monthly_income_usd', y='credit_score', 
                        color='has_loan', size='savings_usd',
                        title="Income vs Credit Score by Loan Status",
                        labels={'monthly_income_usd': 'Monthly Income (USD)',
                               'credit_score': 'Credit Score'},
                        color_discrete_map={'Yes': '#2E4D6B', 'No': '#8FA4A8'})
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Regional analysis
        regional_stats = df.groupby('region').agg({
            'monthly_income_usd': 'mean',
            'credit_score': 'mean',
            'has_loan_binary': 'mean'
        }).round(2)
        regional_stats.columns = ['Avg Income', 'Avg Credit Score', 'Loan Rate']
        regional_stats['Loan Rate'] = regional_stats['Loan Rate'] * 100
        
        fig = px.bar(regional_stats.reset_index(), x='region', y='Avg Income',
                    title="Average Income by Region",
                    color_discrete_sequence=['#2E4D6B'])
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer segmentation table
    st.subheader("📊 Customer Segmentation Summary")
    
    segmentation = df.groupby(['age_group', 'income_bracket']).agg({
        'user_id': 'count',
        'has_loan_binary': 'mean',
        'credit_score': 'mean',
        'monthly_income_usd': 'mean'
    }).round(2)
    segmentation.columns = ['Count', 'Loan Rate', 'Avg Credit Score', 'Avg Income']
    segmentation['Loan Rate'] = segmentation['Loan Rate'] * 100
    
    st.dataframe(segmentation.style.format({
        'Count': '{:.0f}',
        'Loan Rate': '{:.1f}%',
        'Avg Credit Score': '{:.0f}',
        'Avg Income': '${:,.0f}'
    }))

def loan_portfolio_analysis(df):
    """Detailed loan portfolio analysis"""
    st.header("💰 Loan Portfolio Analysis")
    
    loan_data = df[df['has_loan'] == 'Yes']
    
    if loan_data.empty:
        st.warning("No loan data available for the selected filters.")
        return
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_portfolio = loan_data['loan_amount_usd'].sum()
        st.metric("Total Portfolio Value", f"${total_portfolio/1e6:.1f}M")
    
    with col2:
        avg_loan_amount = loan_data['loan_amount_usd'].mean()
        st.metric("Average Loan Amount", f"${avg_loan_amount:,.0f}")
    
    with col3:
        avg_interest_rate = loan_data['loan_interest_rate_pct'].mean()
        st.metric("Average Interest Rate", f"{avg_interest_rate:.1f}%")
    
    with col4:
        avg_loan_term = loan_data['loan_term_months'].mean()
        st.metric("Average Loan Term", f"{avg_loan_term:.0f} months")
    
    # Portfolio analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Loan amount distribution
        fig = px.histogram(loan_data, x='loan_amount_usd', nbins=30,
                          title="Loan Amount Distribution")
        fig.update_layout(xaxis_title="Loan Amount (USD)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Interest rate vs loan amount
        fig = px.scatter(loan_data, x='loan_amount_usd', y='loan_interest_rate_pct',
                        color='loan_type', size='loan_term_months',
                        title="Interest Rate vs Loan Amount by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Loan performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # EMI analysis
        fig = px.box(loan_data, x='loan_type', y='monthly_emi_usd',
                    title="Monthly EMI Distribution by Loan Type")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Loan term analysis
        term_analysis = loan_data.groupby('loan_type')['loan_term_months'].mean().reset_index()
        fig = px.bar(term_analysis, x='loan_type', y='loan_term_months',
                    title="Average Loan Term by Type")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed portfolio breakdown
    st.subheader("📊 Portfolio Breakdown by Loan Type")
    
    portfolio_breakdown = loan_data.groupby('loan_type').agg({
        'loan_amount_usd': ['count', 'sum', 'mean'],
        'loan_interest_rate_pct': 'mean',
        'loan_term_months': 'mean',
        'monthly_emi_usd': 'mean'
    }).round(2)
    
    # Flatten column names
    portfolio_breakdown.columns = ['Count', 'Total Amount', 'Avg Amount', 'Avg Interest Rate', 'Avg Term', 'Avg EMI']
    
    st.dataframe(portfolio_breakdown.style.format({
        'Count': '{:.0f}',
        'Total Amount': '${:,.0f}',
        'Avg Amount': '${:,.0f}',
        'Avg Interest Rate': '{:.1f}%',
        'Avg Term': '{:.0f} months',
        'Avg EMI': '${:,.0f}'
    }))

def correlation_heatmaps(df):
    """Correlation analysis with heatmaps using grey-blue color scheme"""
    st.header("🔥 Correlation Analysis & Heatmaps")
    
    # Select numerical columns for correlation analysis
    numerical_cols = ['age', 'monthly_income_usd', 'monthly_expenses_usd', 'savings_usd', 
                     'loan_amount_usd', 'loan_term_months', 'monthly_emi_usd', 
                     'loan_interest_rate_pct', 'debt_to_income_ratio', 'credit_score', 
                     'savings_to_income_ratio', 'expense_ratio', 'risk_score']
    
    # Filter columns that exist in the dataframe
    available_cols = [col for col in numerical_cols if col in df.columns]
    correlation_df = df[available_cols].corr()
    
    # Main correlation heatmap
    st.subheader("📊 Overall Financial Metrics Correlation")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(correlation_df, dtype=bool))
    
    # Create heatmap with grey-blue color scheme
    sns.heatmap(correlation_df, 
                mask=mask,
                annot=True, 
                cmap='Blues_r',
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": .8},
                fmt='.2f',
                annot_kws={'size': 8})
    
    ax.set_title('Financial Metrics Correlation Matrix', fontsize=14, fontweight='bold', color='#2E4D6B')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Key correlations insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 Strong Positive Correlations")
        strong_positive = []
        for i in range(len(correlation_df.columns)):
            for j in range(i+1, len(correlation_df.columns)):
                corr_val = correlation_df.iloc[i, j]
                if corr_val > 0.5:
                    strong_positive.append(f"• {correlation_df.columns[i]} ↔ {correlation_df.columns[j]}: {corr_val:.3f}")
        
        if strong_positive:
            for corr in strong_positive[:5]:  # Show top 5
                st.write(corr)
        else:
            st.write("No strong positive correlations found (>0.5)")
    
    with col2:
        st.markdown("### ⚠️ Strong Negative Correlations")
        strong_negative = []
        for i in range(len(correlation_df.columns)):
            for j in range(i+1, len(correlation_df.columns)):
                corr_val = correlation_df.iloc[i, j]
                if corr_val < -0.3:
                    strong_negative.append(f"• {correlation_df.columns[i]} ↔ {correlation_df.columns[j]}: {corr_val:.3f}")
        
        if strong_negative:
            for corr in strong_negative[:5]:  # Show top 5
                st.write(corr)
        else:
            st.write("No strong negative correlations found (<-0.3)")
    
    # Credit Score Focused Heatmap
    st.subheader("🎯 Credit Score Correlation Focus")
    
    credit_cols = ['credit_score', 'monthly_income_usd', 'savings_usd', 'debt_to_income_ratio', 
                   'expense_ratio', 'savings_to_income_ratio', 'risk_score']
    credit_available_cols = [col for col in credit_cols if col in df.columns]
    credit_corr = df[credit_available_cols].corr()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(credit_corr, 
                annot=True, 
                cmap='RdBu_r',
                center=0,
                square=True,
                linewidths=0.5,
                fmt='.3f',
                annot_kws={'size': 10})
    
    ax.set_title('Credit Score Related Correlations', fontsize=14, fontweight='bold', color='#2E4D6B')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Loan Analysis Heatmap (for customers with loans)
    loan_customers = df[df['has_loan'] == 'Yes']
    if not loan_customers.empty:
        st.subheader("💰 Loan Portfolio Correlation Analysis")
        
        loan_cols = ['loan_amount_usd', 'loan_term_months', 'monthly_emi_usd', 
                     'loan_interest_rate_pct', 'credit_score', 'monthly_income_usd', 
                     'debt_to_income_ratio']
        loan_available_cols = [col for col in loan_cols if col in loan_customers.columns]
        loan_corr = loan_customers[loan_available_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(loan_corr, 
                    annot=True, 
                    cmap='viridis',
                    center=0,
                    square=True,
                    linewidths=0.5,
                    fmt='.3f',
                    annot_kws={'size': 10})
        
        ax.set_title('Loan Portfolio Metrics Correlations', fontsize=14, fontweight='bold', color='#2E4D6B')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Regional Correlation Comparison
    st.subheader("🌍 Regional Correlation Patterns")
    
    regions = df['region'].unique()
    if len(regions) > 1:
        selected_regions = st.multiselect(
            "Select regions to compare correlations:",
            regions,
            default=regions[:2] if len(regions) >= 2 else regions
        )
        
        if len(selected_regions) >= 2:
            fig, axes = plt.subplots(1, len(selected_regions), figsize=(6*len(selected_regions), 5))
            if len(selected_regions) == 1:
                axes = [axes]
            
            key_metrics = ['monthly_income_usd', 'credit_score', 'savings_usd', 'expense_ratio']
            available_metrics = [col for col in key_metrics if col in df.columns]
            
            for idx, region in enumerate(selected_regions):
                region_data = df[df['region'] == region]
                if len(region_data) > 10:  # Only if sufficient data
                    region_corr = region_data[available_metrics].corr()
                    
                    sns.heatmap(region_corr, 
                                annot=True, 
                                cmap='Blues',
                                center=0,
                                square=True,
                                linewidths=0.5,
                                fmt='.2f',
                                ax=axes[idx],
                                annot_kws={'size': 8})
                    
                    axes[idx].set_title(f'{region}', fontweight='bold', color='#2E4D6B')
                    axes[idx].tick_params(axis='x', rotation=45)
                    axes[idx].tick_params(axis='y', rotation=0)
            
            plt.tight_layout()
            st.pyplot(fig)

def risk_assessment(df):
    """Risk assessment and analysis"""
    st.header("⚠️ Risk Assessment")
    
    # Risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        high_risk_count = len(df[df['risk_category'] == 'Very High Risk'])
        high_risk_pct = (high_risk_count / len(df)) * 100
        st.metric("High Risk Customers", f"{high_risk_count:,}", f"{high_risk_pct:.1f}%")
    
    with col2:
        avg_debt_ratio = df['debt_to_income_ratio'].mean()
        st.metric("Avg Debt-to-Income", f"{avg_debt_ratio:.2f}")
    
    with col3:
        low_credit_count = len(df[df['credit_score'] < 500])
        low_credit_pct = (low_credit_count / len(df)) * 100
        st.metric("Poor Credit (<500)", f"{low_credit_count:,}", f"{low_credit_pct:.1f}%")
    
    with col4:
        high_expense_ratio = len(df[df['expense_ratio'] > 80])
        high_expense_pct = (high_expense_ratio / len(df)) * 100
        st.metric("High Expense Ratio (>80%)", f"{high_expense_ratio:,}", f"{high_expense_pct:.1f}%")
    
    # Risk analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk category distribution
        risk_dist = df['risk_category'].value_counts()
        colors = {'Low Risk': '#2E4D6B', 'Medium Risk': '#4A90A4', 
                 'High Risk': '#8FA4A8', 'Very High Risk': '#B2C4C7'}
        fig = px.pie(values=risk_dist.values, names=risk_dist.index,
                    title="Risk Category Distribution",
                    color_discrete_map=colors)
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Credit score distribution
        fig = px.histogram(df, x='credit_score', nbins=30, color='risk_category',
                          title="Credit Score Distribution by Risk Category",
                          color_discrete_map={'Low Risk': '#2E4D6B', 'Medium Risk': '#4A90A4', 
                                            'High Risk': '#8FA4A8', 'Very High Risk': '#B2C4C7'})
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk factors analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Debt-to-income vs Credit Score
        fig = px.scatter(df, x='debt_to_income_ratio', y='credit_score',
                        color='risk_category', size='loan_amount_usd',
                        title="Risk Analysis: Debt-to-Income vs Credit Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk by demographics
        risk_by_age = df.groupby('age_group')['risk_score'].mean().reset_index()
        fig = px.bar(risk_by_age, x='age_group', y='risk_score',
                    title="Average Risk Score by Age Group")
        st.plotly_chart(fig, use_container_width=True)
    
    # High-risk customer analysis
    st.subheader("🔍 High-Risk Customer Analysis")
    
    high_risk_customers = df[df['risk_category'] == 'Very High Risk']
    
    if not high_risk_customers.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**High-Risk Customer Characteristics:**")
            st.write(f"• Average Age: {high_risk_customers['age'].mean():.0f} years")
            st.write(f"• Average Income: ${high_risk_customers['monthly_income_usd'].mean():,.0f}")
            st.write(f"• Average Credit Score: {high_risk_customers['credit_score'].mean():.0f}")
            st.write(f"• Loan Penetration: {(high_risk_customers['has_loan'] == 'Yes').mean()*100:.1f}%")
        
        with col2:
            # Top regions for high-risk customers
            high_risk_regions = high_risk_customers['region'].value_counts().head(5)
            fig = px.bar(x=high_risk_regions.values, y=high_risk_regions.index, orientation='h',
                        title="Top 5 Regions with High-Risk Customers")
            st.plotly_chart(fig, use_container_width=True)

def loan_recommendations(df):
    """Loan recommendations and opportunities"""
    st.header("🎯 Loan Recommendations")
    
    # Potential customers (no current loan)
    potential_customers = df[df['has_loan'] == 'No']
    
    # Scoring for loan recommendations
    def calculate_loan_eligibility_score(row):
        score = 0
        
        # Credit score (40% weight)
        if row['credit_score'] >= 750:
            score += 40
        elif row['credit_score'] >= 650:
            score += 30
        elif row['credit_score'] >= 500:
            score += 15
        
        # Income stability (25% weight)
        if row['monthly_income_usd'] >= 6000:
            score += 25
        elif row['monthly_income_usd'] >= 4000:
            score += 20
        elif row['monthly_income_usd'] >= 2000:
            score += 12
        
        # Savings ratio (20% weight)
        if row['savings_to_income_ratio'] >= 5:
            score += 20
        elif row['savings_to_income_ratio'] >= 3:
            score += 15
        elif row['savings_to_income_ratio'] >= 1:
            score += 8
        
        # Expense management (15% weight)
        if row['expense_ratio'] <= 40:
            score += 15
        elif row['expense_ratio'] <= 60:
            score += 10
        elif row['expense_ratio'] <= 80:
            score += 5
        
        return score
    
    potential_customers = potential_customers.copy()
    potential_customers['loan_eligibility_score'] = potential_customers.apply(calculate_loan_eligibility_score, axis=1)
    potential_customers['eligibility_category'] = pd.cut(potential_customers['loan_eligibility_score'],
                                                        bins=[0, 40, 60, 80, 100],
                                                        labels=['Low', 'Medium', 'High', 'Excellent'])
    
    # Recommendation metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        excellent_prospects = len(potential_customers[potential_customers['eligibility_category'] == 'Excellent'])
        st.metric("Excellent Prospects", f"{excellent_prospects:,}")
    
    with col2:
        high_prospects = len(potential_customers[potential_customers['eligibility_category'] == 'High'])
        st.metric("High-Quality Prospects", f"{high_prospects:,}")
    
    with col3:
        total_potential_value = potential_customers[potential_customers['eligibility_category'].isin(['High', 'Excellent'])]['monthly_income_usd'].sum() * 3  # Estimated loan potential
        st.metric("Potential Loan Value", f"${total_potential_value/1e6:.1f}M")
    
    with col4:
        avg_prospect_income = potential_customers[potential_customers['eligibility_category'].isin(['High', 'Excellent'])]['monthly_income_usd'].mean()
        st.metric("Avg Prospect Income", f"${avg_prospect_income:,.0f}")
    
    # Recommendation analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Eligibility distribution
        eligibility_dist = potential_customers['eligibility_category'].value_counts()
        colors = {'Excellent': '#2E4D6B', 'High': '#4A90A4', 
                 'Medium': '#8FA4A8', 'Low': '#B2C4C7'}
        fig = px.pie(values=eligibility_dist.values, names=eligibility_dist.index,
                    title="Loan Eligibility Distribution",
                    color_discrete_map=colors)
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Prospects by age group
        prospects_by_age = potential_customers[potential_customers['eligibility_category'].isin(['High', 'Excellent'])].groupby('age_group').size().reset_index(name='count')
        fig = px.bar(prospects_by_age, x='age_group', y='count',
                    title="High-Quality Prospects by Age Group",
                    color_discrete_sequence=['#2E4D6B'])
        fig.update_layout(title_font_color='#2E4D6B', title_font_size=16,
                         plot_bgcolor='#F5F7FA')
        st.plotly_chart(fig, use_container_width=True)
    
    # Top prospects table
    st.subheader("🌟 Top Loan Prospects")
    
    top_prospects = potential_customers[potential_customers['eligibility_category'] == 'Excellent'].head(20)
    
    if not top_prospects.empty:
        display_prospects = top_prospects[['user_id', 'age', 'monthly_income_usd', 'credit_score', 
                                         'savings_usd', 'expense_ratio', 'region', 'loan_eligibility_score']].copy()
        display_prospects.columns = ['Customer ID', 'Age', 'Monthly Income', 'Credit Score', 
                                   'Savings', 'Expense Ratio', 'Region', 'Eligibility Score']
        
        st.dataframe(display_prospects.style.format({
            'Monthly Income': '${:,.0f}',
            'Credit Score': '{:.0f}',
            'Savings': '${:,.0f}',
            'Expense Ratio': '{:.1f}%',
            'Eligibility Score': '{:.0f}'
        }))
    
    # Recommended loan products
    st.subheader("💡 Recommended Loan Products by Segment")
    
    recommendations = {
        'High Income (>$6K)': {
            'Products': 'Home Loans, Business Loans',
            'Suggested Amount': '$100K - $500K',
            'Interest Rate': '5% - 8%',
            'Term': '15-30 years'
        },
        'Medium Income ($4K-$6K)': {
            'Products': 'Car Loans, Personal Loans',
            'Suggested Amount': '$20K - $100K',
            'Interest Rate': '8% - 12%',
            'Term': '3-7 years'
        },
        'Young Professionals (<35)': {
            'Products': 'Education Loans, Car Loans',
            'Suggested Amount': '$10K - $50K',
            'Interest Rate': '6% - 10%',
            'Term': '2-5 years'
        },
        'Excellent Credit (>750)': {
            'Products': 'Premium Loans, Low-rate Products',
            'Suggested Amount': '$50K - $300K',
            'Interest Rate': '4% - 7%',
            'Term': '5-20 years'
        }
    }
    
    for segment, details in recommendations.items():
        with st.expander(f"📋 {segment}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Products:** {details['Products']}")
                st.write(f"**Amount Range:** {details['Suggested Amount']}")
            with col2:
                st.write(f"**Interest Rate:** {details['Interest Rate']}")
                st.write(f"**Term:** {details['Term']}")

if __name__ == "__main__":
    main()
