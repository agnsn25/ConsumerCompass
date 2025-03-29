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

# Custom CSS for responsive design
st.markdown("""
<style>
    .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    @media (max-width: 768px) {
        .stColumn > div {
            width: 100%;
            flex-direction: column;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.3rem !important;
        }
        p, li {
            font-size: 0.9rem !important;
        }
        .stSelectbox, .stTextInput {
            margin-bottom: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'businesses' not in st.session_state:
    st.session_state.businesses = []
if 'business_lookup' not in st.session_state:
    st.session_state.business_lookup = {}
if 'screen_width' not in st.session_state:
    st.session_state.screen_width = 1200  # Default to desktop

# JavaScript to detect screen size and update session state
screen_size_js = """
<script>
    // Function to update the session state with screen width
    function updateScreenWidth() {
        const width = window.innerWidth;
        const data = {
            width: width,
        };
        const stringData = JSON.stringify(data);
        
        // Send data to Streamlit
        if (window.parent.window.streamlitReportObject) {
            window.parent.window.streamlitReportObject.setWidgetValue('screen_width_data', stringData);
        }
    }
    
    // Update on load and on resize
    updateScreenWidth();
    window.addEventListener('resize', updateScreenWidth);
</script>
"""
st.components.v1.html(screen_size_js, height=0)

# Widget to receive screen width data
screen_width_data = st.empty()
if screen_width_data.text_input("", key="screen_width_data", label_visibility="collapsed"):
    try:
        import json
        data = json.loads(screen_width_data.text_input("", key="screen_width_data", label_visibility="collapsed"))
        st.session_state.screen_width = data.get('width', 1200)
    except:
        pass

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

# Search functionality - responsive layout based on screen width
screen_width = st.session_state.get('screen_width', 1200)
if screen_width <= 768:  # Mobile view - stack vertically
    search_query = st.text_input("Search for businesses", placeholder="e.g., coffee shops")
    location = st.text_input("Location (optional)", placeholder="e.g., San Francisco")
else:  # Desktop view - side by side
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

# Business selection - responsive layout based on screen width
if not st.session_state.data.empty:
    # Container with styling for selection area
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0;">
        <h3 style="margin-top: 0; text-align: center;">Select Businesses to Compare</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if screen_width <= 768:  # Mobile view - stack vertically
        # First business
        business1_label = st.selectbox(
            "Select first business",
            options=st.session_state.businesses,
            key='business1_label'
        )
        business1 = st.session_state.business_lookup.get(business1_label) if business1_label else None
        
        # Second business - exclude first selection
        remaining_businesses = [b for b in st.session_state.businesses if b != business1_label]
        business2_label = st.selectbox(
            "Select second business",
            options=remaining_businesses,
            key='business2_label'
        )
        business2 = st.session_state.business_lookup.get(business2_label) if business2_label else None
    
    else:  # Desktop view - side by side
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