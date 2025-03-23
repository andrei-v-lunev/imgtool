import os
import pytest
from app import app
from PIL import Image
from io import BytesIO

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_image_generation(client):
    # Test data
    test_data = {
        'text': 'Hello 👋 World! ❤️',
        'font': 'Arial',
        'font_size': '72',
        'max_width': '800'
    }
    
    # Make POST request
    response = client.post('/', data=test_data)
    
    # Check response status
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    
    # Verify image content
    img_data = BytesIO(response.data)
    img = Image.open(img_data)
    
    # Check image properties
    assert img.mode == 'RGBA'
    assert img.size[0] > 0
    assert img.size[1] > 0
    
    # Convert image to array and check if it's not empty
    img_array = list(img.getdata())
    non_white_pixels = [p for p in img_array if p != (255, 255, 255, 255)]
    assert len(non_white_pixels) > 0, "Image appears to be blank"

def test_empty_text(client):
    test_data = {
        'text': '',
        'font': 'Arial',
        'font_size': '72',
        'max_width': '800'
    }
    response = client.post('/', data=test_data)
    assert response.status_code == 200
    
    # Should still return a valid image
    img_data = BytesIO(response.data)
    img = Image.open(img_data)
    assert img.mode == 'RGBA' 