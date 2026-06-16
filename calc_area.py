# ============================================================================
# Area Calculation Module
# ============================================================================
# This module handles:
# 1. Converting pixel counts to real-world area measurements
# 2. Calculating potential tree plantation capacity
# 3. Generating afforestation estimates
# ============================================================================

import math

# Import configuration settings
import config


def pixels_to_square_meters(pixel_count, meters_per_pixel=None):
    """
    Convert pixel count to square meters.
    
    Formula:
    --------
    area_sqm = pixel_count × (meters_per_pixel)²
    
    At zoom level 18, each pixel represents approximately 0.6 meters.
    So each pixel covers 0.6 × 0.6 = 0.36 square meters.
    
    Parameters:
    -----------
    pixel_count : int
        Number of pixels
    meters_per_pixel : float, optional
        Meters per pixel (uses config default if not specified)
    
    Returns:
    --------
    float : Area in square meters
    """
    if meters_per_pixel is None:
        meters_per_pixel = config.METERS_PER_PIXEL
    
    # Each pixel represents a square area
    area_per_pixel = meters_per_pixel ** 2
    
    return pixel_count * area_per_pixel


def square_meters_to_acres(area_sqm):
    """
    Convert square meters to acres.
    
    Formula:
    --------
    acres = square_meters / 4046.86
    
    Parameters:
    -----------
    area_sqm : float
        Area in square meters
    
    Returns:
    --------
    float : Area in acres
    """
    return area_sqm / config.SQMETERS_PER_ACRE


def square_meters_to_hectares(area_sqm):
    """
    Convert square meters to hectares.
    
    Formula:
    --------
    hectares = square_meters / 10000
    
    Parameters:
    -----------
    area_sqm : float
        Area in square meters
    
    Returns:
    --------
    float : Area in hectares
    """
    return area_sqm / 10000


def estimate_trees_standard_spacing(area_sqm):
    """
    Estimate number of trees with standard spacing.
    
    Standard Spacing Rule:
    ---------------------
    Trees are planted 3 meters apart in a grid pattern.
    Each tree occupies a 3m × 3m = 9 square meter area.
    
    This spacing is recommended for:
    - Timber trees (Teak, Sal, Eucalyptus)
    - Fruit trees (Mango, Jackfruit)
    
    Parameters:
    -----------
    area_sqm : float
        Available area in square meters
    
    Returns:
    --------
    int : Estimated number of trees
    """
    spacing = config.TREE_SPACING_STANDARD
    area_per_tree = spacing ** 2  # 3m × 3m = 9 sq.m
    
    return int(area_sqm / area_per_tree)


def estimate_trees_dense_spacing(area_sqm):
    """
    Estimate number of trees with dense spacing.
    
    Dense Spacing Rule:
    ------------------
    Trees are planted 2 meters apart in a grid pattern.
    Each tree occupies a 2m × 2m = 4 square meter area.
    
    This spacing is recommended for:
    - Fast-growing species (Bamboo, Cassia)
    - Initial plantation (with later thinning)
    
    Parameters:
    -----------
    area_sqm : float
        Available area in square meters
    
    Returns:
    --------
    int : Estimated number of trees
    """
    spacing = config.TREE_SPACING_DENSE
    area_per_tree = spacing ** 2  # 2m × 2m = 4 sq.m
    
    return int(area_sqm / area_per_tree)


def estimate_trees_sparse_spacing(area_sqm):
    """
    Estimate number of trees with sparse spacing.
    
    Sparse Spacing Rule:
    -------------------
    Trees are planted 5 meters apart in a grid pattern.
    Each tree occupies a 5m × 5m = 25 square meter area.
    
    This spacing is recommended for:
    - Large canopy trees (Banyan, Peepal)
    - Agroforestry systems
    
    Parameters:
    -----------
    area_sqm : float
        Available area in square meters
    
    Returns:
    --------
    int : Estimated number of trees
    """
    spacing = 5  # 5 meters apart
    area_per_tree = spacing ** 2  # 5m × 5m = 25 sq.m
    
    return int(area_sqm / area_per_tree)


def calculate_co2_absorption(tree_count, years=10):
    """
    Estimate CO2 absorption by planted trees.
    
    Calculation Basis:
    ------------------
    Average tree absorbs approximately 22 kg of CO2 per year
    (Source: European Environment Agency)
    
    Parameters:
    -----------
    tree_count : int
        Number of trees to be planted
    years : int
        Number of years to calculate absorption for
    
    Returns:
    --------
    dict : CO2 absorption estimates
           - per_year_kg: Annual absorption in kg
           - total_kg: Total absorption over specified years
           - total_tonnes: Total absorption in metric tonnes
    """
    # Average CO2 absorption per tree per year (in kg)
    co2_per_tree_per_year = 22
    
    per_year = tree_count * co2_per_tree_per_year
    total = per_year * years
    
    return {
        "per_year_kg": per_year,
        "total_kg": total,
        "total_tonnes": total / 1000,
        "years": years
    }


def calculate_oxygen_production(tree_count, years=10):
    """
    Estimate oxygen production by planted trees.
    
    Calculation Basis:
    ------------------
    One mature tree produces approximately 118 kg of oxygen per year
    (Source: Arbor Day Foundation)
    
    Parameters:
    -----------
    tree_count : int
        Number of trees to be planted
    years : int
        Number of years to calculate production for
    
    Returns:
    --------
    dict : Oxygen production estimates
    """
    # Average O2 production per tree per year (in kg)
    o2_per_tree_per_year = 118
    
    per_year = tree_count * o2_per_tree_per_year
    total = per_year * years
    
    return {
        "per_year_kg": per_year,
        "total_kg": total,
        "total_tonnes": total / 1000,
        "years": years
    }


def calculate_afforestation_potential(barren_pixels, total_pixels):
    """
    Calculate complete afforestation potential for detected barren land.
    
    This is the main calculation function that brings together all estimates.
    
    Parameters:
    -----------
    barren_pixels : int
        Number of pixels detected as barren land
    total_pixels : int
        Total pixels in the image
    
    Returns:
    --------
    dict : Complete afforestation analysis including:
           - area_sqm: Area in square meters
           - area_acres: Area in acres
           - area_hectares: Area in hectares
           - trees_standard: Trees with 3m spacing
           - trees_dense: Trees with 2m spacing
           - trees_sparse: Trees with 5m spacing
           - barren_percentage: Percentage of barren land
           - co2_absorption: CO2 absorption estimates
           - oxygen_production: Oxygen production estimates
    """
    print("\n" + "=" * 60)
    print("CALCULATING AFFORESTATION POTENTIAL")
    print("=" * 60)
    
    # Calculate area
    area_sqm = pixels_to_square_meters(barren_pixels)
    area_acres = square_meters_to_acres(area_sqm)
    area_hectares = square_meters_to_hectares(area_sqm)
    
    # Calculate tree estimates
    trees_standard = estimate_trees_standard_spacing(area_sqm)
    trees_dense = estimate_trees_dense_spacing(area_sqm)
    trees_sparse = estimate_trees_sparse_spacing(area_sqm)
    
    # Calculate environmental impact (using standard spacing)
    co2 = calculate_co2_absorption(trees_standard)
    oxygen = calculate_oxygen_production(trees_standard)
    
    # Barren land percentage
    barren_pct = (barren_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    # Compile results
    results = {
        # Area measurements
        "area_sqm": round(area_sqm, 2),
        "area_acres": round(area_acres, 4),
        "area_hectares": round(area_hectares, 4),
        
        # Pixel data
        "barren_pixels": barren_pixels,
        "total_pixels": total_pixels,
        "barren_percentage": round(barren_pct, 2),
        
        # Tree estimates
        "trees_standard": trees_standard,
        "trees_dense": trees_dense,
        "trees_sparse": trees_sparse,
        
        # Environmental impact
        "co2_per_year_kg": co2["per_year_kg"],
        "co2_10year_tonnes": round(co2["total_tonnes"], 2),
        "oxygen_per_year_kg": oxygen["per_year_kg"],
        
        # Spacing info for display
        "spacing_standard": config.TREE_SPACING_STANDARD,
        "spacing_dense": config.TREE_SPACING_DENSE
    }
    
    # Print summary
    print(f"\nArea Analysis:")
    print(f"  - Barren Land: {barren_pixels:,} pixels ({barren_pct:.2f}%)")
    print(f"  - Area: {area_sqm:,.2f} sq.m = {area_acres:.4f} acres")
    
    print(f"\nTree Plantation Estimates:")
    print(f"  - Standard (3m spacing): {trees_standard:,} trees")
    print(f"  - Dense (2m spacing): {trees_dense:,} trees")
    print(f"  - Sparse (5m spacing): {trees_sparse:,} trees")
    
    print(f"\nEnvironmental Impact (Standard Planting, 10 years):")
    print(f"  - CO2 Absorption: {co2['total_tonnes']:.2f} tonnes")
    print(f"  - Oxygen Production: {oxygen['total_tonnes']:.2f} tonnes")
    
    print("=" * 60 + "\n")
    
    return results


def format_number(number):
    """
    Format large numbers with commas for display.
    
    Parameters:
    -----------
    number : int or float
        Number to format
    
    Returns:
    --------
    str : Formatted number string
    """
    if isinstance(number, float):
        return f"{number:,.2f}"
    return f"{number:,}"


def calculate_image_coverage(zoom_level=None, image_width=None, image_height=None):
    """
    Calculate the real-world area covered by the satellite image.
    
    Parameters:
    -----------
    zoom_level : int
        Google Maps zoom level (default from config)
    image_width : int
        Image width in pixels (default from config)
    image_height : int
        Image height in pixels (default from config)
    
    Returns:
    --------
    dict : Coverage information
    """
    if zoom_level is None:
        zoom_level = config.ZOOM_LEVEL
    if image_width is None:
        image_width = config.IMAGE_WIDTH
    if image_height is None:
        image_height = config.IMAGE_HEIGHT
    
    # Meters per pixel varies by zoom level
    # At zoom 18: ~0.6m/pixel, each zoom level doubles/halves the scale
    meters_per_pixel = 156543.03392 * math.cos(0) / (2 ** zoom_level)
    
    # For our standard zoom 18, use the config value
    if zoom_level == 18:
        meters_per_pixel = config.METERS_PER_PIXEL
    
    width_meters = image_width * meters_per_pixel
    height_meters = image_height * meters_per_pixel
    area_sqm = width_meters * height_meters
    
    return {
        "width_meters": round(width_meters, 2),
        "height_meters": round(height_meters, 2),
        "area_sqm": round(area_sqm, 2),
        "area_acres": round(square_meters_to_acres(area_sqm), 4),
        "meters_per_pixel": round(meters_per_pixel, 3)
    }


# -----------------------------------------------------------------------------
# Module Test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Area Calculation Module")
    print("=" * 60)
    
    # Test with sample data
    sample_barren_pixels = 50000
    sample_total_pixels = 640 * 640  # 409,600 pixels
    
    print(f"\nTest Data:")
    print(f"  Barren pixels: {sample_barren_pixels:,}")
    print(f"  Total pixels: {sample_total_pixels:,}")
    
    # Calculate afforestation potential
    results = calculate_afforestation_potential(sample_barren_pixels, sample_total_pixels)
    
    print("\nImage Coverage:")
    coverage = calculate_image_coverage()
    for key, value in coverage.items():
        print(f"  {key}: {value}")
