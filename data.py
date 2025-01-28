import pandas as pd
import numpy as np
import googlemaps
import os
from datetime import datetime

# Initialize Google Maps client
try:
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_PLACES_API_KEY'])
except Exception as e:
    print(f"Error initializing Google Maps client: {str(e)}")
    gmaps = None

def verify_api_key():
    """Verify if the API key is working"""
    try:
        # Try a simple geocoding request to verify the key
        if not gmaps:
            return False, "Google Maps client not initialized. Please check your API key."

        result = gmaps.geocode('New York')
        return True, "API key is valid and working"
    except Exception as e:
        error_msg = str(e)
        if 'REQUEST_DENIED' in error_msg:
            return False, "API key is not authorized. Please ensure Places API is enabled in Google Cloud Console."
        return False, f"API key verification failed: {error_msg}"

def search_businesses(query, location=None):
    """Search for businesses using Google Places API"""
    try:
        # Verify API key first
        is_valid, message = verify_api_key()
        if not is_valid:
            print(f"API Key Error: {message}")
            return pd.DataFrame()

        # If location is not provided, use the query as is
        if location:
            search_query = f"{query} in {location}"
        else:
            search_query = query

        print(f"Searching for: {search_query}")

        # Perform the places search
        places_result = gmaps.places(search_query)

        if not places_result['results']:
            print("No results found")
            return pd.DataFrame()

        businesses = []
        for place in places_result['results']:
            # Get place details for more information
            place_details = gmaps.place(place['place_id'])['result']

            # Extract business data
            business = {
                'Business Name': place['name'],
                'Average Rating': place.get('rating', 0),
                'Total Reviews': place.get('user_ratings_total', 0),
                'Address': place.get('formatted_address', ''),
                'Place ID': place['place_id']
            }

            # Get rating distribution if available in details
            reviews = place_details.get('reviews', [])
            ratings = [review['rating'] for review in reviews]

            if ratings:
                total = len(ratings)
                business.update({
                    '5_star': sum(1 for r in ratings if r == 5) / total * 100,
                    '4_star': sum(1 for r in ratings if r == 4) / total * 100,
                    '3_star': sum(1 for r in ratings if r == 3) / total * 100,
                    '2_star': sum(1 for r in ratings if r == 2) / total * 100,
                    '1_star': sum(1 for r in ratings if r == 1) / total * 100,
                })
            else:
                business.update({
                    '5_star': 0,
                    '4_star': 0,
                    '3_star': 0,
                    '2_star': 0,
                    '1_star': 0,
                })

            businesses.append(business)

        return pd.DataFrame(businesses)
    except Exception as e:
        print(f"Error searching businesses: {str(e)}")
        if 'REQUEST_DENIED' in str(e):
            print("Please ensure Places API is enabled in Google Cloud Console")
        return pd.DataFrame()

def get_review_highlights(place_id):
    """Get review highlights for a specific business"""
    try:
        if not gmaps:
            return ["Error: Google Maps client not initialized"]

        place_details = gmaps.place(place_id)['result']
        reviews = place_details.get('reviews', [])

        # Sort reviews by rating and get the top 3 most helpful
        sorted_reviews = sorted(reviews, key=lambda x: (x.get('rating', 0), x.get('time', 0)), reverse=True)
        highlights = [review['text'][:200] + '...' if len(review['text']) > 200 else review['text']
                     for review in sorted_reviews[:3]]

        return highlights if highlights else ["No review highlights available"]
    except Exception as e:
        print(f"Error getting review highlights: {str(e)}")
        return ["Error fetching review highlights"]