import os
from flask import Flask, render_template, request, jsonify
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFilter, ImageChops
from io import BytesIO
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Professional color options
PRO_COLORS = {
    "dark_blue": "#0a1f3b",
    "dark_purple": "#2a0a3b",
    "dark_red": "#3b0a0a",
    "dark_green": "#0a3b1a",
    "charcoal": "#1a1a1a",
    "navy": "#001f3f",
    "burgundy": "#4a0a2a",
    "forest": "#0a3b2a",
    "midnight": "#0a0a3b",
    "crimson": "#3b0a1a",
    "emerald": "#0a3b3b",
    "coffee_brown": "#4a2c2a",
    "deep_teal": "#0a373d",
    "dark_olive": "#3b3b0a",
    "aubergine": "#3a0a29",
    "graphite": "#303030",
    "royal_blue": "#1a237e",
    "mahogany": "#4e2121",
    "moss_green": "#2c3b1a",
    "indigo": "#283593",
    "deep_maroon": "#4a1010",
    "dark_taupe": "#483c32",
    "steel_blue": "#1f4e79",
    "dark_khaki": "#3c3923",
    "muted_plum": "#673147",
    "dark_cyan": "#045d5d"
}

def process_image(input_image, mode, bg_color=None):
    # Remove background
    output_image = remove(input_image)
    
    if mode == "remove_bg":
        return output_image
        
    elif mode == "pro_mode" and output_image.mode == 'RGBA':
        # Split channels
        r, g, b, a = output_image.split()
        
        # Create the mask for the object
        shadow = a.point(lambda x: 255 if x > 20 else 0)  # Lower threshold to capture more of the object
        
        # Fixed narrow border size (approximately 0.3 cm / ~9 pixels)
        expansion_size = 9
        
        # Apply MaxFilter for consistent expansion (creates the white border)
        # Using two passes for smoother edge
        shadow = shadow.filter(ImageFilter.MaxFilter(expansion_size))
        shadow = shadow.filter(ImageFilter.MaxFilter(5))
        
        # Apply slight blur for softer edge
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        # Create a pitch white (255,255,255) shadow image with the shadow alpha
        shadow_img = Image.new('RGBA', output_image.size, (255, 255, 255, 0))
        shadow_img.putalpha(shadow)
        
        if bg_color:
            # Create background
            bg = Image.new('RGBA', output_image.size, bg_color)
            
            # Apply white shadow to background first
            bg = Image.alpha_composite(bg, shadow_img)
            
            # Then add the main object on top
            final_img = Image.alpha_composite(bg, output_image)
        else:
            # For transparent background, create a new transparent image
            transparent_bg = Image.new('RGBA', output_image.size, (0, 0, 0, 0))
            
            # Apply white shadow to transparent background
            transparent_bg = Image.alpha_composite(transparent_bg, shadow_img)
            
            # Then add the main object on top
            final_img = Image.alpha_composite(transparent_bg, output_image)
            
        # Final quality adjustments - increase contrast slightly to make the white pop more
        final_img = ImageEnhance.Contrast(final_img).enhance(1.15)
        final_img = ImageEnhance.Brightness(final_img).enhance(1.05)  # Slightly brighter overall
        final_img = ImageEnhance.Sharpness(final_img).enhance(1.1)
        
        return final_img
    
    return output_image

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        mode = request.form.get('mode', 'remove_bg')
        bg_color = request.form.get('bg_color', '#0a1f3b')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            input_image = Image.open(file.stream)
            
            # Convert hex color to RGB tuple if in pro mode
            bg_rgba = None
            if mode == "pro_mode":
                bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                bg_rgba = bg_rgb + (255,)
            
            output_image = process_image(
                input_image, 
                mode, 
                bg_rgba
            )
            
            buffered = BytesIO()
            output_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return jsonify({
                'image': f"data:image/png;base64,{img_str}"
            })
    
    return render_template('index.html', pro_colors=PRO_COLORS)

if __name__ == '__main__':
    app.run(debug=True)