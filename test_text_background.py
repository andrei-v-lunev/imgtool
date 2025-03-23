import unittest
from PIL import Image, ImageDraw, ImageFont
import os

class TestTextBackground(unittest.TestCase):
    def setUp(self):
        # Create a test image
        self.image_size = (800, 400)
        self.image = Image.new('RGBA', self.image_size, (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        
        # Load font
        try:
            self.font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
        except:
            self.font = ImageFont.load_default()
            
    def test_background_bounds(self):
        """Test that text background only covers the text area"""
        text = "Test Text"
        text_color = "#ffffff"
        bg_color = "#000000"
        
        # Get text size
        bbox = self.draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw text with background
        x = 100
        y = 100
        padding_x = int(32 * 0.8)  # Same as in app.py
        padding_y = int(32 * 0.4)  # Same as in app.py
        
        # Draw background
        bg_left = x - padding_x
        bg_right = x + text_width + padding_x
        bg_top = y - padding_y
        bg_bottom = y + text_height + padding_y
        
        self.draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], 
                          fill=bg_color)
        
        # Draw text
        self.draw.text((x, y), text, font=self.font, fill=text_color)
        
        # Check background pixels
        # Should be black within text area + padding
        # Should be transparent outside
        self.assertEqual(
            self.image.getpixel((bg_left + 1, bg_top + 1))[:-1], 
            (0, 0, 0),
            "Background color incorrect inside bounds"
        )
        
        self.assertEqual(
            self.image.getpixel((bg_left - 1, bg_top - 1))[3],
            0,
            "Background leaking outside bounds"
        )
        
if __name__ == '__main__':
    unittest.main() 