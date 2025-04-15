# Image Text Generator

A tool for adding text from Google Sheets to images.

## Architecture Improvements

The codebase has been restructured following modern web development principles:

### 1. Separation of Concerns

- **HTML**: Template structure (`templates/index.html`)
- **CSS**: Styling (`static/css/style.css`)
- **JavaScript**: Application logic (`static/js/*`)

### 2. Component-Based Architecture

Components are structured in a modular way:

- **FileUploader**: Handles file selection and validation
- **ImagePreview**: Manages image preview and selection box
- **StyleSettings**: Controls font and style settings

### 3. State Management

A lightweight reactive state system manages application state:

```javascript
// Example usage:
import { state } from './state.js';

// Update state
state.set('settings.fontSize', 24);

// Subscribe to changes
state.subscribe('settings', () => {
  updateUI();
});
```

### 4. Error Handling

Centralized error handling with toast notifications:

```javascript
import { showErrorToast, showSuccessToast } from './utils/errorHandler.js';

try {
  // Some operation
  showSuccessToast('Operation completed');
} catch (error) {
  showErrorToast(`Error: ${error.message}`);
}
```

### 5. Utilities

Common functionality is broken into utility modules:

- **fileUtils.js**: File validation and handling
- **errorHandler.js**: Error handling and notifications

## Project Structure

```
imgtool/
├── app.py                  # Flask application
├── static/
│   ├── css/
│   │   └── style.css       # Styles
│   ├── js/
│   │   ├── app.js          # Main application
│   │   ├── state.js        # State management
│   │   ├── components/     # UI components
│   │   │   ├── fileUploader.js
│   │   │   ├── imagePreview.js
│   │   │   └── styleSettings.js
│   │   └── utils/          # Utility modules
│   │       ├── errorHandler.js
│   │       └── fileUtils.js
│   └── test.html           # Component test page
└── templates/
    ├── index.html          # Main application template
    ├── generated.html      # Generated images view
    └── results.html        # Results view
```

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Open in browser: `http://localhost:5000`

## Testing

A test page is available at `/static/test.html` that verifies:

- State management
- File validation
- Error handling

## Future Improvements

Planned architectural improvements:

1. Full TypeScript implementation
2. Unit and integration tests
3. WebGL-based image processing
4. Service worker for offline support
5. Web workers for heavy operations

## Credits

Developed by ImgTool Team 