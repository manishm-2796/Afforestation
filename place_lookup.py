# ============================================================================
# Place Lookup Module
# ============================================================================
# This module handles:
# 1. Converting location names to geographic coordinates (lat/lng)
# 2. Fetching satellite images from Google Maps Static API
# ============================================================================

import requests
from io import BytesIO
from PIL import Image
import os

# Import configuration settings
import config


def get_coordinates(location_name):
    """
    Convert a location name to geographic coordinates using Google Places API.
    
    Algorithm:
    1. Send location name to Google Places API (Text Search)
    2. Parse the JSON response to extract latitude and longitude
    3. Return coordinates as a tuple
    
    Parameters:
    -----------
    location_name : str
        Human-readable location name (e.g., "Nagpur, India")
    
    Returns:
    --------
    tuple : (latitude, longitude) as floats
            Returns (None, None) if location not found or API error
    
    Example:
    --------
    >>> lat, lng = get_coordinates("Nagpur, India")
    >>> print(f"Latitude: {lat}, Longitude: {lng}")
    Latitude: 21.1458, Longitude: 79.0882
    """
    
    # Check for demo mode
    if config.DEMO_MODE:
        # Return sample coordinates for demo
        print("[DEMO MODE] Using sample coordinates for Nagpur, India")
        return (21.1458, 79.0882)
    
    # Check if API key is configured
    if config.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        print("[WARNING] Google API key not configured!")
        print("Please add your API key to config.py")
        print("Using demo coordinates instead...")
        return (21.1458, 79.0882)
    
    # Google Places API endpoint for text search
    api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Request parameters
    params = {
        "query": location_name,
        "key": config.GOOGLE_API_KEY
    }
    
    try:
        # Make API request
        print(f"[API] Searching for location: {location_name}")
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse JSON response
        data = response.json()
        
        # Check API response status
        if data.get("status") != "OK":
            error_msg = data.get("error_message", data.get("status"))
            print(f"[ERROR] Places API error: {error_msg}")
            return (None, None)
        
        # Extract coordinates from first result
        if data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            print(f"[SUCCESS] Found coordinates: ({lat}, {lng})")
            return (lat, lng)
        else:
            print(f"[ERROR] No results found for: {location_name}")
            return (None, None)
            
    except requests.exceptions.Timeout:
        print("[ERROR] API request timed out")
        return (None, None)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return (None, None)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return (None, None)


def fetch_satellite_image(lat, lng, save_path=None):
    """
    Fetch satellite image from Google Maps Static API for given coordinates.
    
    Algorithm:
    1. Build Static Maps API URL with coordinates and parameters
    2. Download the image as bytes
    3. Convert to PIL Image object
    4. Optionally save to disk
    5. Return the Image object
    
    Parameters:
    -----------
    lat : float
        Latitude of the center point
    lng : float
        Longitude of the center point
    save_path : str, optional
        Path to save the downloaded image
    
    Returns:
    --------
    PIL.Image : The satellite image
                Returns None if download fails
    
    Example:
    --------
    >>> image = fetch_satellite_image(21.1458, 79.0882, "satellite.png")
    >>> image.show()
    """
    
    # Check for demo mode - use a sample image
    if config.DEMO_MODE or config.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        print("[DEMO MODE] Using sample satellite image")
        return _create_demo_image(lat, lng, save_path)
    
    # Google Maps Static API endpoint
    api_url = "https://maps.googleapis.com/maps/api/staticmap"
    
    # Request parameters
    params = {
        "center": f"{lat},{lng}",
        "zoom": config.ZOOM_LEVEL,
        "size": f"{config.IMAGE_WIDTH}x{config.IMAGE_HEIGHT}",
        "maptype": config.MAP_TYPE,
        "key": config.GOOGLE_API_KEY
    }
    
    try:
        # Make API request
        print(f"[API] Fetching satellite image for ({lat}, {lng})")
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Check if response is actually an image
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"[ERROR] Invalid response type: {content_type}")
            return _create_demo_image(lat, lng, save_path)
        
        # Convert bytes to PIL Image
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB if needed (remove alpha channel)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Save image if path provided
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)
            print(f"[SUCCESS] Image saved to: {save_path}")
        
        print(f"[SUCCESS] Image fetched: {image.size[0]}x{image.size[1]} pixels")
        return image
        
    except requests.exceptions.Timeout:
        print("[ERROR] Image download timed out")
        return _create_demo_image(lat, lng, save_path)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return _create_demo_image(lat, lng, save_path)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return _create_demo_image(lat, lng, save_path)


def _create_demo_image(lat, lng, save_path=None):
    """
    Create a demo satellite-like image for testing without API.
    
    This creates a synthetic image with various colored regions to simulate:
    - Green areas (vegetation)
    - Brown areas (barren land)
    - Gray areas (roads/buildings)
    - Blue areas (water)
    
    The image pattern varies based on the coordinates to produce unique
    results for different locations.
    
    Parameters:
    -----------
    lat : float
        Latitude (used to seed the pattern)
    lng : float
        Longitude (used to seed the pattern)
    save_path : str, optional
        Path to save the demo image
    
    Returns:
    --------
    PIL.Image : A synthetic demo image unique to the coordinates
    """
    import numpy as np
    import random
    
    print(f"[DEMO] Creating synthetic satellite image for ({lat:.4f}, {lng:.4f})...")
    
    # Use coordinates to create a unique seed for this location
    # This ensures the same location always produces the same image
    seed = int(abs(lat * 10000) + abs(lng * 10000)) % (2**31)
    random.seed(seed)
    np.random.seed(seed % (2**31 - 1))
    
    # Create base image
    width = config.IMAGE_WIDTH
    height = config.IMAGE_HEIGHT
    
    # Initialize image array
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Generate random parameters based on location seed
    # These control the terrain distribution
    num_regions = random.randint(8, 20)  # Number of terrain patches
    barren_ratio = random.uniform(0.15, 0.45)  # 15-45% barren land
    vegetation_ratio = random.uniform(0.25, 0.55)  # 25-55% vegetation
    water_present = random.random() < 0.3  # 30% chance of water
    road_density = random.uniform(0.05, 0.15)  # 5-15% roads
    
    # Generate region centers randomly
    regions = []
    for _ in range(num_regions):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        radius = random.randint(80, 200)
        # Region types: 0=vegetation, 1=barren, 2=roads, 3=forest, 4=barren2
        rtype = random.choices([0, 1, 2, 3, 4], 
                               weights=[vegetation_ratio, barren_ratio, road_density, 
                                       vegetation_ratio, barren_ratio])[0]
        regions.append((cx, cy, radius, rtype))
    
    # Fill the image based on regions
    for y in range(height):
        for x in range(width):
            # Find the closest region center
            min_dist = float('inf')
            region_type = 1  # Default to barren
            
            for cx, cy, radius, rtype in regions:
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                # Weight by radius - larger regions have more influence
                weighted_dist = dist / (radius + 1)
                if weighted_dist < min_dist:
                    min_dist = weighted_dist
                    region_type = rtype
            
            # Add noise for natural look
            noise = random.randint(0, 30)
            
            if region_type == 0:
                # Green vegetation (grass, crops)
                img_array[y, x] = [
                    max(0, min(255, 34 + noise)),
                    max(0, min(255, 139 + noise)),
                    max(0, min(255, 34 + noise))
                ]
            elif region_type == 1:
                # Barren/brown land (target for afforestation)
                img_array[y, x] = [
                    max(0, min(255, 160 + noise)),
                    max(0, min(255, 130 + noise)),
                    max(0, min(255, 90 + noise))
                ]
            elif region_type == 2:
                # Gray roads/buildings
                gray_val = 120 + noise
                img_array[y, x] = [
                    max(0, min(255, gray_val)),
                    max(0, min(255, gray_val)),
                    max(0, min(255, gray_val))
                ]
            elif region_type == 3:
                # Dense forest (darker green)
                img_array[y, x] = [
                    max(0, min(255, 20 + noise // 2)),
                    max(0, min(255, 80 + noise)),
                    max(0, min(255, 20 + noise // 2))
                ]
            else:
                # Mixed brown/tan (barren land variation)
                img_array[y, x] = [
                    max(0, min(255, 180 + noise)),
                    max(0, min(255, 150 + noise)),
                    max(0, min(255, 100 + noise))
                ]
    
    # Add water body if present for this location
    if water_present:
        water_x = random.randint(100, width - 100)
        water_y = random.randint(100, height - 100)
        water_size = random.randint(40, 80)
        
        for y in range(max(0, water_y - water_size), min(height, water_y + water_size)):
            for x in range(max(0, water_x - water_size), min(width, water_x + water_size)):
                if (x - water_x)**2 + (y - water_y)**2 < water_size**2:
                    noise = random.randint(0, 20)
                    img_array[y, x] = [
                        max(0, min(255, 65 + noise)),
                        max(0, min(255, 105 + noise)),
                        max(0, min(255, 200 + noise))
                    ]
    
    # Add some road lines
    num_roads = random.randint(1, 3)
    for _ in range(num_roads):
        if random.random() < 0.5:
            # Horizontal road
            road_y = random.randint(50, height - 50)
            road_width = random.randint(8, 15)
            for y in range(road_y, min(height, road_y + road_width)):
                for x in range(width):
                    if random.random() < 0.9:  # Some gaps
                        img_array[y, x] = [100, 100, 100]
        else:
            # Vertical road
            road_x = random.randint(50, width - 50)
            road_width = random.randint(8, 15)
            for x in range(road_x, min(width, road_x + road_width)):
                for y in range(height):
                    if random.random() < 0.9:
                        img_array[y, x] = [100, 100, 100]
    
    # Convert to PIL Image
    image = Image.fromarray(img_array, mode='RGB')
    
    # Save if path provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)
        print(f"[DEMO] Image saved to: {save_path}")
    
    # Reset random seed
    random.seed()
    np.random.seed()
    
    return image


def get_location_info(location_name):
    """
    Get complete location information including coordinates and formatted address.
    
    Parameters:
    -----------
    location_name : str
        Human-readable location name
    
    Returns:
    --------
    dict : Location information including:
           - lat: latitude
           - lng: longitude
           - formatted_address: full address
           - name: location name
           Returns None if location not found
    """
    
    # Check for demo mode - generate unique coordinates based on location name
    if config.DEMO_MODE or config.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        # Use hash of location name to generate consistent but unique coordinates
        import hashlib
        loc_hash = int(hashlib.md5(location_name.encode()).hexdigest(), 16)
        
        # Generate latitude between -60 and 60 (most habitable areas)
        lat = ((loc_hash % 12000) / 100) - 60
        # Generate longitude between -180 and 180  
        lng = ((loc_hash // 12000 % 36000) / 100) - 180
        
        return {
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "formatted_address": f"{location_name} (Demo Mode)",
            "name": location_name or "Demo Location"
        }
    
    # Google Places API endpoint
    api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        "query": location_name,
        "key": config.GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            location = result["geometry"]["location"]
            
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": result.get("formatted_address", location_name),
                "name": result.get("name", location_name)
            }
        
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to get location info: {e}")
        return None


# -----------------------------------------------------------------------------
# Module Test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Testing Place Lookup Module")
    print("=" * 60)
    
    # Test location lookup
    test_location = "Nagpur, India"
    print(f"\nLooking up: {test_location}")
    
    lat, lng = get_coordinates(test_location)
    
    if lat and lng:
        print(f"Coordinates: ({lat}, {lng})")
        
        # Test image fetch
        print("\nFetching satellite image...")
        image = fetch_satellite_image(lat, lng, "static/images/test_satellite.png")
        
        if image:
            print(f"Image size: {image.size}")
        else:
            print("Failed to fetch image")
    else:
        print("Failed to find location")
