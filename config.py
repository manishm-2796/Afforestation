# ============================================================================
# Configuration File for Afforestation Detection System
# ============================================================================
# This file contains all configuration settings, API keys, and constants
# used throughout the application.
# ============================================================================

# -----------------------------------------------------------------------------
# GOOGLE API CONFIGURATION
# -----------------------------------------------------------------------------
# To use this application, you need a Google Cloud API key with:
# 1. Places API enabled
# 2. Maps Static API enabled
# 
# Get your API key from: https://console.cloud.google.com/
# Replace 'YOUR_API_KEY_HERE' with your actual key
# -----------------------------------------------------------------------------

GOOGLE_API_KEY = "YOUR_API_KEY_HERE"

# -----------------------------------------------------------------------------
# IMAGE SETTINGS
# -----------------------------------------------------------------------------
# These settings control the satellite image fetching

# Image dimensions (pixels) - Maximum for free tier is 640x640
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640

# Zoom level for satellite imagery
# Zoom 18 = ~0.6 meters per pixel (good for detailed land analysis)
# Zoom 17 = ~1.2 meters per pixel
# Zoom 16 = ~2.4 meters per pixel
ZOOM_LEVEL = 18

# Meters per pixel at zoom level 18 (at equator, varies slightly by latitude)
METERS_PER_PIXEL = 0.6

# Map type for Google Static Maps API
MAP_TYPE = "satellite"

# -----------------------------------------------------------------------------
# HSV COLOR RANGES FOR SEGMENTATION
# -----------------------------------------------------------------------------
# HSV = Hue, Saturation, Value
# H: 0-179 (in OpenCV), S: 0-255, V: 0-255
#
# These ranges are tuned for satellite imagery to detect different land types
# -----------------------------------------------------------------------------

# Green vegetation (trees, grass, crops)
# Hue: 35-85 covers yellow-green to cyan-green
HSV_GREEN_LOWER = (35, 40, 40)
HSV_GREEN_UPPER = (85, 255, 255)

# Barren/Brown land (empty land, dry soil, potential afforestation areas)
# Hue: 10-30 covers orange-brown to yellow-brown
HSV_BROWN_LOWER = (10, 50, 50)
HSV_BROWN_UPPER = (30, 200, 200)

# Water bodies (lakes, rivers, ponds)
# Hue: 100-130 covers cyan to blue
HSV_WATER_LOWER = (100, 50, 50)
HSV_WATER_UPPER = (130, 255, 255)

# Roads and buildings (low saturation gray areas)
# These are identified by low saturation values
GRAY_SATURATION_THRESHOLD = 50

# -----------------------------------------------------------------------------
# TREE PLANTATION SETTINGS
# -----------------------------------------------------------------------------
# Standard spacing rules for tree plantation

# Standard spacing: 3 meters apart (3m x 3m = 9 sq.m per tree)
TREE_SPACING_STANDARD = 3  # meters

# Dense spacing: 2 meters apart (2m x 2m = 4 sq.m per tree)
TREE_SPACING_DENSE = 2  # meters

# Conversion factor: 1 acre = 4046.86 square meters
SQMETERS_PER_ACRE = 4046.86

# -----------------------------------------------------------------------------
# IMAGE PROCESSING SETTINGS
# -----------------------------------------------------------------------------

# Mean Shift segmentation parameters
MEANSHIFT_SPATIAL_RADIUS = 21  # Window size for spatial distance
MEANSHIFT_COLOR_RADIUS = 51    # Window size for color distance

# Morphological operation kernel size (for noise removal)
MORPH_KERNEL_SIZE = 5

# Minimum contour area to consider (in pixels) - filters out tiny regions
MIN_CONTOUR_AREA = 100

# -----------------------------------------------------------------------------
# FLASK SETTINGS
# -----------------------------------------------------------------------------

# Flask debug mode (set to False in production)
DEBUG_MODE = True

# Host and port for Flask server
HOST = "0.0.0.0"
PORT = 5000

# -----------------------------------------------------------------------------
# FILE PATHS
# -----------------------------------------------------------------------------

# Directory for saving processed images
STATIC_IMAGES_DIR = "static/images"

# -----------------------------------------------------------------------------
# DEMO MODE
# -----------------------------------------------------------------------------
# When set to True, the application uses sample images instead of API calls
# Useful for testing without a Google API key

DEMO_MODE = False  # Set to True to use demo images
