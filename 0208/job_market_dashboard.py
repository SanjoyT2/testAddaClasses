import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Job Market Opportunities Dashboard",
    page_icon="💼",
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
    </style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("🎯 Job Market Opportunities Dashboard")
st.markdown("""
This interactive dashboard helps job seekers identify opportunities across different cities 
and make informed decisions about their job search. Explore the visualizations below to 
understand job market trends, in-demand skills, and opportunities in different locations.
""")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('job_market_unemployment_trends.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

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

# Load the data
df = load_data()

# Calculate key metrics
total_jobs = int(df['job_postings'].mean())
total_cities = len(df['location'].unique())
avg_unemployment = df['unemployment_rate'].mean()

# Display key metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average Job Postings", f"{total_jobs:,}", "per city")
with col2:
    st.metric("Cities Analyzed", total_cities, "major metro areas")
with col3:
    st.metric("Avg Unemployment Rate", f"{avg_unemployment:.1f}%", "nationwide")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["📍 Job Market Map", "📊 City Rankings", "🎯 Skills Analysis"])

with tab1:
    st.subheader("Job Market Opportunities Across Cities")
    
    # Prepare map data
    location_summary = df.groupby('location').agg({
        'job_postings': 'mean',
        'unemployment_rate': 'mean',
        'in_demand_skills': lambda x: ', '.join(pd.Series(x.str.split(',').explode().str.strip().unique()).head(3))
    }).round(2)

    map_data = pd.DataFrame({
        'city': list(city_coords.keys()),
        'lat': [coords[0] for coords in city_coords.values()],
        'lon': [coords[1] for coords in city_coords.values()],
        'job_postings': location_summary['job_postings'],
        'unemployment_rate': location_summary['unemployment_rate'],
        'top_skills': location_summary['in_demand_skills']
    })

    # Create map
    fig_map = px.scatter_mapbox(
        map_data,
        lat='lat',
        lon='lon',
        size='job_postings',
        color='unemployment_rate',
        hover_name='city',
        hover_data=['job_postings', 'unemployment_rate', 'top_skills'],
        title='Job Market Opportunities',
        mapbox_style='carto-positron',
        color_continuous_scale='Viridis_r',
        size_max=30,
        zoom=3,
        center={'lat': 39.8283, 'lon': -98.5795}
    )
    fig_map.update_layout(height=600)
    st.plotly_chart(fig_map, use_container_width=True)

with tab2:
    st.subheader("City Opportunity Rankings")
    
    # Calculate opportunity scores
    metrics = location_summary[['job_postings', 'unemployment_rate']].copy()
    scaler = MinMaxScaler()
    metrics['job_postings_scaled'] = scaler.fit_transform(metrics[['job_postings']])
    metrics['unemployment_rate_scaled'] = 1 - scaler.fit_transform(metrics[['unemployment_rate']])
    metrics['opportunity_score'] = (metrics['job_postings_scaled'] + metrics['unemployment_rate_scaled']) / 2 * 100

    # Create opportunity score chart
    fig_scores = px.bar(
        metrics.sort_values('opportunity_score', ascending=True),
        y=metrics.index,
        x='opportunity_score',
        title='Job Market Opportunity Score by City',
        labels={'opportunity_score': 'Opportunity Score (0-100)', 'index': 'City'},
        color='opportunity_score',
        color_continuous_scale='Viridis',
        orientation='h'
    )
    fig_scores.update_layout(height=600)
    st.plotly_chart(fig_scores, use_container_width=True)

with tab3:
    st.subheader("In-Demand Skills Analysis")
    
    # Prepare skills data
    skills_data = df['in_demand_skills'].str.split(',').explode().str.strip().value_counts().reset_index()
    skills_data.columns = ['skill', 'count']
    skills_data['percentage'] = (skills_data['count'] / len(df) * 100).round(1)

    # Create skills treemap
    fig_skills = px.treemap(
        skills_data.head(20),
        path=['skill'],
        values='count',
        title='Most In-Demand Skills',
        custom_data=['percentage']
    )
    fig_skills.update_traces(
        textinfo='label+percent entry',
        hovertemplate='<b>%{label}</b><br>Demanded in %{customdata[0]:.1f}% of job postings<extra></extra>'
    )
    fig_skills.update_layout(height=500)
    st.plotly_chart(fig_skills, use_container_width=True)

    # Display top skills by city
    st.subheader("Top Skills by City")
    selected_city = st.selectbox("Select a city:", sorted(df['location'].unique()))
    
    city_skills = df[df['location'] == selected_city]['in_demand_skills'].str.split(',').explode().str.strip()
    city_skills = city_skills.value_counts().head(10)
    
    fig_city_skills = px.bar(
        x=city_skills.values,
        y=city_skills.index,
        orientation='h',
        title=f'Top 10 In-Demand Skills in {selected_city}',
        labels={'x': 'Number of Job Postings', 'y': 'Skill'}
    )
    st.plotly_chart(fig_city_skills, use_container_width=True)

# Add insights and tips section
st.markdown("---")
st.subheader("💡 Tips for Success")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Key Insights:
    - Focus on developing the most in-demand skills
    - Consider cities with high opportunity scores
    - Look for growing job markets
    - Network with professionals in your target cities
    """)

with col2:
    st.markdown("""
    #### Next Steps:
    1. Research specific companies in your target cities
    2. Update your skills based on local demand
    3. Set up job alerts for your preferred locations
    4. Connect with local professional groups
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Created with ❤️ for job seekers | Data updated: 2025</p>
</div>
""", unsafe_allow_html=True)
