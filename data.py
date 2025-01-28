import pandas as pd
import numpy as np

# Mock data generation for businesses
def generate_mock_data():
    businesses = {
        'Business Name': [
            'Joe\'s Coffee Shop', 'Central Cafe', 'Morning Brew',
            'Pizza Palace', 'Burger Joint', 'Sushi Express',
            'Taco Town', 'Thai Delight', 'Indian Spices',
            'French Bistro'
        ],
        'Average Rating': [
            4.5, 4.2, 4.7, 4.3, 4.1, 4.8, 4.4, 4.6, 4.2, 4.9
        ],
        'Total Reviews': [
            np.random.randint(50, 500) for _ in range(10)
        ]
    }
    
    df = pd.DataFrame(businesses)
    
    # Generate rating distributions
    for business in range(len(df)):
        total = df.loc[business, 'Total Reviews']
        avg = df.loc[business, 'Average Rating']
        
        # Create a somewhat realistic distribution around the average
        distribution = np.random.normal(avg, 0.5, total)
        distribution = np.clip(distribution, 1, 5)
        
        df.loc[business, '5_star'] = np.sum(distribution >= 4.5) / total * 100
        df.loc[business, '4_star'] = np.sum((distribution >= 3.5) & (distribution < 4.5)) / total * 100
        df.loc[business, '3_star'] = np.sum((distribution >= 2.5) & (distribution < 3.5)) / total * 100
        df.loc[business, '2_star'] = np.sum((distribution >= 1.5) & (distribution < 2.5)) / total * 100
        df.loc[business, '1_star'] = np.sum(distribution < 1.5) / total * 100
    
    return df

# Sample review highlights
REVIEW_HIGHLIGHTS = {
    'Joe\'s Coffee Shop': [
        "Great atmosphere and friendly staff",
        "Best coffee in town",
        "Cozy environment"
    ],
    'Central Cafe': [
        "Decent food but slow service",
        "Nice outdoor seating",
        "Good value for money"
    ],
    'Morning Brew': [
        "Amazing breakfast options",
        "Quick service",
        "Fresh ingredients"
    ],
    'Pizza Palace': [
        "Authentic Italian taste",
        "Large portions",
        "Great value"
    ],
    'Burger Joint': [
        "Juicy burgers",
        "Fast service",
        "Good variety"
    ],
    'Sushi Express': [
        "Fresh fish",
        "Creative rolls",
        "Excellent presentation"
    ],
    'Taco Town': [
        "Authentic Mexican flavors",
        "Generous portions",
        "Friendly staff"
    ],
    'Thai Delight': [
        "Spicy and flavorful",
        "Beautiful decor",
        "Great service"
    ],
    'Indian Spices': [
        "Rich flavors",
        "Authentic cuisine",
        "Friendly atmosphere"
    ],
    'French Bistro': [
        "Excellent wine selection",
        "Romantic atmosphere",
        "Outstanding service"
    ]
}
