import streamlit as st
import pandas as pd
from data import search_businesses, get_review_highlights, verify_api_key
from components import display_comparison

# Page configuration
st.set_page_config(
    page_title="ConsumerCompass",
    page_icon="🧭",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'businesses' not in st.session_state:
    st.session_state.businesses = []
if 'business_lookup' not in st.session_state:
    st.session_state.business_lookup = {}

# App title and description
st.title("🧭 ConsumerCompass")
st.markdown("""
Compare ratings and reviews between different businesses to make informed decisions.
Search for businesses and select two to compare.
""")

# Verify API key status
api_valid, api_message = verify_api_key()
if not api_valid:
    st.error(f"⚠️ API Error: {api_message}")
    st.info("Please ensure you have:")
    st.markdown("""
    1. Added a valid Google Places API key
    2. Enabled the Places API in Google Cloud Console
    3. Waited a few minutes for the API activation to take effect
    """)
    st.stop()

# Search functionality
col1, col2 = st.columns(2)

with col1:
    search_query = st.text_input("Search for businesses", placeholder="e.g., coffee shops")

with col2:
    location = st.text_input("Location (optional)", placeholder="e.g., San Francisco")

@st.cache_data(ttl=300)
def perform_business_search(query, location):
    """Perform business search with caching and detailed error handling"""
    try:
        data = search_businesses(query, location)
        if data.empty:
            return None, "No businesses found. Please try a different search term or location."
        return data, None
    except Exception as e:
        error_msg = str(e)
        if 'REQUEST_DENIED' in error_msg:
            return None, "API access denied. Please ensure the Places API is enabled and the API key is valid."
        return None, f"Error searching businesses: {error_msg}"

# Update the search button logic
if st.button("Search"):
    if not search_query:
        st.warning("Please enter a search term")
    else:
        with st.spinner("Searching for businesses..."):
            data, error = perform_business_search(search_query, location)
            if error:
                st.error(error)
            else:
                st.session_state.data = data
                # Store original business names for lookup
                st.session_state.business_lookup = {
                    f"{name} - {addr}": name 
                    for name, addr in zip(data['Business Name'], data['Address'])
                }
                st.session_state.businesses = list(st.session_state.business_lookup.keys())
                st.success(f"Found {len(data)} businesses!")

# Business selection
if not st.session_state.data.empty:
    col1, col2 = st.columns(2)

    with col1:
        business1_label = st.selectbox(
            "Select first business",
            options=st.session_state.businesses,
            key='business1_label'
        )
        business1 = st.session_state.business_lookup.get(business1_label) if business1_label else None

    with col2:
        # Ensure second dropdown excludes the first selection
        remaining_businesses = [b for b in st.session_state.businesses if b != business1_label]
        business2_label = st.selectbox(
            "Select second business",
            options=remaining_businesses,
            key='business2_label'
        )
        business2 = st.session_state.business_lookup.get(business2_label) if business2_label else None

    # Add a filter for minimum rating
    min_rating = st.slider(
        "Filter by minimum rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5
    )

    # Display comparison if both businesses are selected
    if business1 and business2:
        # Print debug information
        st.write("Debug Info:")
        st.write(f"Business 1 Label: {business1_label}")
        st.write(f"Business 1 Name: {business1}")
        st.write(f"Business 2 Label: {business2_label}")
        st.write(f"Business 2 Name: {business2}")

        # Filter data based on minimum rating
        filtered_data = st.session_state.data[
            st.session_state.data['Average Rating'] >= min_rating
        ].copy()

        # Display comparison
        display_comparison(filtered_data, business1, business2)
    else:
        st.info("Please select two businesses to compare")
else:
    st.info("Search for businesses to start comparing")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>ConsumerCompass | Powered by Google Places API</p>
</div>
""", unsafe_allow_html=True)