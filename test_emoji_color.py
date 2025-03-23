import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def test_emoji_color():
    # Create a test image with white background for better contrast
    img = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to load the emoji font
    font_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/System/Library/Fonts/Apple Color Emoji.ttf",
        "/Library/Fonts/Apple Color Emoji.ttf"
    ]
    
    emoji_font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                emoji_font = ImageFont.truetype(path, 160)
                print(f"Loaded emoji font from {path}")
                break
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    
    if not emoji_font:
        raise Exception("Could not load emoji font")
    
    # Draw some emojis with different colors
    emojis = [
        "❤️",  # red heart
        "💚",  # green heart
        "💙",  # blue heart
        "🌈",  # rainbow
        "🔥"   # fire
    ]
    
    y = 100
    for emoji in emojis:
        print(f"\nTesting emoji: {emoji}")
        # Draw with embedded color enabled
        draw.text((100, y), emoji, font=emoji_font, embedded_color=True)
        y += 100
    
    # Save the test image
    output_path = "emoji_color_test.png"
    img.save(output_path)
    print(f"\nSaved test image to {output_path}")
    
    # Load the saved image and check for color
    result = Image.open(output_path)
    img_array = np.array(result)
    
    # Function to check if a pixel is colored
    def is_colored(pixel):
        if len(pixel) >= 3:
            r, g, b = pixel[:3]
            return not (r == g == b)  # True if not grayscale
        return False
    
    # Check each emoji area for color
    colored_emojis = []
    y = 100
    for emoji in emojis:
        area = img_array[y:y+80, 100:200]  # Check a region around each emoji
        has_color = False
        for i in range(area.shape[0]):
            for j in range(area.shape[1]):
                if is_colored(area[i, j]):
                    has_color = True
                    colored_emojis.append(emoji)
                    print(f"Found color in emoji {emoji} at offset ({i}, {j}): RGB{tuple(area[i, j][:3])}")
                    break
            if has_color:
                break
        y += 100
    
    print("\nResults:")
    print(f"Total emojis tested: {len(emojis)}")
    print(f"Emojis with color: {len(colored_emojis)}")
    print(f"Colored emojis: {' '.join(colored_emojis)}")
    
    assert len(colored_emojis) > 0, "No colored emojis found in the rendering"

if __name__ == "__main__":
    test_emoji_color() 