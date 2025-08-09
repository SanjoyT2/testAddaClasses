import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Telco Customer Churn Analysis", layout="wide")

# Title and description
st.title("Telco Customer Churn Analysis Dashboard")
st.markdown("This dashboard provides insights into customer churn patterns and risk factors.")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')
    # Convert TotalCharges to numeric
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].str.strip(), errors='coerce')
    return df

df = load_data()

# Sidebar for filtering
st.sidebar.header("Filters")
contract_filter = st.sidebar.multiselect(
    "Select Contract Type",
    options=df['Contract'].unique(),
    default=df['Contract'].unique()
)

internet_filter = st.sidebar.multiselect(
    "Select Internet Service",
    options=df['InternetService'].unique(),
    default=df['InternetService'].unique()
)

# Filter the dataframe
filtered_df = df[
    (df['Contract'].isin(contract_filter)) &
    (df['InternetService'].isin(internet_filter))
]

# Main dashboard content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Overall Churn Rate")
    churn_rate = filtered_df['Churn'].value_counts(normalize=True).mul(100).round(2)
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.pie(churn_rate, labels=churn_rate.index, autopct='%1.1f%%')
    plt.title('Customer Churn Distribution')
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Churn by Contract Type")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(data=filtered_df, x='Contract', hue='Churn')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

# Demographics Analysis
st.header("Demographics Analysis")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Churn by Senior Citizen Status")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(data=filtered_df, x='SeniorCitizen', hue='Churn')
    plt.title('Churn Distribution by Senior Citizen Status')
    st.pyplot(fig)
    plt.close()

with col4:
    st.subheader("Average Monthly Charges by Demographics")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=filtered_df, x='SeniorCitizen', y='MonthlyCharges', hue='Churn')
    plt.title('Monthly Charges by Senior Citizen Status and Churn')
    st.pyplot(fig)
    plt.close()

# Services Analysis
st.header("Services Analysis")
col5, col6 = st.columns(2)

with col5:
    st.subheader("Internet Service Distribution")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(data=filtered_df, x='InternetService', hue='Churn')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

with col6:
    st.subheader("Additional Services Impact")
    services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
    service_churn = []
    for service in services:
        churn_rate = filtered_df[filtered_df[service]=='Yes']['Churn'].value_counts(normalize=True)
        if 'Yes' in churn_rate:
            service_churn.append({'Service': service, 'Churn Rate': churn_rate['Yes']*100})
    
    service_churn_df = pd.DataFrame(service_churn)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=service_churn_df, x='Service', y='Churn Rate')
    plt.xticks(rotation=45)
    plt.title('Churn Rate by Additional Services')
    st.pyplot(fig)
    plt.close()

# Key Metrics
st.header("Key Metrics")
col7, col8, col9 = st.columns(3)

with col7:
    avg_monthly = filtered_df['MonthlyCharges'].mean()
    st.metric("Average Monthly Charges", f"${avg_monthly:.2f}")

with col8:
    avg_tenure = filtered_df['tenure'].mean()
    st.metric("Average Tenure (months)", f"{avg_tenure:.1f}")

with col9:
    churn_count = filtered_df['Churn'].value_counts()
    churn_rate = (churn_count['Yes'] / len(filtered_df)) * 100
    st.metric("Overall Churn Rate", f"{churn_rate:.1f}%")

# Detailed Data View
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.dataframe(filtered_df)
