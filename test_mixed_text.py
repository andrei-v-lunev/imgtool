import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def test_mixed_text_rendering():
    # Create a test image with white background
    img = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load emoji font
    emoji_font = None
    emoji_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/System/Library/Fonts/Apple Color Emoji.ttf"
    ]
    for path in emoji_paths:
        if os.path.exists(path):
            try:
                emoji_font = ImageFont.truetype(path, 160)
                print(f"Loaded emoji font from {path}")
                break
            except Exception as e:
                print(f"Failed to load emoji font {path}: {e}")
    
    if not emoji_font:
        raise Exception("Could not load emoji font")
    
    # Load regular font
    regular_font = None
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                regular_font = ImageFont.truetype(path, 48)
                print(f"Loaded regular font from {path}")
                break
            except Exception as e:
                print(f"Failed to load regular font {path}: {e}")
    
    if not regular_font:
        raise Exception("Could not load regular font")
    
    # Test text with mixed content
    test_text = "Hello 👋 World! ❤️ Testing 123 🌈"
    y = 100
    
    # Function to split text into segments
    def split_text(text):
        segments = []
        current_text = ""
        
        for char in text:
            if ord(char) > 0xFFFF:  # Emoji
                if current_text:
                    segments.append(("text", current_text))
                    current_text = ""
                segments.append(("emoji", char))
            else:
                current_text += char
        if current_text:
            segments.append(("text", current_text))
        return segments
    
    # Draw text segments
    x = 100
    segments = split_text(test_text)
    
    for seg_type, content in segments:
        if seg_type == "emoji":
            # Draw emoji with color
            draw.text((x, y), content, font=emoji_font, embedded_color=True)
            # Get emoji width
            bbox = draw.textbbox((x, y), content, font=emoji_font)
            x += bbox[2] - bbox[0]
        else:
            # Draw regular text
            draw.text((x, y), content, font=regular_font, fill=(0, 0, 0))
            # Get text width
            bbox = draw.textbbox((x, y), content, font=regular_font)
            x += bbox[2] - bbox[0]
    
    # Save test image
    output_path = "mixed_text_test.png"
    img.save(output_path)
    print(f"\nSaved test image to {output_path}")
    
    # Verify the output
    result = Image.open(output_path)
    img_array = np.array(result)
    
    # Check for both black text and colored pixels
    has_black_text = False
    has_color = False
    
    for y in range(100, 200):
        for x in range(100, 700):
            pixel = img_array[y, x]
            if len(pixel) >= 3:
                r, g, b = pixel[:3]
                if r == g == b == 0:  # Black text
                    has_black_text = True
                elif not (r == g == b):  # Colored pixel
                    has_color = True
            if has_black_text and has_color:
                break
    
    assert has_black_text, "No regular text found"
    assert has_color, "No colored emojis found"
    print("Test passed: Found both regular text and colored emojis")

if __name__ == "__main__":
    test_mixed_text_rendering() 