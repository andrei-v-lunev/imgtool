import os
import sys
import logging
from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from PIL import Image, ImageDraw, ImageFont
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

def measure_text(text, font, draw):
    """
    Measure the width and height of the given text using the provided font and draw object.
    Tries using draw.textsize() and falls back to draw.textbbox() if needed.
    Returns a tuple (width, height).
    """
    try:
        return draw.textsize(text, font=font)
    except Exception as e:
        logger.warning("draw.textsize failed: %s; falling back to textbbox.", e)
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def wrap_text(text, font, max_width, draw):
    """
    Wrap the text into multiple lines so that each line does not exceed max_width.
    Returns a list of lines.
    """
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        w, _ = measure_text(test_line, font, draw)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def get_texts_from_sheet():
    """
    Fetch a list of texts from the first column of the specified Google Sheet.
    """
    logger.debug("Loading credentials from %s", CREDENTIALS_FILE)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    logger.debug("Authorized with Google Sheets")
    
    sh = gc.open_by_key(SPREADSHEET_KEY)
    logger.debug("Opened spreadsheet with key: %s", SPREADSHEET_KEY)
    
    worksheet = sh.worksheet(SHEET_NAME)
    texts = worksheet.col_values(1)
    # Optionally, skip the header row if the first cell is "text"
    if texts and texts[0].lower() == 'text':
        texts = texts[1:]
    logger.debug("Fetched texts: %s", texts)
    return texts

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve and validate form data
        try:
            font_size = int(request.form.get('font_size', 24))
            # Get text position and dimensions
            text_x = int(request.form.get('text_x', 0))
            text_y = int(request.form.get('text_y', 0))
            text_width = int(request.form.get('text_width', 0))
            text_height = int(request.form.get('text_height', 0))
            logger.debug("Form parameters - Font size: %d, Position: (%d, %d), Size: %dx%d", 
                         font_size, text_x, text_y, text_width, text_height)
        except ValueError as e:
            flash("Font size and positions must be numeric.")
            logger.error("ValueError in form data: %s", e)
            return redirect(request.url)
            
        # Set default font color to white (#ffffff)
        font_color = request.form.get('font_color', '#ffffff')
        # Default alignment is center
        alignment = request.form.get('alignment', 'center').lower()
        font_name = request.form.get('font_name', '').strip()
        if not font_name:
            font_name = "ProximaNova-Bold.ttf"
            logger.debug("No font name provided, defaulting to ProximaNova-Bold.ttf")
        
        # Retrieve text background settings from form:
        text_background_enabled = request.form.get('text_background') == 'on'
        text_background_color = request.form.get('text_background_color', '#000000')  # default background color is black

        # Handle image file upload
        if 'image_file' not in request.files:
            flash('No file part.')
            logger.error("No file part in the request")
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file.')
            logger.error("No file selected")
            return redirect(request.url)

        upload_path = os.path.join('uploads', file.filename)
        file.save(upload_path)
        logger.info("Uploaded image saved at: %s", upload_path)

        # Retrieve texts from the Google Sheet
        try:
            texts = get_texts_from_sheet()
        except Exception as e:
            flash(f"Error accessing Google Sheet: {e}")
            logger.error("Error accessing Google Sheet: %s", e)
            return redirect(request.url)

        output_files = []
        for idx, text in enumerate(texts):
            logger.debug("Processing text #%d: %s", idx, text)
            try:
                # Open the base image and convert it to RGBA for transparency support
                image = Image.open(upload_path).convert("RGBA")
                logger.debug("Opened image: %s", upload_path)
                
                # Create a transparent layer for text
                txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # Try to load the specified font
                try:
                    font = ImageFont.truetype(font_name, font_size)
                except IOError as e:
                    logger.warning("Font '%s' not found: %s. Attempting to load ProximaNova-Bold.ttf", font_name, e)
                    try:
                        font = ImageFont.truetype("ProximaNova-Bold.ttf", font_size)
                    except IOError as e:
                        try:
                            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                        except IOError as e:
                            font = ImageFont.load_default()
                            flash("Could not load a TrueType font. Using default font, which may not reflect the specified size.")
                            logger.error("Could not load ProximaNova-Bold.ttf or DejaVuSans.ttf: %s. Using default font.", e)
                
                # Determine maximum width for text wrapping from the selection area
                max_text_width = text_width if text_width > 0 else int(image.width * 0.9)
                logger.debug("Max text width for wrapping: %d", max_text_width)
                
                # Wrap text to fit in the selection area
                lines = wrap_text(text, font, max_text_width, draw)
                logger.debug("Wrapped text into lines: %s", lines)
                
                # Calculate total height of the text block (line heights + spacing)
                line_spacing = 4  # pixels between lines
                line_heights = []
                for line in lines:
                    _, h = measure_text(line, font, draw)
                    line_heights.append(h)
                total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
                
                # For vertical positioning based on selection area
                if text_height > 0:
                    # Center the text vertically within the selection area
                    y_start = text_y + (text_height - total_text_height) // 2
                else:
                    # If no height specified, center at the given y position
                    y_start = text_y - total_text_height // 2
                
                # If background is enabled, draw the background rectangle using the selection area
                if text_background_enabled:
                    # Use the selection area as the background if defined
                    if text_width > 0 and text_height > 0:
                        bg_box = (text_x, text_y, text_x + text_width, text_y + text_height)
                    else:
                        # Compute the bounds of the text
                        x_positions = []
                        for line in lines:
                            line_width, _ = measure_text(line, font, draw)
                            if alignment == 'center':
                                x_line = text_x - line_width // 2
                            elif alignment == 'right':
                                x_line = text_x - line_width
                            else:  # left alignment
                                x_line = text_x
                            x_positions.append((x_line, x_line + line_width))
                        min_x = min(x for x, _ in x_positions)
                        max_x = max(x_end for _, x_end in x_positions)
                        padding = 5  # pixels of padding around the text
                        bg_box = (min_x - padding, y_start - padding,
                                max_x + padding, y_start + total_text_height + padding)
                    
                    logger.debug("Drawing background rectangle at: %s with color: %s", bg_box, text_background_color)
                    draw.rectangle(bg_box, fill=text_background_color)
                
                # Draw each line of text, aligning according to selection
                current_y = y_start
                for i, line in enumerate(lines):
                    line_width, line_height = measure_text(line, font, draw)
                    
                    # Calculate x position based on alignment and selection area
                    if text_width > 0:
                        if alignment == 'center':
                            x = text_x + (text_width - line_width) // 2
                        elif alignment == 'right':
                            x = text_x + text_width - line_width
                        else:  # left alignment
                            x = text_x
                    else:
                        # If no width specified, use the old logic
                        if alignment == 'center':
                            x = text_x - line_width // 2
                        elif alignment == 'right':
                            x = text_x - line_width
                        else:  # left alignment
                            x = text_x
                    
                    logger.debug("Drawing line '%s' at (%d, %d)", line, x, current_y)
                    draw.text((x, current_y), line, font=font, fill=font_color)
                    current_y += line_height + line_spacing

                # Composite the text layer onto the base image
                combined = Image.alpha_composite(image, txt_layer)
                output_filename = f"output_{idx}_{file.filename}"
                output_path_full = os.path.join('outputs', output_filename)
                combined.convert("RGB").save(output_path_full)
                output_files.append(output_filename)
                logger.info("Generated image saved as: %s", output_filename)
            except Exception as e:
                flash(f"Error processing text '{text}': {e}")
                logger.error("Error processing text '%s': %s", text, e)
                continue

        logger.debug("Final list of output files: %s", output_files)
        return render_template('results.html', files=output_files)
    
    # GET request returns the main form template
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('outputs', filename)
    logger.debug("Downloading file: %s", file_path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    app.run(debug=True)