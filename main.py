import streamlit as st
import pandas as pd
from data import search_businesses, get_review_highlights
from components import display_comparison

# Page configuration
st.set_page_config(
    page_title="Business Review Comparison",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'businesses' not in st.session_state:
    st.session_state.businesses = []

# App title and description
st.title("📊 Business Review Comparison Tool")
st.markdown("""
Compare ratings and reviews between different businesses to make informed decisions.
Search for businesses and select two to compare.
""")

# Search functionality
col1, col2 = st.columns(2)

with col1:
    search_query = st.text_input("Search for businesses", placeholder="e.g., coffee shops")

with col2:
    location = st.text_input("Location (optional)", placeholder="e.g., San Francisco")

if st.button("Search"):
    with st.spinner("Searching for businesses..."):
        st.session_state.data = search_businesses(search_query, location)
        if st.session_state.data.empty:
            st.error("No businesses found. Try a different search term or location.")
        else:
            st.success(f"Found {len(st.session_state.data)} businesses!")
            st.session_state.businesses = st.session_state.data['Business Name'].tolist()

# Business selection
if not st.session_state.data.empty:
    col1, col2 = st.columns(2)

    with col1:
        business1 = st.selectbox(
            "Select first business",
            options=st.session_state.businesses,
            key='business1'
        )

    with col2:
        # Filter out first business from second dropdown
        remaining_businesses = [b for b in st.session_state.businesses if b != business1]
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
else:
    st.info("Search for businesses to start comparing")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by Google Places API</p>
</div>
""", unsafe_allow_html=True)