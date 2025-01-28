import streamlit as st
import plotly.express as px
from utils import create_rating_distribution_chart, create_comparison_radar_chart
from data import get_review_highlights

def display_business_metrics(data, business_name):
    """Display key metrics for a single business"""
    business_data = data[data['Business Name'].str.strip() == business_name.strip()]
    if business_data.empty:
        st.error(f"No data found for {business_name}")
        return

    business = business_data.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Rating", f"{business['Average Rating']:.1f}⭐")

    with col2:
        st.metric("Total Reviews", f"{business['Total Reviews']:,}")

    with col3:
        st.metric("5-Star Reviews", f"{business['5_star']:.1f}%")

    # Display address if available
    if 'Address' in business and business['Address']:
        st.markdown(f"**Address:** {business['Address']}")

    st.plotly_chart(create_rating_distribution_chart(data, business_name), use_container_width=True)

    st.subheader("Review Highlights")
    highlights = get_review_highlights(business['Place ID'])
    for highlight in highlights:
        st.markdown(f"- {highlight}")

def display_comparison(data, business1, business2):
    """Display side-by-side comparison of two businesses"""
    # Strip whitespace for comparison
    data['Business Name'] = data['Business Name'].str.strip()
    business1 = business1.strip()
    business2 = business2.strip()

    # Check if businesses exist in the data
    if business1 not in data['Business Name'].values or business2 not in data['Business Name'].values:
        missing_businesses = []
        if business1 not in data['Business Name'].values:
            missing_businesses.append(business1)
        if business2 not in data['Business Name'].values:
            missing_businesses.append(business2)
        st.error(f"The following businesses were filtered out due to low rating: {', '.join(missing_businesses)}")
        st.info("Try adjusting the minimum rating filter to include these businesses.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(business1)
        display_business_metrics(data, business1)

    with col2:
        st.subheader(business2)
        display_business_metrics(data, business2)

    st.subheader("Comparison Chart")
    st.plotly_chart(create_comparison_radar_chart(data, business1, business2), use_container_width=True)