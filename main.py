import streamlit as st
import pandas as pd
from data import generate_mock_data
from components import display_comparison

# Page configuration
st.set_page_config(
    page_title="Business Review Comparison",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = generate_mock_data()

# App title and description
st.title("📊 Business Review Comparison Tool")
st.markdown("""
Compare ratings and reviews between different businesses to make informed decisions.
Choose two businesses below to see a detailed comparison.
""")

# Business selection
col1, col2 = st.columns(2)

with col1:
    business1 = st.selectbox(
        "Select first business",
        options=st.session_state.data['Business Name'].unique(),
        key='business1'
    )

with col2:
    # Filter out first business from second dropdown
    remaining_businesses = st.session_state.data[
        st.session_state.data['Business Name'] != business1
    ]['Business Name'].unique()
    
    business2 = st.selectbox(
        "Select second business",
        options=remaining_businesses,
        key='business2'
    )

# Add a filter for minimum rating
min_rating = st.slider(
    "Filter by minimum rating",
    min_value=1.0,
    max_value=5.0,
    value=1.0,
    step=0.5
)

# Filter data based on minimum rating
filtered_data = st.session_state.data[
    st.session_state.data['Average Rating'] >= min_rating
]

# Display comparison
if business1 and business2:
    display_comparison(filtered_data, business1, business2)
else:
    st.info("Please select two businesses to compare")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Data shown is mock data for demonstration purposes.</p>
</div>
""", unsafe_allow_html=True)
