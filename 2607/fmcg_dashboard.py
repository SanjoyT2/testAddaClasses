import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="FMCG Sales Dashboard", layout="wide")

# Title
st.title("FMCG Sales Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('FMCG_2022_2024_cleaned.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['date'].min(), df['date'].max()],
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

# Category filter
categories = ['All'] + list(df['category'].unique())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Brand filter
brands = ['All'] + list(df['brand'].unique())
selected_brand = st.sidebar.selectbox("Select Brand", brands)

# Filter data based on selections
mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
if selected_category != 'All':
    mask &= (df['category'] == selected_category)
if selected_brand != 'All':
    mask &= (df['brand'] == selected_brand)
filtered_df = df[mask]

# Main dashboard
# Row 1: Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sales", f"{filtered_df['units_sold'].sum():,.0f}")
with col2:
    st.metric("Average Daily Sales", f"{filtered_df.groupby('date')['units_sold'].sum().mean():,.0f}")
with col3:
    st.metric("Total Revenue", f"${(filtered_df['units_sold'] * filtered_df['price_unit']).sum():,.2f}")
with col4:
    st.metric("Number of Products", f"{filtered_df['sku'].nunique():,}")

# Row 2: Sales Trends
st.subheader("Sales Trends")
col1, col2 = st.columns(2)

with col1:
    # Daily sales trend
    daily_sales = filtered_df.groupby('date')['units_sold'].sum().reset_index()
    fig = px.line(daily_sales, x='date', y='units_sold', title='Daily Sales Trend')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Monthly sales trend
    monthly_sales = filtered_df.groupby(filtered_df['date'].dt.strftime('%Y-%m'))['units_sold'].sum().reset_index()
    fig = px.bar(monthly_sales, x='date', y='units_sold', title='Monthly Sales Distribution')
    st.plotly_chart(fig, use_container_width=True)

# Row 3: Product Performance
st.subheader("Product Performance Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top 10 products by sales
    top_products = filtered_df.groupby('sku')['units_sold'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(top_products, title='Top 10 Products by Sales')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Sales by category
    category_sales = filtered_df.groupby('category')['units_sold'].sum().sort_values(ascending=False)
    fig = px.pie(values=category_sales.values, names=category_sales.index, title='Sales Distribution by Category')
    st.plotly_chart(fig, use_container_width=True)

# Row 4: Channel and Regional Analysis
st.subheader("Distribution Analysis")
col1, col2 = st.columns(2)

with col1:
    # Sales by channel
    channel_sales = filtered_df.groupby('channel')['units_sold'].sum().sort_values(ascending=False)
    fig = px.bar(channel_sales, title='Sales by Channel')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Sales by region
    region_sales = filtered_df.groupby('region')['units_sold'].sum().sort_values(ascending=False)
    fig = px.bar(region_sales, title='Sales by Region')
    st.plotly_chart(fig, use_container_width=True)

# Row 5: Promotion Impact
st.subheader("Promotion Impact Analysis")
col1, col2 = st.columns(2)

with col1:
    # Average sales with/without promotion
    promo_impact = filtered_df.groupby('promotion_flag')['units_sold'].mean().reset_index()
    fig = px.bar(promo_impact, x='promotion_flag', y='units_sold', 
                 title='Average Sales: Promoted vs Non-Promoted Products')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Promotion success rate by category
    promo_category = filtered_df.pivot_table(
        index='category', 
        columns='promotion_flag',
        values='units_sold',
        aggfunc='mean'
    ).fillna(0)
    
    # Get the unique promotion flag values
    promo_flags = sorted(filtered_df['promotion_flag'].unique())
    if len(promo_flags) >= 2:
        promoted = promo_flags[-1]  # Assuming higher value means promoted
        not_promoted = promo_flags[0]  # Assuming lower value means not promoted
        
        # Calculate promotion success rate
        promo_success = ((promo_category[promoted] - promo_category[not_promoted]) / 
                        promo_category[not_promoted] * 100).fillna(0)
        
        fig = px.bar(
            x=promo_success.index,
            y=promo_success.values,
            title='Promotion Success Rate by Category (%)'
        )
        fig.update_layout(xaxis_title='Category', yaxis_title='Success Rate (%)')
    else:
        st.write("Insufficient promotion data to calculate success rate")

# Row 6: Price Analysis
st.subheader("Price Analysis")
col1, col2 = st.columns(2)

with col1:
    # Price vs Sales correlation
    fig = px.scatter(filtered_df, x='price_unit', y='units_sold', title='Price vs Sales Correlation')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Average price by category
    avg_price = filtered_df.groupby('category')['price_unit'].mean().sort_values(ascending=True)
    fig = px.bar(avg_price, title='Average Price by Category')
    st.plotly_chart(fig, use_container_width=True)

# Row 7: Recommendations
st.subheader("Product Recommendations")
col1, col2 = st.columns(2)

with col1:
    # Best performing products
    best_products = filtered_df.groupby('sku').agg({
        'units_sold': 'sum',
        'price_unit': 'mean'
    }).sort_values('units_sold', ascending=False).head(5)
    
    st.write("Top 5 Best Performing Products:")
    st.dataframe(best_products)

with col2:
    # Products with highest revenue
    filtered_df['revenue'] = filtered_df['units_sold'] * filtered_df['price_unit']
    top_revenue = filtered_df.groupby('sku')['revenue'].sum().sort_values(ascending=False).head(5)
    
    st.write("Top 5 Products by Revenue:")
    st.dataframe(top_revenue)

# Add a download button for the filtered data
st.sidebar.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name="filtered_fmcg_data.csv",
    mime="text/csv"
)
