import streamlit as st
import plotly.express as px
from utils import create_rating_distribution_chart, create_comparison_radar_chart
from data import get_review_highlights

def display_business_metrics(data, business_name):
    """Display key metrics for a single business"""
    business_data = data[data['Business Name'] == business_name]
    if business_data.empty:
        st.error(f"Business '{business_name}' was filtered out due to the minimum rating requirement.")
        return

    business = business_data.iloc[0]

    # Check screen width dynamically - use more columns on wider screens
    # and stack vertically on mobile screens
    screen_width = st.session_state.get('screen_width', 1200)  # Default to desktop
    
    # Responsive layout for metrics
    if screen_width <= 768:  # Mobile view
        st.metric("Average Rating", f"{business['Average Rating']:.1f}⭐")
        st.metric("Total Reviews", f"{business['Total Reviews']:,}")
        st.metric("5-Star Reviews", f"{business['5_star']:.1f}%")
    else:  # Desktop view
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Rating", f"{business['Average Rating']:.1f}⭐")
        with col2:
            st.metric("Total Reviews", f"{business['Total Reviews']:,}")
        with col3:
            st.metric("5-Star Reviews", f"{business['5_star']:.1f}%")

    # Display address if available
    if 'Address' in business and business['Address']:
        # Make address responsive with word wrapping
        st.markdown(f"""
        <div style="word-wrap: break-word; max-width: 100%;">
            <strong>Address:</strong> {business['Address']}
        </div>
        """, unsafe_allow_html=True)

    # Responsive charts
    st.plotly_chart(create_rating_distribution_chart(data, business_name), use_container_width=True)

    st.subheader("Review Highlights")
    highlights = get_review_highlights(business['Place ID'])
    
    # Add custom styling for review highlights
    for highlight in highlights:
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 10px; 
                    border-radius: 5px; margin-bottom: 8px; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            {highlight}
        </div>
        """, unsafe_allow_html=True)

def display_comparison(data, business1, business2):
    """Display side-by-side comparison of two businesses"""
    # Check if businesses exist in the filtered data
    business1_data = data[data['Business Name'] == business1]
    business2_data = data[data['Business Name'] == business2]

    missing_businesses = []
    if business1_data.empty:
        missing_businesses.append(business1)
    if business2_data.empty:
        missing_businesses.append(business2)

    if missing_businesses:
        st.error(f"The following businesses were filtered out due to low rating: {', '.join(missing_businesses)}")
        st.info("Try adjusting the minimum rating filter to include these businesses.")
        return

    # Check screen width dynamically
    screen_width = st.session_state.get('screen_width', 1200)  # Default to desktop
    
    # Add comparison header with styling
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 10px 0; text-align: center;">
        <h2 style="margin: 0; color: #1e3a8a;">Business Comparison</h2>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Comparing {business1} vs {business2}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Responsive layout based on screen width
    if screen_width <= 768:  # Mobile view - stack vertically
        # First business
        st.markdown(f"""
        <div style="background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin-top: 15px;">
            <h3 style="margin: 0;">{business1}</h3>
        </div>
        """, unsafe_allow_html=True)
        display_business_metrics(data, business1)
        
        # Add a visual separator
        st.markdown("<hr style='margin: 20px 0; border-color: #ddd;'>", unsafe_allow_html=True)
        
        # Second business
        st.markdown(f"""
        <div style="background-color: #fff7e6; padding: 10px; border-radius: 5px; margin-top: 15px;">
            <h3 style="margin: 0;">{business2}</h3>
        </div>
        """, unsafe_allow_html=True)
        display_business_metrics(data, business2)
    else:  # Desktop view - side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background-color: #e6f7ff; padding: 10px; border-radius: 5px;">
                <h3 style="margin: 0;">{business1}</h3>
            </div>
            """, unsafe_allow_html=True)
            display_business_metrics(data, business1)
        with col2:
            st.markdown(f"""
            <div style="background-color: #fff7e6; padding: 10px; border-radius: 5px;">
                <h3 style="margin: 0;">{business2}</h3>
            </div>
            """, unsafe_allow_html=True)
            display_business_metrics(data, business2)

    # Comparison radar chart with responsive styling
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-top: 20px;">
        <h3 style="margin: 0 0 10px 0; text-align: center;">Comparison Chart</h3>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(create_comparison_radar_chart(data, business1, business2), use_container_width=True)