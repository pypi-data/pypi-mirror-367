"""
Create Simple Images for PowerPoint Templates

This script generates simple placeholder images that can be used
in PowerPoint presentations to demonstrate image capabilities.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_simple_image(width, height, text, filename, bg_color=(70, 130, 180), text_color=(255, 255, 255)):
    """Create a simple image with text"""
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save image
    img.save(filename)
    print(f"✅ Created: {filename}")
    return filename

def create_chart_image(width, height, filename):
    """Create a simple chart-like image"""
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw chart background
    draw.rectangle([20, 20, width-20, height-20], fill=(240, 240, 240), outline=(100, 100, 100))
    
    # Draw some bars to simulate a chart
    bar_width = 40
    bar_spacing = 20
    start_x = 60
    base_y = height - 60
    
    # Sample data bars
    bars = [120, 180, 140, 220, 160]
    colors = [(70, 130, 180), (100, 150, 200), (130, 170, 220), (160, 190, 240), (190, 210, 250)]
    
    for i, height_val in enumerate(bars):
        x = start_x + i * (bar_width + bar_spacing)
        y = base_y - height_val
        draw.rectangle([x, y, x + bar_width, base_y], fill=colors[i])
    
    # Add title
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2 - 50, 30), "Sample Chart", fill=(50, 50, 50), font=font)
    
    img.save(filename)
    print(f"✅ Created: {filename}")
    return filename

def create_icon_image(size, text, filename, bg_color=(100, 150, 200)):
    """Create a simple icon-style image"""
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    margin = 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(255, 255, 255), outline=(50, 50, 50))
    
    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(50, 50, 50), font=font)
    
    img.save(filename)
    print(f"✅ Created: {filename}")
    return filename

def main():
    """Create a set of simple images for PowerPoint templates"""
    print("=== Creating Simple Images for PowerPoint Templates ===\n")
    
    # Create images directory if it doesn't exist
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 Created directory: {images_dir}")
    
    images_created = []
    
    # Create various types of images
    images_created.append(create_simple_image(400, 300, "Company\nLogo", f"{images_dir}/company_logo.png", (70, 130, 180)))
    images_created.append(create_simple_image(600, 400, "Product\nOverview", f"{images_dir}/product_overview.png", (100, 150, 100)))
    images_created.append(create_simple_image(500, 350, "Team\nPhoto", f"{images_dir}/team_photo.png", (150, 100, 150)))
    images_created.append(create_simple_image(450, 300, "Process\nDiagram", f"{images_dir}/process_diagram.png", (200, 150, 100)))
    images_created.append(create_chart_image(500, 300, f"{images_dir}/sample_chart.png"))
    images_created.append(create_simple_image(400, 250, "Results\nSummary", f"{images_dir}/results_summary.png", (120, 120, 120)))
    
    # Create icon-style images with simple symbols instead of emojis
    images_created.append(create_icon_image(64, "CHART", f"{images_dir}/chart_icon.png", (70, 130, 180)))
    images_created.append(create_icon_image(64, "GROWTH", f"{images_dir}/growth_icon.png", (100, 150, 100)))
    images_created.append(create_icon_image(64, "IDEA", f"{images_dir}/idea_icon.png", (200, 150, 100)))
    images_created.append(create_icon_image(64, "TARGET", f"{images_dir}/target_icon.png", (150, 100, 150)))
    
    print(f"\n🎉 Successfully created {len(images_created)} images!")
    print(f"📁 Images saved in: {images_dir}/")
    
    return images_created

if __name__ == "__main__":
    main() 