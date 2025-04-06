# BgPro - Professional Image Background Editor

BgPro is a web application that allows you to easily remove backgrounds from images and apply professional effects to make your subject stand out.

## Features

- **Background Removal**: Instantly remove backgrounds from any image with AI-powered technology
- **Pro Mode**: Enhance your images with professional effects
- **Custom Background Colors**: Choose from a selection of professional background colors
- **White Glow Effect**: Add a customizable white glow/shadow around the main object
- **Adjustable Intensity**: Control the thickness and intensity of the white glow effect
- **One-Click Download**: Easily download your processed images

## How It Works

1. **Upload an Image**: Drag and drop an image or click to browse your files
2. **Select Mode**: Choose between simple background removal or Pro Mode
3. **Customize (Pro Mode)**: Adjust background color and white glow intensity
4. **Download**: Get your professionally edited image with one click

## Technical Details

BgPro uses:
- Flask web framework for the backend
- PIL/Pillow for image processing
- rembg library for AI-powered background removal
- Modern HTML, CSS, and JavaScript for the interface

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Requirements

- Python 3.8 or higher
- Required Python packages are listed in requirements.txt
