import pandas as pd
import numpy as np
import googlemaps
import os
import time
from datetime import datetime

# Initialize Google Maps client
gmaps = None

def initialize_gmaps():
    """Initialize Google Maps client"""
    global gmaps
    try:
        api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        if not api_key:
            print("No API key found in environment variables")
            return False
        gmaps = googlemaps.Client(key=api_key)
        return True
    except Exception as e:
        print(f"Error initializing Google Maps client: {str(e)}")
        return False

# Try to initialize on module load
initialize_gmaps()

def verify_api_key():
    """Verify if the API key is working"""
    global gmaps
    try:
        if not gmaps and not initialize_gmaps():
            return False, "Google Maps client not initialized. Please check your API key."

        try:
            # Try a simple place search instead of geocode
            test_result = gmaps.places("restaurant")
            return True, "API key is valid and working"
        except Exception as e:
            if 'REQUEST_DENIED' in str(e):
                # Re-initialize the client to ensure fresh connection
                if initialize_gmaps():
                    # Try one more time with a simple search
                    test_result = gmaps.places("restaurant")
                    return True, "API key is valid and working"
            print(f"API verification error: {str(e)}")
            raise e
    except Exception as e:
        error_msg = str(e)
        if 'REQUEST_DENIED' in error_msg:
            return False, "API key is not authorized. Please ensure Places API is enabled in Google Cloud Console."
        return False, f"API key verification failed: {error_msg}"

def search_businesses(query, location=None):
    """Search for businesses using Google Places API"""
    global gmaps
    try:
        # Verify API key first
        is_valid, message = verify_api_key()
        if not is_valid:
            print(f"API Key Error: {message}")
            return pd.DataFrame()

        # Set up location parameters
        search_location = None
        if location:
            try:
                # Geocode the location to get coordinates
                geocode_result = gmaps.geocode(location)
                if geocode_result:
                    search_location = {
                        'lat': geocode_result[0]['geometry']['location']['lat'],
                        'lng': geocode_result[0]['geometry']['location']['lng']
                    }
                    print(f"Using location coordinates: {search_location}")
            except Exception as e:
                print(f"Error geocoding location: {str(e)}")

        print(f"Searching for: {query}")

        all_results = []
        next_page_token = None

        # Split query into keywords for better matching
        keywords = query.lower().split()
        base_query = ' '.join(keywords)

        # Get results with pagination
        while True:
            try:
                # Prepare search parameters
                search_params = {
                    'query': base_query,
                    'language': 'en'
                }

                if search_location:
                    search_params['location'] = search_location
                    search_params['radius'] = 150000  # Increased to 150km radius for wider coverage

                if next_page_token:
                    search_params = {'page_token': next_page_token}

                print(f"Search parameters: {search_params}")

                # Perform the search
                places_result = gmaps.places(**search_params)

                # Process current page results
                if places_result.get('results'):
                    all_results.extend(places_result['results'])
                    print(f"Found {len(places_result['results'])} results on current page")

                # Check for next page
                next_page_token = places_result.get('next_page_token')
                if not next_page_token:
                    break

                # Wait briefly before requesting next page (API requirement)
                time.sleep(2)

            except Exception as e:
                print(f"Error in places search: {str(e)}")
                break

        if not all_results:
            print("No results found in places search")
            return pd.DataFrame()

        print(f"Total results found: {len(all_results)}")

        # Process all results
        businesses = []
        for place in all_results:
            try:
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
            except Exception as e:
                print(f"Error processing place details for {place.get('name', 'unknown')}: {str(e)}")
                continue

        return pd.DataFrame(businesses)

    except Exception as e:
        print(f"Error searching businesses: {str(e)}")
        return pd.DataFrame()

def get_review_highlights(place_id):
    """Get review highlights for a specific business"""
    global gmaps
    try:
        if not gmaps and not initialize_gmaps():
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

def get_business_image(place_id):
    """Get the primary photo for a business using its place_id"""
    global gmaps
    try:
        if not gmaps and not initialize_gmaps():
            return None
            
        # Get place details with photo field
        place_details = gmaps.place(place_id, fields=['photo'])['result']
        photos = place_details.get('photos', [])
        
        if not photos:
            print(f"No photos available for place_id: {place_id}")
            return None
            
        # Get the first (primary) photo reference
        photo_reference = photos[0].get('photo_reference')
        if not photo_reference:
            print(f"No photo reference found for place_id: {place_id}")
            return None
            
        # Get the photo URL from the API (max width 400 for better display)
        # This URL will work directly in an img tag
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={os.environ.get('GOOGLE_PLACES_API_KEY')}"
        return photo_url
        
    except Exception as e:
        print(f"Error getting business image: {str(e)}")
        return None