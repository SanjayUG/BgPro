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
    "slate": "#2a2a3b",
    "emerald": "#0a3b3b"
}

def process_image(input_image, mode, bg_color=None, shadow_intensity=100):
    # Remove background
    output_image = remove(input_image)
    
    if mode == "remove_bg":
        return output_image
        
    elif mode == "pro_mode" and output_image.mode == 'RGBA':
        # Convert shadow_intensity to enhancement factors
        # Higher intensity = thicker/bolder shadow, lower intensity = thinner shadow
        shadow_factor = float(shadow_intensity) / 100.0
        blur_radius = max(0.5, 4.0 * shadow_factor)  # Adjust blur based on intensity
        
        # Calculate expansion size - must be odd number for MaxFilter
        # Ensure it's at least 3 (minimum valid size) and odd
        raw_size = max(3, int(7 * shadow_factor))
        expansion_size = raw_size if raw_size % 2 == 1 else raw_size + 1
        
        # Split channels
        r, g, b, a = output_image.split()
        
        # Create the mask for the object
        shadow = a.point(lambda x: 255 if x > 20 else 0)  # Lower threshold to capture more of the object
        
        # Expand the mask to control the thickness of the white glow
        if shadow_factor > 0.1:  # Apply expansion at lower threshold for more consistent glow
            # Apply multiple passes for smoother expansion at higher intensities
            expansion_passes = max(1, min(3, int(shadow_factor * 3)))
            for _ in range(expansion_passes):
                shadow = shadow.filter(ImageFilter.MaxFilter(expansion_size))
            
        # Apply blur to create soft glow effect - less blur for crisper white
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Ensure maximum brightness for pitch white glow
        # Higher intensity makes the white more prominent
        shadow_opacity = min(255, int(255 * shadow_factor))
        shadow = shadow.point(lambda x: shadow_opacity if x > 50 else 0)
        
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
        shadow_intensity = request.form.get('shadow_intensity', '100')
        
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
                bg_rgba, 
                shadow_intensity
            )
            
            buffered = BytesIO()
            output_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return jsonify({
                'image': f"data:image/png;base64,{img_str}",
                'shadow_intensity': shadow_intensity
            })
    
    return render_template('index.html', pro_colors=PRO_COLORS)

if __name__ == '__main__':
    app.run(debug=True)