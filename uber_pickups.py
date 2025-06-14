import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
print("Hello Worlds")
# Set page config
st.set_page_config(page_title="Signup Analysis", layout="wide")

# Add custom CSS for sticky header (dark theme compatible)
st.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
            position: sticky;
            top: 0;
            background-color: #0e1117; /* Streamlit dark theme background */
            z-index: 999;
            padding: 1rem 0;
            border-bottom: 1px solid #333;
        }
        .stSelectbox {
            background-color: #262730 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Read the CSV file
@st.cache_data
def load_data():
    print("Starting to load data...")
    # Read CSV without header and assign column names
    df = pd.read_csv('signers.csv', header=None, 
                     names=['id', 'status', 'organization', 'language', 'zipcode', 'signup_date'])
    
    print("CSV loaded. First few rows:")
    print(df.head())
    print("\nColumn names:", df.columns.tolist())
    
    # Filter out rows where signup_date doesn't match the expected format
    def is_valid_date(date_str):
        try:
            pd.to_datetime(date_str, format='%m/%d/%Y %H:%M')
            return True
        except:
            return False
    
    # Filter the dataframe
    df = df[df['signup_date'].apply(is_valid_date)]
    print(f"\nFiltered out {len(df)} valid rows")
    
    # Convert signup_date to datetime with explicit format
    df['signup_date'] = pd.to_datetime(df['signup_date'], format='%m/%d/%Y %H:%M')
    print("\nSuccessfully converted dates")
    
    # Extract month and year
    df['month_year'] = df['signup_date'].dt.to_period('M')
    return df

# Load the data
print("About to load data...")
df = load_data()
print("Data loaded successfully!")

# Title
st.title("Signup Analysis Dashboard")

# Sticky organization selector
organizations = ['All Organizations'] + sorted(df['organization'].unique().tolist())
selected_org = st.selectbox('Select Organization', organizations)

# Filter data based on selected organization
if selected_org != 'All Organizations':
    filtered_df = df[df['organization'] == selected_org]
else:
    filtered_df = df

# View Type Toggle (now in scroll area)
st.write("")  # Spacer for visual separation
view_type = st.radio("Select View Type", ["Regular", "Cumulative"], horizontal=True)

# Monthly signups chart
monthly_signups = filtered_df.groupby('month_year').size().reset_index(name='count')
monthly_signups['month_year'] = monthly_signups['month_year'].astype(str)

if view_type == "Cumulative":
    monthly_signups['count'] = monthly_signups['count'].cumsum()
    title_suffix = "Cumulative"
else:
    title_suffix = "Monthly"

fig = px.line(monthly_signups, 
              x='month_year', 
              y='count',
              title=f'{title_suffix} Signups Over Time - {selected_org}',
              labels={'month_year': 'Month', 'count': 'Number of Signups'})

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Number of Signups",
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# Additional metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Signups", len(filtered_df))
    
with col2:
    st.metric("Unique Organizations", filtered_df['organization'].nunique())
    
with col3:
    st.metric("Languages", filtered_df['language'].nunique())

# Assessment Status Analysis
st.subheader("Assessment Status Analysis")

# Get status counts
status_counts = filtered_df['status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']

if view_type == "Cumulative":
    status_counts['Count'] = status_counts['Count'].cumsum()
    title_suffix = "Cumulative"
else:
    title_suffix = "Distribution of"

# Create a bar chart for status distribution with labels on top of bars
fig_status = px.bar(status_counts, 
                    x='Status', 
                    y='Count',
                    text='Count',
                    title=f'{title_suffix} Assessment Statuses - {selected_org}',
                    labels={'Status': 'Assessment Status', 'Count': 'Number of Signups'})

fig_status.update_traces(textposition='outside')
fig_status.update_layout(
    xaxis_title="Assessment Status",
    yaxis_title="Number of Signups",
    hovermode='x unified',
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

st.plotly_chart(fig_status, use_container_width=True)

# Raw data view
st.subheader("Raw Data")
st.dataframe(filtered_df) 