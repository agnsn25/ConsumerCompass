import plotly.graph_objects as go
import plotly.express as px

def create_rating_distribution_chart(business_data, business_name):
    """Create a bar chart showing the rating distribution for a business"""
    ratings = ['5_star', '4_star', '3_star', '2_star', '1_star']
    values = business_data[business_data['Business Name'] == business_name][ratings].values[0]
    
    fig = go.Figure(data=[
        go.Bar(
            x=ratings,
            y=values,
            marker_color=['#4CAF50', '#8BC34A', '#FFEB3B', '#FF9800', '#F44336'],
            text=[f'{v:.1f}%' for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f'Rating Distribution for {business_name}',
        xaxis_title='Rating',
        yaxis_title='Percentage',
        showlegend=False,
        height=300
    )
    
    return fig

def create_comparison_radar_chart(business_data, business1, business2):
    """Create a radar chart comparing two businesses"""
    metrics = ['Average Rating', '5_star', '4_star', '3_star', '2_star', '1_star']
    
    fig = go.Figure()
    
    for business in [business1, business2]:
        values = business_data[business_data['Business Name'] == business][metrics].values[0]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name=business
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        height=400
    )
    
    return fig
