# ============================================================================
# Afforestation Detection - Flask Application
# ============================================================================
# Main entry point for the web application.
# 
# This Flask application provides:
# - Web interface for location input
# - API endpoints for processing satellite images
# - Results display with visualizations
# ============================================================================

from flask import Flask, render_template, request, jsonify, url_for
import os
import time

# Import custom modules
import config
import place_lookup
import image_processing
import calc_area

# Initialize Flask application
app = Flask(__name__)

# Ensure static images directory exists
os.makedirs(config.STATIC_IMAGES_DIR, exist_ok=True)


# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def index():
    """
    Home page route.
    
    Renders the main page with:
    - Location input form
    - Project information
    - Results display area (initially hidden)
    """
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze location for afforestation potential.
    
    This endpoint:
    1. Receives location name from the form
    2. Fetches satellite image using Google APIs
    3. Processes image to detect barren land
    4. Calculates afforestation potential
    5. Returns results as JSON
    
    Request Body:
    -------------
    location : str
        Name of the location to analyze (e.g., "Nagpur, India")
    
    Returns:
    --------
    JSON response with:
    - success: boolean
    - location_info: location details
    - processing_results: image processing data
    - afforestation_data: area and tree calculations
    - images: paths to processed images
    """
    try:
        # Get location from request
        location_name = request.form.get("location", "").strip()
        
        if not location_name:
            return jsonify({
                "success": False,
                "error": "Please enter a location name"
            }), 400
        
        print(f"\n{'='*60}")
        print(f"ANALYZING LOCATION: {location_name}")
        print(f"{'='*60}")
        
        # Step 1: Get location coordinates
        print("\n[STEP 1] Getting location coordinates...")
        location_info = place_lookup.get_location_info(location_name)
        
        if not location_info:
            return jsonify({
                "success": False,
                "error": f"Could not find location: {location_name}"
            }), 404
        
        lat = location_info["lat"]
        lng = location_info["lng"]
        print(f"[SUCCESS] Coordinates: ({lat}, {lng})")
        
        # Step 2: Fetch satellite image
        print("\n[STEP 2] Fetching satellite image...")
        timestamp = int(time.time())
        original_path = os.path.join(config.STATIC_IMAGES_DIR, f"satellite_{timestamp}.png")
        
        satellite_image = place_lookup.fetch_satellite_image(lat, lng, original_path)
        
        if satellite_image is None:
            return jsonify({
                "success": False,
                "error": "Failed to fetch satellite image"
            }), 500
        
        # Step 3: Process image
        print("\n[STEP 3] Processing satellite image...")
        processing_results = image_processing.process_satellite_image(
            satellite_image, 
            config.STATIC_IMAGES_DIR
        )
        
        # Step 4: Calculate afforestation potential
        print("\n[STEP 4] Calculating afforestation potential...")
        afforestation_data = calc_area.calculate_afforestation_potential(
            processing_results["barren_pixels"],
            processing_results["total_pixels"]
        )
        
        # Step 5: Get image coverage info
        coverage = calc_area.calculate_image_coverage()
        
        # Prepare response
        response = {
            "success": True,
            "location": {
                "name": location_info.get("name", location_name),
                "formatted_address": location_info.get("formatted_address", location_name),
                "lat": lat,
                "lng": lng
            },
            "coverage": coverage,
            "processing": {
                "barren_percentage": processing_results["barren_percentage"],
                "vegetation_pixels": processing_results["vegetation_pixels"],
                "water_pixels": processing_results["water_pixels"],
                "roads_pixels": processing_results["roads_pixels"]
            },
            "afforestation": {
                "area_sqm": afforestation_data["area_sqm"],
                "area_acres": afforestation_data["area_acres"],
                "area_hectares": afforestation_data["area_hectares"],
                "trees_standard": afforestation_data["trees_standard"],
                "trees_dense": afforestation_data["trees_dense"],
                "trees_sparse": afforestation_data["trees_sparse"],
                "co2_10year_tonnes": afforestation_data["co2_10year_tonnes"],
                "oxygen_per_year_kg": afforestation_data["oxygen_per_year_kg"]
            },
            "images": {
                "original": "/" + processing_results["original_path"].replace("\\", "/"),
                "processed": "/" + processing_results["processed_path"].replace("\\", "/"),
                "overlay": "/" + processing_results["overlay_path"].replace("\\", "/")
            }
        }
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500


@app.route("/demo")
def demo():
    """
    Demo route that uses sample data without API calls.
    
    Useful for testing the interface without a Google API key.
    """
    # Force demo mode temporarily
    original_demo_mode = config.DEMO_MODE
    config.DEMO_MODE = True
    
    try:
        # Analyze a sample location
        location_info = {
            "name": "Demo Location",
            "formatted_address": "Nagpur, Maharashtra, India (Demo)",
            "lat": 21.1458,
            "lng": 79.0882
        }
        
        # Create demo image
        satellite_image = place_lookup.fetch_satellite_image(
            location_info["lat"], 
            location_info["lng"],
            os.path.join(config.STATIC_IMAGES_DIR, "demo_satellite.png")
        )
        
        # Process image
        processing_results = image_processing.process_satellite_image(
            satellite_image, 
            config.STATIC_IMAGES_DIR
        )
        
        # Calculate afforestation
        afforestation_data = calc_area.calculate_afforestation_potential(
            processing_results["barren_pixels"],
            processing_results["total_pixels"]
        )
        
        return render_template("index.html", 
            demo_data={
                "location": location_info,
                "afforestation": afforestation_data,
                "images": {
                    "original": "/" + processing_results["original_path"].replace("\\", "/"),
                    "processed": "/" + processing_results["processed_path"].replace("\\", "/"),
                    "overlay": "/" + processing_results["overlay_path"].replace("\\", "/")
                }
            }
        )
    finally:
        # Restore original demo mode setting
        config.DEMO_MODE = original_demo_mode


@app.route("/api/coverage")
def get_coverage():
    """
    API endpoint to get image coverage information.
    
    Returns the real-world area covered by the satellite image
    based on current zoom level settings.
    """
    coverage = calc_area.calculate_image_coverage()
    return jsonify(coverage)


@app.route("/api/tree-estimates")
def get_tree_estimates():
    """
    API endpoint to calculate tree estimates for a given area.
    
    Query Parameters:
    -----------------
    area_sqm : float
        Area in square meters
    
    Returns:
    --------
    JSON with tree estimates for different spacing options
    """
    area_sqm = request.args.get("area_sqm", type=float, default=0)
    
    if area_sqm <= 0:
        return jsonify({"error": "Please provide a valid area_sqm parameter"}), 400
    
    return jsonify({
        "area_sqm": area_sqm,
        "area_acres": calc_area.square_meters_to_acres(area_sqm),
        "trees_standard": calc_area.estimate_trees_standard_spacing(area_sqm),
        "trees_dense": calc_area.estimate_trees_dense_spacing(area_sqm),
        "trees_sparse": calc_area.estimate_trees_sparse_spacing(area_sqm)
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template("index.html", error="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template("index.html", error="Internal server error"), 500


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AFFORESTATION DETECTION SYSTEM")
    print("Pollution Control by Identifying Potential Land")
    print("=" * 60)
    
    # Check API key configuration
    if config.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        print("\n[WARNING] Google API key not configured!")
        print("The application will run in DEMO MODE.")
        print("To use real satellite images, add your API key to config.py")
        print("\nGet your API key from: https://console.cloud.google.com/")
    
    print(f"\n[INFO] Starting Flask server...")
    print(f"[INFO] Debug mode: {config.DEBUG_MODE}")
    print(f"\n[INFO] Open your browser and navigate to:")
    print(f"       http://localhost:{config.PORT}")
    print("=" * 60 + "\n")
    
    # Run the Flask application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG_MODE
    )
