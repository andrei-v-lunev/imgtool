import os
import pytest
from PIL import Image, ImageDraw, ImageFont
from app import app, measure_text, wrap_text, split_text_and_emojis, draw_rounded_rectangle, get_system_fonts, has_emoji
import unittest
import io

@pytest.fixture
def test_image():
    # Create a test image
    img = Image.new('RGBA', (800, 600), (128, 0, 128, 255))  # Purple background
    return img

@pytest.fixture
def emoji_font():
    # Try loading the emoji font with different sizes
    emoji_sizes = [160, 144, 128, 96, 76, 64, 48, 32]
    font_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS system emoji font
        "/System/Library/Fonts/Apple Color Emoji.ttf",
        "/System/Library/Fonts/AppleColorEmoji.ttf",
        os.path.join('fonts', 'fonts', 'AppleColorEmoji.ttf'),
        "/Library/Fonts/Apple Color Emoji.ttf"
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            print(f"Found font at {path}")
            for size in emoji_sizes:
                try:
                    font = ImageFont.truetype(path, size)
                    print(f"Successfully loaded font at size {size}")
                    return font
                except Exception as e:
                    print(f"Failed to load {path} at size {size}: {e}")
                    continue
    
    pytest.skip("Emoji font not available")

@pytest.fixture
def regular_font():
    # Try to load a regular system font
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf"
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, 24)  # Use a reasonable size for regular text
            except Exception:
                continue
    
    return ImageFont.load_default()

def test_emoji_detection():
    # Test emoji detection function
    assert has_emoji("Hello 👋 World") == True
    assert has_emoji("Hello World") == False
    assert has_emoji("❤️🖕") == True

def test_emoji_text_wrapping(emoji_font, regular_font, test_image):
    # Test text wrapping with emojis
    draw = ImageDraw.Draw(test_image)
    text = "Hello 👋 World ❤️ This is a test 🖕"
    
    # Get the width of a single emoji to set a reasonable max_width
    emoji_width, _ = measure_text("👋", emoji_font, draw)
    max_width = emoji_width * 3  # Allow 3 emojis per line
    
    # Create a custom measure function that uses the appropriate font for each character
    def mixed_measure(text, draw):
        if has_emoji(text):
            # Split text into emoji and non-emoji parts
            parts = []
            current_text = ""
            
            for char in text:
                if ord(char) > 0xFFFF:  # Emoji
                    if current_text:
                        parts.append((current_text, regular_font))
                        current_text = ""
                    parts.append((char, emoji_font))
                else:
                    current_text += char
            if current_text:
                parts.append((current_text, regular_font))
            
            # Measure total width
            total_width = 0
            max_height = 0
            for part_text, part_font in parts:
                w, h = measure_text(part_text.strip(), part_font, draw)
                total_width += w
                max_height = max(max_height, h)
            return total_width, max_height
        return measure_text(text, regular_font, draw)
    
    lines = wrap_text(text, regular_font, max_width, draw, measure_func=mixed_measure)
    
    # Print debug info
    print(f"\nMax width: {max_width}")
    for line in lines:
        width, height = mixed_measure(line, draw)
        print(f"Line: '{line}' - Width: {width}, Height: {height}")
    
    # Verify that emojis are preserved and not split
    assert any("👋" in line for line in lines)
    assert any("❤️" in line for line in lines)
    assert any("🖕" in line for line in lines)
    
    # Verify each line fits within max width
    for line in lines:
        width, _ = mixed_measure(line, draw)
        assert width <= max_width, f"Line '{line}' width {width} exceeds max width {max_width}"
        
    # Verify we have multiple lines (text should wrap)
    assert len(lines) > 1, "Text should be wrapped into multiple lines"

def test_emoji_measurement(emoji_font, test_image):
    # Test text measurement with emojis
    draw = ImageDraw.Draw(test_image)
    
    # Test single emoji
    width1, height1 = measure_text("👋", emoji_font, draw)
    assert width1 > 0
    assert height1 > 0
    
    # Test emoji with text
    width2, height2 = measure_text("Hi 👋", emoji_font, draw)
    assert width2 > width1  # Combined width should be larger
    assert height2 > 0

def test_multiple_emojis_measurement(emoji_font, test_image):
    # Test measurement with multiple emojis
    draw = ImageDraw.Draw(test_image)
    
    # Multiple emojis in sequence
    width, height = measure_text("👋❤️🖕", emoji_font, draw)
    assert width > 0
    assert height > 0
    
    # Multiple emojis with text
    text_width, text_height = measure_text("Hi 👋 Test ❤️ End 🖕", emoji_font, draw)
    assert text_width > width  # Should be wider than just emojis
    assert text_height > 0

class TestImageTextGenerator(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Create test image
        self.test_image = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(self.test_image)
        draw.rectangle([0, 0, 800, 600], fill='lightblue')
        
        # Save test image
        self.test_image_path = 'test_image.png'
        self.test_image.save(self.test_image_path)
        
        # Create outputs directory if it doesn't exist
        if not os.path.exists('outputs'):
            os.makedirs('outputs')

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        
        # Clean up generated outputs
        if os.path.exists('outputs'):
            for file in os.listdir('outputs'):
                if file.startswith('output_'):
                    os.remove(os.path.join('outputs', file))

    def test_homepage(self):
        """Test if homepage loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image Text Generator', response.data)

    def test_image_upload(self):
        """Test image upload functionality"""
        with open(self.test_image_path, 'rb') as img:
            data = {
                'image_file': (io.BytesIO(img.read()), 'test_image.png'),
                'font_name': 'ProximaNova-Bold.ttf',
                'font_size': '24',
                'font_color': '#ffffff',
                'alignment': 'center',
                'text_x': '100',
                'text_y': '100',
                'text_width': '200',
                'text_height': '50'
            }
            response = self.client.post('/', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

    def test_text_background(self):
        """Test text background functionality"""
        with open(self.test_image_path, 'rb') as img:
            data = {
                'image_file': (io.BytesIO(img.read()), 'test_image.png'),
                'font_name': 'ProximaNova-Bold.ttf',
                'font_size': '24',
                'font_color': '#ffffff',
                'alignment': 'center',
                'text_x': '100',
                'text_y': '100',
                'text_width': '200',
                'text_height': '50',
                'text_background': 'on',
                'text_background_color': '#000000',
                'bg_vertical_padding': '10',
                'bg_horizontal_padding': '20',
                'bg_corner_radius': '5'
            }
            response = self.client.post('/', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

    def test_emoji_support(self):
        """Test emoji rendering"""
        with open(self.test_image_path, 'rb') as img:
            data = {
                'image_file': (io.BytesIO(img.read()), 'test_image.png'),
                'font_name': 'Apple Color Emoji.ttc',
                'font_size': '24',
                'font_color': '#ffffff',
                'alignment': 'center',
                'text_x': '100',
                'text_y': '100',
                'text_width': '200',
                'text_height': '50'
            }
            response = self.client.post('/', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

    def test_font_loading(self):
        """Test if system fonts are loaded correctly"""
        response = self.client.get('/fonts')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertIn('ProximaNova-Bold.ttf', response.json)

    def test_invalid_image(self):
        """Test handling of invalid image upload"""
        data = {
            'image_file': (io.BytesIO(b'not an image'), 'test.png'),
            'font_name': 'ProximaNova-Bold.ttf',
            'font_size': '24'
        }
        response = self.client.post('/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)  # Should redirect back

    def test_missing_parameters(self):
        """Test handling of missing parameters"""
        with open(self.test_image_path, 'rb') as img:
            data = {
                'image_file': (io.BytesIO(img.read()), 'test_image.png')
                # Missing other parameters
            }
            response = self.client.post('/', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

    def test_text_wrapping(self):
        """Test text wrapping functionality"""
        test_text = "This is a long text that should be wrapped across multiple lines"
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
        draw = ImageDraw.Draw(Image.new('RGB', (800, 600)))
        lines = wrap_text(test_text, font, 200, draw)
        self.assertTrue(len(lines) > 1)
        
    def test_emoji_splitting(self):
        """Test emoji and text splitting"""
        test_text = "Hello 👋 World 🌍"
        segments = split_text_and_emojis(test_text)
        self.assertEqual(len(segments), 4)
        self.assertEqual(segments[0], ("Hello ", False))
        self.assertEqual(segments[1], ("👋", True))
        self.assertEqual(segments[2], (" World ", False))
        self.assertEqual(segments[3], ("🌍", True))

    def test_rounded_rectangle(self):
        """Test rounded rectangle drawing"""
        img = Image.new('RGBA', (400, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_rounded_rectangle(draw, [50, 50, 350, 250], '#000000', 20)
        # Check if pixels at corners are transparent (indicating rounded corners)
        self.assertEqual(img.getpixel((50, 50))[3], 0)
        self.assertEqual(img.getpixel((350, 50))[3], 0)
        self.assertEqual(img.getpixel((50, 250))[3], 0)
        self.assertEqual(img.getpixel((350, 250))[3], 0)

if __name__ == "__main__":
    pytest.main([__file__])
    unittest.main() 