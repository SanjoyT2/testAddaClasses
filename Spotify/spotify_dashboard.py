import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Spotify Listening Analytics Dashboard",
    page_icon="🎵",
    layout="wide"
)

# Add title and description
st.title("🎵 Spotify Listening Analytics Dashboard")
st.markdown("### Record Company Analytics Platform")

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv('spotify_history.csv')
    df['ts'] = pd.to_datetime(df['ts'])
    df['date'] = df['ts'].dt.date
    df['hour'] = df['ts'].dt.hour
    df['day_of_week'] = df['ts'].dt.day_name()
    df['month'] = df['ts'].dt.month_name()
    df['minutes_played'] = df['ms_played'] / (1000 * 60)
    df['hours_played'] = df['minutes_played'] / 60
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["All Time", "Last Month", "Last Week"]
)

# Filter data based on selection
if selected_timeframe != "All Time":
    if selected_timeframe == "Last Month":
        df = df[df['ts'] >= df['ts'].max() - pd.Timedelta(days=30)]
    else:  # Last Week
        df = df[df['ts'] >= df['ts'].max() - pd.Timedelta(days=7)]

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_minutes = df['minutes_played'].sum()
    st.metric("Total Listening Time (hours)", f"{total_minutes/60:.1f}")

with col2:
    total_tracks = len(df)
    st.metric("Total Tracks Played", f"{total_tracks:,}")

with col3:
    unique_artists = df['artist_name'].nunique()
    st.metric("Unique Artists", f"{unique_artists:,}")

with col4:
    avg_duration = df['minutes_played'].mean()
    st.metric("Average Track Duration (min)", f"{avg_duration:.1f}")

# Artist Analysis
st.header("Artist Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top Artists by Playtime
    top_artists = df.groupby('artist_name')['minutes_played'].sum().sort_values(ascending=True).tail(10)
    fig = px.bar(
        x=top_artists.values,
        y=top_artists.index,
        orientation='h',
        title="Top 10 Artists by Listening Time",
        labels={"x": "Minutes Played", "y": "Artist"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Artist Engagement (Skip Rates)
    artist_skips = df.groupby('artist_name').agg({
        'skipped': 'mean',
        'track_name': 'count'
    }).sort_values('track_name', ascending=False)
    artist_skips['skip_rate'] = artist_skips['skipped'] * 100
    artist_skips = artist_skips[artist_skips['track_name'] >= 10]
    
    top_engaging_artists = artist_skips.sort_values('skip_rate').head(10)
    fig = go.Figure(go.Bar(
        x=100 - top_engaging_artists['skip_rate'],
        y=top_engaging_artists.index,
        orientation='h'
    ))
    fig.update_layout(
        title="Top 10 Artists by Engagement Rate",
        xaxis_title="Completion Rate (%)",
        yaxis_title="Artist"
    )
    st.plotly_chart(fig, use_container_width=True)

# Temporal Analysis
st.header("Temporal Analysis")
col1, col2 = st.columns(2)

with col1:
    # Daily listening patterns
    hourly_listening = df.groupby('hour')['minutes_played'].mean()
    fig = px.line(
        x=hourly_listening.index,
        y=hourly_listening.values,
        title="Average Listening Time by Hour",
        labels={"x": "Hour of Day", "y": "Average Minutes Played"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Weekly patterns
    weekly_listening = df.groupby('day_of_week')['minutes_played'].mean()
    weekly_listening = weekly_listening.reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    fig = px.bar(
        x=weekly_listening.index,
        y=weekly_listening.values,
        title="Average Listening Time by Day",
        labels={"x": "Day of Week", "y": "Average Minutes Played"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Platform Analysis
st.header("Platform Analysis")
col1, col2 = st.columns(2)

with col1:
    # Platform distribution
    platform_stats = df['platform'].value_counts()
    fig = px.pie(
        values=platform_stats.values,
        names=platform_stats.index,
        title="Listening Distribution by Platform"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Platform usage by time
    platform_by_hour = pd.crosstab(df['hour'], df['platform'])
    fig = px.area(
        platform_by_hour,
        title="Platform Usage Throughout the Day",
        labels={"index": "Hour of Day", "value": "Number of Tracks"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Track Analysis
st.header("Track Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top tracks
    top_tracks = df.groupby(['track_name', 'artist_name'])['minutes_played'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=top_tracks.values,
        y=[f"{i[0]} - {i[1]}" for i in top_tracks.index],
        orientation='h',
        title="Top 10 Tracks",
        labels={"x": "Minutes Played", "y": "Track - Artist"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Track duration distribution
    fig = px.histogram(
        df,
        x='minutes_played',
        title="Distribution of Track Durations",
        labels={"minutes_played": "Minutes Played", "count": "Number of Tracks"},
        nbins=50
    )
    st.plotly_chart(fig, use_container_width=True)

# User Behavior
st.header("User Behavior Insights")
col1, col2 = st.columns(2)

with col1:
    # Shuffle usage
    shuffle_stats = df['shuffle'].value_counts()
    fig = px.pie(
        values=shuffle_stats.values,
        names=shuffle_stats.index,
        title="Shuffle Mode Usage"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Start reasons
    start_reasons = df['reason_start'].value_counts()
    fig = px.bar(
        x=start_reasons.values,
        y=start_reasons.index,
        orientation='h',
        title="Track Start Reasons",
        labels={"x": "Count", "y": "Reason"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Add footer
st.markdown("---")
st.markdown("Dashboard created for record company analytics using Spotify listening history data")
