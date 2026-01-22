"""
Create placeholder icons for the browser extension
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with text"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple "ID" text (Image Describer)
    try:
        # Try to use a default font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "ID"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

if __name__ == "__main__":
    icons_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(icons_dir, "icons"), exist_ok=True)
    
    create_icon(16, os.path.join(icons_dir, "icons", "icon16.png"))
    create_icon(48, os.path.join(icons_dir, "icons", "icon48.png"))
    create_icon(128, os.path.join(icons_dir, "icons", "icon128.png"))
    
    print("All icons created successfully!")

