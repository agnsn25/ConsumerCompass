import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def create_rating_distribution_chart(business_data, business_name):
    """Create a bar chart showing the rating distribution for a business"""
    ratings = ['5_star', '4_star', '3_star', '2_star', '1_star']
    values = business_data[business_data['Business Name'] == business_name][ratings].values[0]
    
    # Determine if we're on mobile
    screen_width = st.session_state.get('screen_width', 1200)
    is_mobile = screen_width <= 768
    
    # Create labels that look better on mobile
    display_ratings = ["5★", "4★", "3★", "2★", "1★"] if is_mobile else ratings
    
    fig = go.Figure(data=[
        go.Bar(
            x=display_ratings,
            y=values,
            marker_color=['#4CAF50', '#8BC34A', '#FFEB3B', '#FF9800', '#F44336'],
            text=[f'{v:.1f}%' for v in values],
            textposition='auto',
        )
    ])
    
    # Responsive layout adjustments
    title_font_size = 14 if is_mobile else 18
    axis_font_size = 10 if is_mobile else 12
    margin_size = dict(l=20, r=20, t=30, b=20) if is_mobile else dict(l=50, r=50, t=80, b=50)
    height = 250 if is_mobile else 300
    
    fig.update_layout(
        title={
            'text': f'Rating Distribution',
            'font': {'size': title_font_size},
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title='Rating',
        yaxis_title='Percentage',
        xaxis={'tickfont': {'size': axis_font_size}},
        yaxis={'tickfont': {'size': axis_font_size}},
        showlegend=False,
        height=height,
        margin=margin_size,
        autosize=True,
    )
    
    return fig

def create_comparison_radar_chart(business_data, business1, business2):
    """Create a radar chart comparing two businesses"""
    metrics = ['Average Rating', '5_star', '4_star', '3_star', '2_star', '1_star']
    
    # Determine if we're on mobile
    screen_width = st.session_state.get('screen_width', 1200)
    is_mobile = screen_width <= 768
    
    # Create labels that look better on mobile
    display_metrics = ["Avg Rating", "5★", "4★", "3★", "2★", "1★"] if is_mobile else metrics
    
    fig = go.Figure()
    
    # Custom colors for better distinction
    colors = ['rgba(31, 119, 180, 0.7)', 'rgba(255, 127, 14, 0.7)']
    
    for i, business in enumerate([business1, business2]):
        values = business_data[business_data['Business Name'] == business][metrics].values[0]
        # Truncate business name for better display on mobile
        display_name = business if not is_mobile else (business[:15] + '...' if len(business) > 15 else business)
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=display_metrics,
            fill='toself',
            name=display_name,
            fillcolor=colors[i],
            line=dict(color=colors[i].replace('0.7', '1.0')),
            opacity=0.8
        ))
    
    # Responsive layout adjustments
    font_size = 10 if is_mobile else 12
    height = 350 if is_mobile else 450
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont={'size': font_size}
            ),
            angularaxis=dict(
                tickfont={'size': font_size}
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1 if is_mobile else 0,
            xanchor="center",
            x=0.5,
            font=dict(size=font_size)
        ),
        height=height,
        autosize=True,
        margin=dict(l=10, r=10, t=20, b=30) if is_mobile else dict(l=50, r=50, t=50, b=50)
    )
    
    return fig
