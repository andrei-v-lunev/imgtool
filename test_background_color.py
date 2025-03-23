import unittest
from PIL import Image, ImageDraw, ImageFont
import os

class TestBackgroundColor(unittest.TestCase):
    def setUp(self):
        self.image_size = (400, 200)
        self.image = Image.new('RGBA', self.image_size, (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        
        try:
            self.font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
        except:
            self.font = ImageFont.load_default()
    
    def test_background_opacity(self):
        """Test that background color maintains full opacity when no transparency is specified"""
        text = "Test Text"
        text_color = "#ffffff"
        bg_color = "#000000"  # Pure black
        
        # Draw background rectangle
        x, y = 50, 50
        bbox = self.draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding_x = int(32 * 0.8)
        padding_y = int(32 * 0.4)
        
        # Convert hex color to RGBA (should be fully opaque)
        r = int(bg_color[1:3], 16)
        g = int(bg_color[3:5], 16)
        b = int(bg_color[5:7], 16)
        bg_rgba = (r, g, b, 255)  # Full opacity
        
        # Draw background
        self.draw.rectangle([
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            y + text_height + padding_y
        ], fill=bg_rgba)
        
        # Check pixel color - should be pure black with full opacity
        pixel = self.image.getpixel((x, y))
        self.assertEqual(
            pixel,
            (0, 0, 0, 255),
            f"Background color should be pure black (0,0,0,255), got {pixel}"
        )
        
        # Test multiple points to ensure consistency
        pixel2 = self.image.getpixel((x + text_width//2, y + text_height//2))
        self.assertEqual(
            pixel2,
            (0, 0, 0, 255),
            f"Background color inconsistent at center point, got {pixel2}"
        )

if __name__ == '__main__':
    unittest.main() 