# ============================================================================
# Image Processing Module
# ============================================================================
# This module handles all computer vision operations:
# 1. Mean Shift segmentation for grouping similar regions
# 2. HSV color masking to identify different land types
# 3. Barren land detection for afforestation potential
# ============================================================================

import cv2
import numpy as np
from PIL import Image
import os

# Import configuration settings
import config


def load_image(image_source):
    """
    Load image from file path or PIL Image object.
    
    Parameters:
    -----------
    image_source : str or PIL.Image
        File path or PIL Image object
    
    Returns:
    --------
    numpy.ndarray : Image in BGR format (OpenCV format)
    """
    if isinstance(image_source, str):
        # Load from file path
        image = cv2.imread(image_source)
        if image is None:
            raise ValueError(f"Could not load image from: {image_source}")
        return image
    elif isinstance(image_source, Image.Image):
        # Convert PIL Image to OpenCV format (RGB to BGR)
        image_rgb = np.array(image_source)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        return image_bgr
    else:
        raise TypeError("image_source must be a file path or PIL Image")


def apply_mean_shift_segmentation(image):
    """
    Apply Mean Shift segmentation to group similar colored regions.
    
    Algorithm Explanation:
    ----------------------
    Mean Shift is a clustering algorithm that:
    1. Treats each pixel as a point in (x, y, color) space
    2. Iteratively shifts each point towards the densest nearby region
    3. Groups pixels that converge to the same point
    
    This helps in:
    - Reducing noise in the image
    - Creating distinct regions with uniform colors
    - Making subsequent color-based detection more accurate
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image in BGR format
    
    Returns:
    --------
    numpy.ndarray : Segmented image with smoothed regions
    """
    print("[PROCESS] Applying Mean Shift segmentation...")
    
    # pyrMeanShiftFiltering parameters:
    # - sp: Spatial window radius (how far to look spatially)
    # - sr: Color window radius (how different colors can be to group together)
    segmented = cv2.pyrMeanShiftFiltering(
        image,
        sp=config.MEANSHIFT_SPATIAL_RADIUS,
        sr=config.MEANSHIFT_COLOR_RADIUS
    )
    
    print("[SUCCESS] Mean Shift segmentation complete")
    return segmented


def convert_to_hsv(image):
    """
    Convert BGR image to HSV color space.
    
    Why HSV?
    --------
    HSV (Hue, Saturation, Value) is better for color detection because:
    - Hue represents the actual color (0-179 in OpenCV)
    - Saturation represents color intensity
    - Value represents brightness
    
    This separation makes it easier to detect colors regardless of lighting.
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image in BGR format
    
    Returns:
    --------
    numpy.ndarray : Image in HSV format
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def detect_vegetation(hsv_image):
    """
    Detect green vegetation (trees, grass) in the image.
    
    Parameters:
    -----------
    hsv_image : numpy.ndarray
        Image in HSV format
    
    Returns:
    --------
    numpy.ndarray : Binary mask where white = vegetation
    """
    print("[PROCESS] Detecting vegetation...")
    
    # Create mask for green colors
    lower = np.array(config.HSV_GREEN_LOWER)
    upper = np.array(config.HSV_GREEN_UPPER)
    
    mask = cv2.inRange(hsv_image, lower, upper)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove small noise
    
    vegetation_pixels = np.count_nonzero(mask)
    print(f"[INFO] Vegetation pixels detected: {vegetation_pixels}")
    
    return mask


def detect_barren_land(hsv_image):
    """
    Detect barren/brown land suitable for afforestation.
    
    Algorithm:
    ----------
    1. Create mask for brown/tan colors (typical of barren land)
    2. Apply morphological operations to:
       - Close small gaps (fill tiny holes)
       - Open to remove noise (small false detections)
    3. Return binary mask
    
    Parameters:
    -----------
    hsv_image : numpy.ndarray
        Image in HSV format
    
    Returns:
    --------
    numpy.ndarray : Binary mask where white = barren land
    """
    print("[PROCESS] Detecting barren land...")
    
    # Create mask for brown/tan colors
    lower = np.array(config.HSV_BROWN_LOWER)
    upper = np.array(config.HSV_BROWN_UPPER)
    
    mask = cv2.inRange(hsv_image, lower, upper)
    
    # Apply morphological operations
    kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    barren_pixels = np.count_nonzero(mask)
    print(f"[INFO] Barren land pixels detected: {barren_pixels}")
    
    return mask


def detect_water(hsv_image):
    """
    Detect water bodies (lakes, rivers, ponds) in the image.
    
    Parameters:
    -----------
    hsv_image : numpy.ndarray
        Image in HSV format
    
    Returns:
    --------
    numpy.ndarray : Binary mask where white = water
    """
    print("[PROCESS] Detecting water bodies...")
    
    lower = np.array(config.HSV_WATER_LOWER)
    upper = np.array(config.HSV_WATER_UPPER)
    
    mask = cv2.inRange(hsv_image, lower, upper)
    
    kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    water_pixels = np.count_nonzero(mask)
    print(f"[INFO] Water pixels detected: {water_pixels}")
    
    return mask


def detect_roads_buildings(hsv_image):
    """
    Detect roads and buildings (gray, low-saturation areas).
    
    These are identified by low saturation values, as man-made structures
    typically appear gray or desaturated in satellite imagery.
    
    Parameters:
    -----------
    hsv_image : numpy.ndarray
        Image in HSV format
    
    Returns:
    --------
    numpy.ndarray : Binary mask where white = roads/buildings
    """
    print("[PROCESS] Detecting roads and buildings...")
    
    # Extract saturation channel
    saturation = hsv_image[:, :, 1]
    
    # Low saturation indicates gray colors (roads, buildings)
    mask = np.where(saturation < config.GRAY_SATURATION_THRESHOLD, 255, 0).astype(np.uint8)
    
    kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    gray_pixels = np.count_nonzero(mask)
    print(f"[INFO] Road/building pixels detected: {gray_pixels}")
    
    return mask


def create_segmentation_overlay(original_image, vegetation_mask, barren_mask, water_mask, roads_mask):
    """
    Create a color-coded overlay showing different land types.
    
    Color Coding:
    - Green: Vegetation (existing trees)
    - Orange/Yellow: Barren land (potential afforestation)
    - Blue: Water bodies
    - Gray: Roads and buildings
    
    Parameters:
    -----------
    original_image : numpy.ndarray
        Original satellite image (BGR)
    vegetation_mask : numpy.ndarray
        Binary mask for vegetation
    barren_mask : numpy.ndarray
        Binary mask for barren land
    water_mask : numpy.ndarray
        Binary mask for water
    roads_mask : numpy.ndarray
        Binary mask for roads/buildings
    
    Returns:
    --------
    numpy.ndarray : Color-coded overlay image
    """
    print("[PROCESS] Creating segmentation overlay...")
    
    # Start with a copy of original converted to float for blending
    overlay = original_image.copy().astype(np.float32)
    
    # Apply color overlays with transparency
    alpha = 0.6  # Overlay transparency
    
    # Green for vegetation - check if mask has any pixels
    if np.count_nonzero(vegetation_mask) > 0:
        vegetation_color = np.array([0, 200, 0], dtype=np.float32)
        mask_idx = vegetation_mask > 0
        overlay[mask_idx] = overlay[mask_idx] * (1 - alpha) + vegetation_color * alpha
    
    # Orange for barren land (afforestation target)
    if np.count_nonzero(barren_mask) > 0:
        barren_color = np.array([0, 165, 255], dtype=np.float32)
        mask_idx = barren_mask > 0
        overlay[mask_idx] = overlay[mask_idx] * (1 - alpha) + barren_color * alpha
    
    # Blue for water
    if np.count_nonzero(water_mask) > 0:
        water_color = np.array([255, 100, 50], dtype=np.float32)
        mask_idx = water_mask > 0
        overlay[mask_idx] = overlay[mask_idx] * (1 - alpha) + water_color * alpha
    
    # Gray for roads/buildings
    if np.count_nonzero(roads_mask) > 0:
        roads_color = np.array([128, 128, 128], dtype=np.float32)
        mask_idx = roads_mask > 0
        overlay[mask_idx] = overlay[mask_idx] * (1 - alpha) + roads_color * alpha
    
    # Convert back to uint8
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)
    
    print("[SUCCESS] Overlay created")
    return overlay


def highlight_barren_land(original_image, barren_mask):
    """
    Create an image highlighting only the barren land areas.
    
    This creates a clear visual of areas suitable for afforestation.
    
    Parameters:
    -----------
    original_image : numpy.ndarray
        Original satellite image (BGR)
    barren_mask : numpy.ndarray
        Binary mask for barren land
    
    Returns:
    --------
    numpy.ndarray : Image with barren land highlighted in bright color
    """
    print("[PROCESS] Highlighting barren land for afforestation...")
    
    # Create a darker version of the original for non-barren areas
    highlighted = (original_image * 0.4).astype(np.float32)
    
    # Highlight barren areas in bright orange/yellow - check if mask has any pixels
    if np.count_nonzero(barren_mask) > 0:
        highlight_color = np.array([0, 200, 255], dtype=np.float32)  # BGR: Yellow-Orange
        mask_idx = barren_mask > 0
        # Blend original with highlight color
        highlighted[mask_idx] = (
            original_image[mask_idx].astype(np.float32) * 0.5 + highlight_color * 0.5
        )
    
    # Convert back to uint8
    highlighted = np.clip(highlighted, 0, 255).astype(np.uint8)
    
    # Draw contours around barren areas
    contours, _ = cv2.findContours(barren_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(highlighted, contours, -1, (0, 255, 255), 2)  # Yellow contours
    
    print("[SUCCESS] Barren land highlighted")
    return highlighted


def process_satellite_image(image_source, output_dir="static/images"):
    """
    Main processing function that performs complete analysis on satellite image.
    
    Algorithm Pipeline:
    1. Load and prepare the image
    2. Apply Mean Shift segmentation for smoother regions
    3. Convert to HSV color space
    4. Detect different land types using color masks
    5. Create visualization overlays
    6. Calculate barren land statistics
    7. Save processed images
    
    Parameters:
    -----------
    image_source : str or PIL.Image
        Input satellite image (path or PIL Image)
    output_dir : str
        Directory to save processed images
    
    Returns:
    --------
    dict : Processing results including:
           - barren_pixels: Number of barren land pixels
           - total_pixels: Total image pixels
           - barren_percentage: Percentage of barren land
           - vegetation_pixels: Number of vegetation pixels
           - water_pixels: Number of water pixels
           - roads_pixels: Number of road/building pixels
           - original_path: Path to saved original image
           - processed_path: Path to saved processed image
           - overlay_path: Path to saved overlay image
    """
    print("\n" + "=" * 60)
    print("SATELLITE IMAGE PROCESSING")
    print("=" * 60)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Load image
    print("\n[STEP 1] Loading image...")
    original = load_image(image_source)
    total_pixels = original.shape[0] * original.shape[1]
    print(f"[INFO] Image size: {original.shape[1]}x{original.shape[0]} pixels")
    print(f"[INFO] Total pixels: {total_pixels}")
    
    # Save original image
    original_path = os.path.join(output_dir, "satellite_original.png")
    cv2.imwrite(original_path, original)
    
    # Step 2: Apply Mean Shift segmentation
    print("\n[STEP 2] Segmenting image...")
    segmented = apply_mean_shift_segmentation(original)
    
    # Step 3: Convert to HSV
    print("\n[STEP 3] Converting to HSV color space...")
    hsv_image = convert_to_hsv(segmented)
    
    # Step 4: Detect different land types
    print("\n[STEP 4] Detecting land types...")
    vegetation_mask = detect_vegetation(hsv_image)
    barren_mask = detect_barren_land(hsv_image)
    water_mask = detect_water(hsv_image)
    roads_mask = detect_roads_buildings(hsv_image)
    
    # Step 5: Create visualizations
    print("\n[STEP 5] Creating visualizations...")
    
    # Full segmentation overlay
    overlay = create_segmentation_overlay(
        original, vegetation_mask, barren_mask, water_mask, roads_mask
    )
    overlay_path = os.path.join(output_dir, "segmentation_overlay.png")
    cv2.imwrite(overlay_path, overlay)
    
    # Highlighted barren land
    highlighted = highlight_barren_land(original, barren_mask)
    processed_path = os.path.join(output_dir, "barren_land_highlighted.png")
    cv2.imwrite(processed_path, highlighted)
    
    # Step 6: Calculate statistics
    print("\n[STEP 6] Calculating statistics...")
    barren_pixels = np.count_nonzero(barren_mask)
    vegetation_pixels = np.count_nonzero(vegetation_mask)
    water_pixels = np.count_nonzero(water_mask)
    roads_pixels = np.count_nonzero(roads_mask)
    
    barren_percentage = (barren_pixels / total_pixels) * 100
    
    # Prepare results
    results = {
        "barren_pixels": int(barren_pixels),
        "total_pixels": int(total_pixels),
        "barren_percentage": round(barren_percentage, 2),
        "vegetation_pixels": int(vegetation_pixels),
        "water_pixels": int(water_pixels),
        "roads_pixels": int(roads_pixels),
        "original_path": original_path.replace("\\", "/"),
        "processed_path": processed_path.replace("\\", "/"),
        "overlay_path": overlay_path.replace("\\", "/")
    }
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Barren land: {barren_pixels} pixels ({barren_percentage:.2f}%)")
    print(f"Vegetation: {vegetation_pixels} pixels")
    print(f"Water: {water_pixels} pixels")
    print(f"Roads/Buildings: {roads_pixels} pixels")
    print("=" * 60 + "\n")
    
    return results


def add_legend_to_image(image_path, output_path=None):
    """
    Add a color legend to the processed image.
    
    Parameters:
    -----------
    image_path : str
        Path to the image to add legend to
    output_path : str, optional
        Path to save the result (defaults to same as input)
    
    Returns:
    --------
    str : Path to the saved image with legend
    """
    image = cv2.imread(image_path)
    if image is None:
        return image_path
    
    # Legend dimensions
    legend_height = 100
    legend_width = image.shape[1]
    
    # Create legend panel
    legend = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 255
    
    # Add color boxes and labels
    colors = [
        ((0, 200, 0), "Vegetation"),
        ((0, 165, 255), "Barren Land (Afforestation)"),
        ((255, 100, 50), "Water"),
        ((128, 128, 128), "Roads/Buildings")
    ]
    
    x_offset = 20
    for color, label in colors:
        # Draw color box
        cv2.rectangle(legend, (x_offset, 40), (x_offset + 30, 70), color, -1)
        cv2.rectangle(legend, (x_offset, 40), (x_offset + 30, 70), (0, 0, 0), 1)
        
        # Add label
        cv2.putText(legend, label, (x_offset + 40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        x_offset += 160
    
    # Combine image and legend
    combined = np.vstack([image, legend])
    
    # Save result
    if output_path is None:
        output_path = image_path
    cv2.imwrite(output_path, combined)
    
    return output_path


# -----------------------------------------------------------------------------
# Module Test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Image Processing Module")
    print("=" * 60)
    
    # Test with a sample image
    test_image_path = "static/images/test_satellite.png"
    
    if os.path.exists(test_image_path):
        results = process_satellite_image(test_image_path)
        print("\nResults:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    else:
        print(f"Test image not found: {test_image_path}")
        print("Run place_lookup.py first to generate a test image")
