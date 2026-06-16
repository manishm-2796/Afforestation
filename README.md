# 🌳 Pollution Control by Identifying Potential Land for Afforestation

A Python-based full-stack project that analyzes satellite images to identify barren land suitable for tree plantation and estimates the afforestation potential.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Algorithm Explanation](#algorithm-explanation)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [License](#license)

## 🎯 Overview

This system helps in pollution control by analyzing satellite imagery of user-specified locations to:
1. Identify barren or unused land suitable for tree plantation
2. Calculate the total afforestation area
3. Estimate the number of trees that can be planted
4. Predict environmental impact (CO₂ absorption, O₂ production)

## ✨ Features

- **Location Search**: Enter any location name and get satellite imagery
- **Image Segmentation**: Uses Mean Shift algorithm for region grouping
- **Color-based Detection**: HSV color masking to identify:
  - 🌲 Vegetation (green areas)
  - 🟫 Barren land (brown/tan areas)
  - 💧 Water bodies (blue areas)
  - 🏢 Roads/Buildings (gray areas)
- **Area Calculation**: Converts pixel data to real-world measurements
- **Tree Estimation**: Multiple spacing options (2m, 3m, 5m)
- **Visual Results**: Highlighted images showing detected areas
- **Demo Mode**: Works without API key using synthetic images

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.8+ |
| Web Framework | Flask |
| Image Processing | OpenCV, NumPy |
| Image Handling | Pillow (PIL) |
| HTTP Requests | Requests |
| Frontend | HTML5, CSS3, JavaScript |
| APIs | Google Places API, Google Maps Static API |

## 📁 Project Structure

```
Afforestation project/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration and settings
├── place_lookup.py           # Location → Coordinates conversion
├── image_processing.py       # Image segmentation and analysis
├── calc_area.py              # Area and tree calculations
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── static/
│   ├── css/
│   │   └── style.css         # Stylesheet
│   └── images/               # Processed images (auto-generated)
└── templates/
    └── index.html            # Web interface
```

## 💻 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project

```bash
cd "d:\Afforesation project"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Google API Key Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - **Places API**
   - **Maps Static API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the API key

### Configure the Project

Open `config.py` and update:

```python
GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

### Demo Mode (No API Key Required)

If you don't have an API key, the project works in demo mode with synthetic satellite images. To enable explicitly:

```python
DEMO_MODE = True
```

## 🚀 Running the Project

### Start the Flask Server

```bash
python app.py
```

### Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Application

1. Enter a location name (e.g., "Nagpur, India")
2. Click the "Analyze" button
3. Wait for processing (10-20 seconds)
4. View results:
   - Original satellite image
   - Processed image with barren land highlighted
   - Segmentation overlay
   - Statistics (area, tree count, CO₂ absorption)

## 🧠 Algorithm Explanation

### 1. Mean Shift Segmentation

**What it does**: Groups similar colored pixels together to create distinct regions.

**How it works**:
- Each pixel is a point in (x, y, color) space
- The algorithm iteratively shifts points towards dense regions
- Pixels that converge to the same point are grouped together

**Why we use it**: Reduces noise and creates cleaner regions for color detection.

### 2. HSV Color Masking

**What it does**: Detects land types based on color in HSV space.

**HSV = Hue, Saturation, Value**:
- **Hue**: The actual color (0-179 in OpenCV)
- **Saturation**: Color intensity
- **Value**: Brightness

**Color Ranges Used**:
- **Vegetation**: H: 35-85 (green range)
- **Barren Land**: H: 10-30 (brown/tan range)
- **Water**: H: 100-130 (blue range)
- **Roads/Buildings**: Low saturation (gray)

### 3. Morphological Operations

**What it does**: Cleans up the detected masks.

- **Closing**: Fills small holes in detected regions
- **Opening**: Removes small noise points

### 4. Area Calculation

**Formula**:
```
Area (sq.m) = Pixel Count × (Meters per Pixel)²

At Zoom 18: 1 pixel ≈ 0.6 meters
So: 1 pixel = 0.36 sq.m
```

**Tree Estimation**:
```
Standard (3m spacing): Trees = Area / 9
Dense (2m spacing):    Trees = Area / 4
Sparse (5m spacing):   Trees = Area / 25
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with input form |
| `/analyze` | POST | Analyze a location |
| `/demo` | GET | Run demo with sample data |
| `/api/coverage` | GET | Get image coverage info |
| `/api/tree-estimates?area_sqm=<value>` | GET | Calculate tree estimates |

## 📸 Screenshots

### Home Page
The main interface with location search input.

### Results View
Shows original satellite image, processed image with barren land highlighted, and segmentation overlay.

### Statistics Cards
Displays area in acres, number of trees (different spacing options), and CO₂ absorption estimates.

## 📖 Understanding the Output

### Images

1. **Original Satellite Image**: Raw satellite imagery from Google Maps
2. **Barren Land Highlighted**: Yellow/orange overlay on detected barren land
3. **Segmentation Overlay**: Color-coded map showing all land types

### Statistics

- **Barren Land Area**: Total area suitable for afforestation
- **Trees (Standard)**: Estimated trees with 3m×3m spacing
- **Trees (Dense)**: Estimated trees with 2m×2m spacing
- **CO₂ Absorption**: Environmental impact over 10 years

## 🔧 Customization

### Adjust HSV Color Ranges

Edit `config.py` to tune color detection:

```python
# More sensitive brown detection
HSV_BROWN_LOWER = (8, 40, 40)
HSV_BROWN_UPPER = (35, 210, 210)
```

### Change Image Settings

```python
IMAGE_WIDTH = 800        # Higher resolution
IMAGE_HEIGHT = 800
ZOOM_LEVEL = 17          # Lower zoom = larger area
```

## 📝 Notes for Academic Submission

- All code is well-commented for easy understanding
- Modular architecture follows software engineering principles
- Error handling implemented throughout
- Demo mode allows testing without external dependencies
- Professional UI suitable for presentations

## 📄 License

This project is created for academic purposes. Feel free to use and modify for educational projects.

---

**Made with 🌱 for a greener future**

*MCA Final Year Project*
