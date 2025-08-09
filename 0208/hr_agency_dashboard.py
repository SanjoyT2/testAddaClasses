import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="HR Agency Analytics Dashboard",
    page_icon="👥",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("👥 HR Agency Analytics Dashboard")
st.markdown("""
This comprehensive dashboard provides insights for HR agencies to optimize recruitment strategies,
analyze market demands, and identify talent opportunities across different locations.
""")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('job_market_unemployment_trends.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar for filtering
st.sidebar.header("Filters")
selected_locations = st.sidebar.multiselect(
    "Select Locations",
    options=sorted(df['location'].unique()),
    default=sorted(df['location'].unique())[:5]
)

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)

# Filter data based on selections
filtered_df = df[
    (df['location'].isin(selected_locations)) &
    (df['date'].dt.date >= selected_date_range[0]) &
    (df['date'].dt.date <= selected_date_range[1])
]

# Top KPI Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_jobs = int(filtered_df['job_postings'].sum())
    st.metric("Total Job Postings", f"{total_jobs:,}", "Active positions")

with col2:
    avg_unemployment = filtered_df['unemployment_rate'].mean()
    st.metric("Average Unemployment Rate", f"{avg_unemployment:.1f}%", "Selected markets")

with col3:
    avg_college_degree = filtered_df['college_degree_percentage'].mean()
    st.metric("Average Education Level", f"{avg_college_degree:.1f}%", "College degree")

with col4:
    total_markets = len(selected_locations)
    st.metric("Markets Analyzed", total_markets, "Active locations")

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "🎯 Skills Analysis", "📈 Trends", "🗺️ Geographic Analysis"])

with tab1:
    st.subheader("Market Overview and Recruitment Opportunities")
    
    # Market dynamics chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Job postings by location
        location_jobs = filtered_df.groupby('location')['job_postings'].mean().sort_values(ascending=True)
        fig_jobs = px.bar(
            location_jobs,
            orientation='h',
            title='Average Job Postings by Location',
            labels={'value': 'Average Job Postings', 'location': 'Location'}
        )
        st.plotly_chart(fig_jobs, use_container_width=True)
    
    with col2:
        # Unemployment vs Job Postings
        fig_scatter = px.scatter(
            filtered_df,
            x='unemployment_rate',
            y='job_postings',
            color='location',
            title='Job Market Balance: Unemployment vs Job Postings',
            labels={'unemployment_rate': 'Unemployment Rate (%)', 'job_postings': 'Number of Job Postings'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("Skills Demand Analysis")
    
    # Skills analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Top skills demand
        all_skills = filtered_df['in_demand_skills'].str.split(',').explode().str.strip()
        top_skills = all_skills.value_counts().head(15)
        
        fig_skills = px.bar(
            top_skills,
            title='Top 15 Most In-Demand Skills',
            labels={'value': 'Number of Job Postings', 'index': 'Skills'}
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    
    with col2:
        # Skills by location
        selected_location = st.selectbox("Select Location for Skills Analysis:", sorted(selected_locations))
        location_skills = filtered_df[filtered_df['location'] == selected_location]['in_demand_skills'].str.split(',').explode().str.strip()
        location_top_skills = location_skills.value_counts().head(10)
        
        fig_loc_skills = px.bar(
            location_top_skills,
            title=f'Top Skills in {selected_location}',
            labels={'value': 'Number of Job Postings', 'index': 'Skills'}
        )
        st.plotly_chart(fig_loc_skills, use_container_width=True)

with tab3:
    st.subheader("Market Trends and Forecasting")
    
    # Time series analysis
    time_series = filtered_df.groupby(['date', 'location'])[['job_postings', 'unemployment_rate']].mean().reset_index()
    
    # Trend visualization
    fig_trend = px.line(
        time_series,
        x='date',
        y='job_postings',
        color='location',
        title='Job Postings Trends Over Time'
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Monthly changes
    monthly_changes = filtered_df.groupby([pd.Grouper(key='date', freq='M'), 'location'])['job_postings'].mean().reset_index()
    monthly_changes['month'] = monthly_changes['date'].dt.strftime('%Y-%m')
    
    fig_monthly = px.bar(
        monthly_changes,
        x='month',
        y='job_postings',
        color='location',
        title='Monthly Job Market Activity'
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

with tab4:
    st.subheader("Geographic Distribution and Market Opportunities")
    
    # Create location summary for map
    location_summary = filtered_df.groupby('location').agg({
        'job_postings': 'mean',
        'unemployment_rate': 'mean',
        'college_degree_percentage': 'mean',
        'in_demand_skills': lambda x: ', '.join(pd.Series(x.str.split(',').explode().str.strip().unique()).head(3))
    }).round(2)

    # City coordinates
    city_coords = {
        'New York': [40.7128, -74.0060],
        'Los Angeles': [34.0522, -118.2437],
        'Chicago': [41.8781, -87.6298],
        'Houston': [29.7604, -95.3698],
        'Phoenix': [33.4484, -112.0740],
        'Philadelphia': [39.9526, -75.1652],
        'San Antonio': [29.4241, -98.4936],
        'San Diego': [32.7157, -117.1611],
        'Dallas': [32.7767, -96.7970],
        'San Jose': [37.3382, -121.8863],
        'Austin': [30.2672, -97.7431],
        'Jacksonville': [30.3322, -81.6557],
        'Fort Worth': [32.7555, -97.3308],
        'Columbus': [39.9612, -82.9988],
        'San Francisco': [37.7749, -122.4194],
        'Charlotte': [35.2271, -80.8431],
        'Indianapolis': [39.7684, -86.1581],
        'Seattle': [47.6062, -122.3321],
        'Denver': [39.7392, -104.9903],
        'Washington': [38.9072, -77.0369]
    }

    # Prepare map data
    map_data = pd.DataFrame({
        'city': list(city_coords.keys()),
        'lat': [coords[0] for coords in city_coords.values()],
        'lon': [coords[1] for coords in city_coords.values()]
    }).merge(location_summary, left_on='city', right_index=True)

    # Create map
    fig_map = px.scatter_mapbox(
        map_data,
        lat='lat',
        lon='lon',
        size='job_postings',
        color='unemployment_rate',
        hover_name='city',
        hover_data=['job_postings', 'unemployment_rate', 'college_degree_percentage', 'in_demand_skills'],
        title='Geographic Market Overview',
        mapbox_style='carto-positron',
        color_continuous_scale='Viridis_r',
        size_max=30,
        zoom=3,
        center={'lat': 39.8283, 'lon': -98.5795}
    )
    st.plotly_chart(fig_map, use_container_width=True)

# Recruitment Strategy Insights
st.markdown("---")
st.subheader("💡 Strategic Insights")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Market Opportunities:
    - High-demand markets with growing job postings
    - Skills gaps in specific locations
    - Educational demographics alignment
    - Emerging industry trends
    """)

with col2:
    st.markdown("""
    #### Recommended Actions:
    1. Focus recruitment efforts in high-opportunity markets
    2. Develop talent pools for in-demand skills
    3. Adjust strategies based on market-specific trends
    4. Target campaigns based on demographic insights
    """)

# Add download capability for reports
st.markdown("---")
st.subheader("📊 Download Reports")

# Generate report data
@st.cache_data
def generate_report_data():
    report_data = {
        'Market Summary': location_summary.to_csv().encode('utf-8'),
        'Skills Analysis': all_skills.value_counts().to_frame().to_csv().encode('utf-8'),
        'Monthly Trends': monthly_changes.to_csv().encode('utf-8')
    }
    return report_data

report_data = generate_report_data()

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        label="Download Market Summary",
        data=report_data['Market Summary'],
        file_name="market_summary.csv",
        mime="text/csv"
    )

with col2:
    st.download_button(
        label="Download Skills Analysis",
        data=report_data['Skills Analysis'],
        file_name="skills_analysis.csv",
        mime="text/csv"
    )

with col3:
    st.download_button(
        label="Download Monthly Trends",
        data=report_data['Monthly Trends'],
        file_name="monthly_trends.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>HR Agency Analytics Dashboard | Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)
