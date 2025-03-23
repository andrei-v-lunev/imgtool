import os
import pytest
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def test_emoji_rendering():
    # Create test image
    img_size = (400, 600)
    image = Image.new('RGBA', img_size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to load emoji font with different sizes
    emoji_font_paths = [
        '/System/Library/Fonts/Apple Color Emoji.ttc',
        '/System/Library/Fonts/Apple Color Emoji.ttf',
        '/Library/Fonts/Apple Color Emoji.ttf'
    ]
    
    emoji_font = None
    font_sizes = [32, 64, 128, 160]  # Try different sizes
    
    for path in emoji_font_paths:
        if os.path.exists(path):
            for size in font_sizes:
                try:
                    emoji_font = ImageFont.truetype(path, size)
                    print(f"Successfully loaded emoji font from {path} at size {size}")
                    break
                except Exception as e:
                    print(f"Failed to load {path} at size {size}: {e}")
        if emoji_font:
            break
    
    assert emoji_font is not None, "Could not load emoji font"
    
    # Test different types of emojis
    test_emojis = [
        "❤️",  # Red Heart
        "💚",  # Green Heart
        "😊",  # Smiling Face
        "👋",  # Waving Hand
        "🌈",  # Rainbow
        "🔥",  # Fire
        "⭐",  # Star
        "✨",  # Sparkles
        "🎨",  # Artist Palette
        "🎯"   # Direct Hit
    ]
    
    y_position = 10
    for i, emoji in enumerate(test_emojis):
        try:
            # Draw emoji
            draw.text((10, y_position), emoji, font=emoji_font, embedded_color=True)
            
            # Get bounding box for verification
            bbox = draw.textbbox((10, y_position), emoji, font=emoji_font)
            
            # Convert to numpy array for color analysis
            emoji_region = np.array(image.crop((bbox[0], bbox[1], bbox[2], bbox[3])))
            
            # Check if the emoji region contains non-grayscale pixels
            r, g, b = emoji_region[..., 0], emoji_region[..., 1], emoji_region[..., 2]
            is_colored = not np.all(r == g) or not np.all(g == b)
            
            print(f"Emoji {emoji} at y={y_position}:")
            print(f"- Bounding box: {bbox}")
            print(f"- Contains color: {is_colored}")
            
            # Assert that emoji contains color
            assert is_colored, f"Emoji {emoji} appears to be grayscale"
            
            y_position += 60
        except Exception as e:
            print(f"Error drawing emoji {emoji}: {e}")
            raise
    
    # Save test image for visual inspection
    image.save("emoji_test_output.png")
    print("Test image saved as emoji_test_output.png")

if __name__ == "__main__":
    test_emoji_rendering() 