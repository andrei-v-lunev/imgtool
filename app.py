import os
import sys
import logging
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, jsonify
from PIL import Image, ImageDraw, ImageFont
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
import base64
from subprocess import check_output

# Configure logging to output to the console
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO or WARNING in production as needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secure secret key

# --- Google Sheets API Configuration ---
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'access.json'  # Ensure this file is in the same directory as app.py
# Memorized spreadsheet key:
SPREADSHEET_KEY = '1XEt1-TN_0_-_qZZT5_0vG4MBbOUC57YqPGR1HuhLbvY'
SHEET_NAME = 'Sheet1'  # Update if your sheet tab is named differently

def has_emoji(text):
    """Check if text contains any emoji characters."""
    return any(ord(char) > 0xFFFF for char in text)

def measure_text(text, font, draw):
    """
    Measure the width and height of the given text using the provided font and draw object.
    Uses textbbox for more accurate measurements, especially with emoji fonts.
    Returns a tuple (width, height).
    """
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except Exception as e:
        logger.error("textbbox failed: %s", e)
        # Fallback to a rough estimate if all else fails
        return (len(text) * (font.size // 2), font.size)

def wrap_text(text, font, max_width, draw, measure_func=None):
    """
    Wrap the text into multiple lines so that each line does not exceed max_width.
    Returns a list of lines.
    
    Args:
        text: The text to wrap
        font: The default font to use
        max_width: Maximum width in pixels
        draw: ImageDraw object
        measure_func: Optional custom function to measure text width
    """
    if measure_func is None:
        measure_func = lambda t, d: measure_text(t, font, d)
        
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        w, _ = measure_func(test_line, draw)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def get_all_sheets():
    """
    Get a list of all available sheets in the spreadsheet.
    """
    logger.debug("Loading credentials from %s", CREDENTIALS_FILE)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    logger.debug("Authorized with Google Sheets")
    
    sh = gc.open_by_key(SPREADSHEET_KEY)
    logger.debug("Opened spreadsheet with key: %s", SPREADSHEET_KEY)
    
    worksheets = sh.worksheets()
    return [ws.title for ws in worksheets]

def get_texts_from_sheet(sheet_name=None):
    """
    Fetch a list of texts from the first column of the specified Google Sheet.
    
    Args:
        sheet_name: Name of the sheet to fetch texts from. If None, uses default SHEET_NAME.
    """
    logger.debug("Loading credentials from %s", CREDENTIALS_FILE)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    logger.debug("Authorized with Google Sheets")
    
    sh = gc.open_by_key(SPREADSHEET_KEY)
    logger.debug("Opened spreadsheet with key: %s", SPREADSHEET_KEY)
    
    worksheet = sh.worksheet(sheet_name or SHEET_NAME)
    texts = worksheet.col_values(1)
    # Optionally, skip the header row if the first cell is "text"
    if texts and texts[0].lower() == 'text':
        texts = texts[1:]
    logger.debug("Fetched texts: %s", texts)
    return texts

def split_text_and_emojis(text):
    segments = []
    current_segment = ""
    is_emoji = False
    
    for char in text:
        char_is_emoji = ord(char) > 0xFFFF
        if char_is_emoji != is_emoji and current_segment:
            segments.append((current_segment, is_emoji))
            current_segment = ""
        current_segment += char
        is_emoji = char_is_emoji
    
    if current_segment:
        segments.append((current_segment, is_emoji))
    return segments

def draw_rounded_rectangle(draw, coords, color, radius):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = coords
    
    # Draw main rectangle
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=color)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=color)
    
    # Draw four corners
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=color)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=color)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=color)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=color)

def get_system_fonts():
    try:
        # Get fonts from system locations on macOS
        font_paths = [
            '/System/Library/Fonts',
            '/Library/Fonts',
            os.path.expanduser('~/Library/Fonts')
        ]
        
        fonts = []
        for path in font_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith(('.ttf', '.otf')):
                        fonts.append(file)
        
        # Add ProximaNova as the first option
        if 'ProximaNova-Bold.ttf' in fonts:
            fonts.remove('ProximaNova-Bold.ttf')
        fonts.insert(0, 'ProximaNova-Bold.ttf')
        
        return sorted(list(set(fonts)))
    except Exception as e:
        print(f"Error getting system fonts: {e}")
        return ['ProximaNova-Bold.ttf']

@app.route('/fonts')
def get_fonts():
    return jsonify(get_system_fonts())

@app.route('/sheets')
def get_sheets():
    try:
        sheets = get_all_sheets()
        return jsonify(sheets)
    except Exception as e:
        logger.error(f"Error fetching sheets: {str(e)}")
        return jsonify([SHEET_NAME])

@app.route('/', methods=['GET', 'POST'])
def index():
    # Get available sheets
    try:
        sheets = get_all_sheets()
        sheet_name = request.args.get('sheet') or sheets[0]  # Use first sheet if none selected
    except Exception as e:
        logger.error(f"Error fetching sheets: {str(e)}")
        sheets = [SHEET_NAME]
        sheet_name = SHEET_NAME

    # Get sample text from Google Sheet
    try:
        texts = get_texts_from_sheet(sheet_name)
        sample_text = texts[0].strip('"') if texts else "Sample text will appear here"
    except Exception as e:
        logger.error(f"Error fetching sample text: {str(e)}")
        sample_text = "Sample text will appear here"

    fonts = get_system_fonts()

    if request.method == 'POST':
        # Handle image upload case
        if 'image_file' not in request.files:
            flash('No file part.')
            logger.error("No file part in the request")
            return redirect(request.url)
            
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file.')
            logger.error("No file selected")
            return redirect(request.url)
        
        # Get form parameters
        sheet_name = request.form.get('sheet_name', SHEET_NAME)
        font_name = request.form.get('font_name', 'ProximaNova-Bold.ttf')
        font_size = int(request.form.get('font_size', 24))
        font_color = request.form.get('font_color', '#ffffff')
        alignment = request.form.get('alignment', 'center').lower()
        text_background = request.form.get('text_background') == 'on'
        text_background_color = request.form.get('text_background_color', '#000000')
        bg_vertical_padding = int(request.form.get('bg_vertical_padding', 10))
        bg_horizontal_padding = int(request.form.get('bg_horizontal_padding', 20))
        bg_corner_radius = int(request.form.get('bg_corner_radius', 5))
        
        # Get text position and dimensions
        text_x = int(request.form.get('text_x', 0))
        text_y = int(request.form.get('text_y', 0))
        text_width = int(request.form.get('text_width', 0))
        text_height = int(request.form.get('text_height', 0))
        
        # Save uploaded file
        upload_path = os.path.join('uploads', file.filename)
        file.save(upload_path)
        
        try:
            # Get texts from the selected sheet
            texts = get_texts_from_sheet(sheet_name)
            logger.info(f"Starting to process {len(texts)} texts from sheet '{sheet_name}'")
            
            # Process each text
            results = []
            processed_count = 0
            for text in texts:
                try:
                    processed_count += 1
                    logger.info(f"Processing image {processed_count} of {len(texts)}")
                    
                    # Open the base image
                    image = Image.open(upload_path).convert("RGBA")
                    txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
                    draw = ImageDraw.Draw(txt_layer)
                    
                    # Load fonts
                    emoji_font = None
                    regular_font = None
                    
                    # Try to load emoji font with different sizes
                    emoji_font_paths = [
                        '/System/Library/Fonts/Apple Color Emoji.ttc',
                        '/System/Library/Fonts/Apple Color Emoji.ttf',
                        '/Library/Fonts/Apple Color Emoji.ttf'
                    ]
                    emoji_sizes = [32, 64, 128, 160]
                    
                    for path in emoji_font_paths:
                        if os.path.exists(path):
                            for size in emoji_sizes:
                                try:
                                    emoji_font = ImageFont.truetype(path, size)
                                    break
                                except Exception as e:
                                    continue
                        if emoji_font:
                            break
                    
                    # Load regular font
                    try:
                        regular_font = ImageFont.truetype(os.path.join('fonts', font_name), font_size)
                    except OSError:
                        try:
                            regular_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
                        except OSError:
                            regular_font = ImageFont.load_default()
                            logger.error("Failed to load fonts, using default")
                    
                    # Split text into lines based on width
                    lines = wrap_text(text, regular_font, text_width, draw)
                    current_y = text_y
                    padding_x = int(font_size * 0.8)  # Horizontal padding
                    padding_y = int(font_size * 0.4)  # Vertical padding
                    line_height = int(font_size * 1.5)  # Line spacing
                    
                    for line in lines:
                        # Split line into segments (text and emojis)
                        segments = split_text_and_emojis(line)
                        
                        # Calculate total line width including all segments
                        line_width = 0
                        for segment, is_emoji in segments:
                            font = emoji_font if is_emoji else regular_font
                            bbox = draw.textbbox((0, 0), segment, font=font)
                            segment_width = bbox[2] - bbox[0]
                            line_width += segment_width
                        
                        # Calculate x position based on alignment
                        if alignment == 'center':
                            x = text_x + (text_width - line_width) // 2
                        elif alignment == 'right':
                            x = text_x + text_width - line_width
                        else:  # left alignment
                            x = text_x
                        
                        # Draw background for this line if enabled
                        if text_background:
                            bg_color = text_background_color
                            # Convert hex color to RGBA with full opacity
                            if bg_color.startswith('#'):
                                r = int(bg_color[1:3], 16)
                                g = int(bg_color[3:5], 16)
                                b = int(bg_color[5:7], 16)
                                bg_color = (r, g, b, 255)  # Full opacity
                            
                            # Get line height including any emoji
                            max_height = font_size
                            for segment, is_emoji in segments:
                                font = emoji_font if is_emoji else regular_font
                                bbox = draw.textbbox((0, 0), segment, font=font)
                                height = bbox[3] - bbox[1]
                                max_height = max(max_height, height)
                            
                            # Draw background with padding, ensuring it aligns with text
                            bg_left = x - padding_x
                            bg_right = x + line_width + padding_x
                            bg_top = current_y - padding_y
                            bg_bottom = current_y + max_height + padding_y
                            
                            draw_rounded_rectangle(draw, (bg_left, bg_top, bg_right, bg_bottom), bg_color, bg_corner_radius)
                        
                        # Draw each segment
                        segment_x = x
                        for segment, is_emoji in segments:
                            if is_emoji:
                                draw.text((segment_x, current_y), segment, font=emoji_font, embedded_color=True)
                                bbox = draw.textbbox((segment_x, current_y), segment, font=emoji_font)
                            else:
                                draw.text((segment_x, current_y), segment, font=regular_font, fill=font_color)
                                bbox = draw.textbbox((segment_x, current_y), segment, font=regular_font)
                            segment_x += bbox[2] - bbox[0]
                        
                        current_y += line_height
                    
                    # Composite text layer onto base image
                    result = Image.alpha_composite(image, txt_layer)
                    
                    # Save result
                    base_filename = os.path.splitext(file.filename)[0]  # Get filename without extension
                    output_filename = f"{base_filename}_HD-{len(results)+1:02d}.png"
                    output_path = os.path.join('outputs', output_filename)
                    result.save(output_path)
                    
                    # Only store base64 preview for first 5 images
                    if len(results) < 5:
                        img_io = BytesIO()
                        result.save(img_io, 'PNG')
                        img_io.seek(0)
                        image_data = base64.b64encode(img_io.getvalue()).decode()
                        results.append({'filename': output_filename, 'image_data': image_data})
                    else:
                        results.append({'filename': output_filename, 'image_data': None})
                
                except Exception as e:
                    logger.error(f"Error processing text '{text}': {str(e)}")
                    continue
            
            if not results:
                flash("Failed to generate any images")
                return redirect(request.url)
            
            logger.info(f"Successfully processed {processed_count} images out of {len(texts)} texts")
            return render_template('index.html', results=results, fonts=fonts, sheets=sheets, total_processed=processed_count)
            
        except Exception as e:
            flash(f"Error processing image: {str(e)}")
            logger.error(f"Error processing image: {str(e)}")
            return redirect(request.url)
    
    return render_template('index.html', sample_text=sample_text, fonts=fonts, sheets=sheets)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('outputs', filename)
    logger.debug("Downloading file: %s", file_path)
    return send_file(file_path, as_attachment=True)

@app.route('/generated/')
def generated_images():
    files = []
    generated_dir = os.path.join(app.static_folder, 'generated')
    for filename in os.listdir(generated_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            file_url = url_for('static', filename=f'generated/{filename}')
            files.append({
                'url': file_url,
                'name': filename
            })
    return render_template('generated.html', files=files)

@app.route('/sample_text/<sheet_name>')
def get_sample_text(sheet_name):
    try:
        texts = get_texts_from_sheet(sheet_name)
        sample_text = texts[0].strip('"') if texts else "Sample text will appear here"
        return jsonify({'sample_text': sample_text})
    except Exception as e:
        logger.error(f"Error fetching sample text: {str(e)}")
        return jsonify({'sample_text': "Sample text will appear here"}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    app.run(debug=True, port=5005)