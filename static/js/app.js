/**
 * Main application entry point
 */
import { state } from './state.js';
import { FileUploader } from './components/fileUploader.js';
import { ImagePreview } from './components/imagePreview.js';
import { StyleSettings } from './components/styleSettings.js';
import { initErrorHandling, showErrorToast, showSuccessToast } from './utils/errorHandler.js';
import { validateImageFile } from './utils/fileUtils.js';

/**
 * Initialize the app when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
  // Initialize error handling
  initErrorHandling();
  
  // Get sample text from the document
  const sampleText = window.sampleText || "Sample text will appear here";
  
  try {
    // Initialize UI components
    initUI(sampleText);
    
    // Initialize modals
    initModals();
    
    // Initialize sheet selection
    initSheetSelector();
    
    console.info('App initialized successfully');
  } catch (error) {
    console.error('Error initializing app:', error);
    showErrorToast(`Failed to initialize app: ${error.message}`);
  }
});

/**
 * Initialize all UI components
 * @param {string} sampleText - Sample text to display in previews
 */
function initUI(sampleText) {
  // Initialize file uploader
  const uploadSection = document.querySelector('.upload-area');
  if (uploadSection) {
    const fileUploader = new FileUploader(uploadSection, (file, preview) => {
      console.log('File uploaded:', file.name);
    });
  }
  
  // Initialize image preview
  const previewContainer = document.getElementById('preview-container');
  if (previewContainer) {
    const imagePreview = new ImagePreview(previewContainer, sampleText);
    
    // Listen for selection changes to trigger preview updates
    state.subscribe('selection', () => {
      imagePreview.updatePreview();
    });
    
    // Listen for setting changes to trigger preview updates
    state.subscribe('settings', () => {
      imagePreview.updatePreview();
    });
  }
  
  // Initialize style settings
  const styleSettingsPanel = document.querySelector('.panel-left');
  if (styleSettingsPanel) {
    const styleSettings = new StyleSettings(styleSettingsPanel);
    
    // Setup eyedroppers
    styleSettings.setupEyedropper('font_color', 'font_color_hex', 'settings.fontColor');
    styleSettings.setupEyedropper('text_background_color', 'text_background_color_hex', 'settings.textBackgroundColor');
  }
  
  // Set up form submission
  const form = document.getElementById('imageForm');
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }
}

/**
 * Initialize modal dialogs
 */
function initModals() {
  const modal = document.getElementById('helpModal');
  const helpBtn = document.getElementById('helpBtn');
  const closeBtn = document.querySelector('.modal-close');

  if (helpBtn && modal) {
    helpBtn.addEventListener('click', () => {
      modal.style.display = "block";
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.style.display = "none";
    });
  }

  // Close modal when clicking outside
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}

/**
 * Initialize sheet selector functionality
 */
function initSheetSelector() {
  const sheetSelect = document.getElementById('sheet_name');
  
  if (sheetSelect) {
    sheetSelect.addEventListener('change', function() {
      const selectedSheet = this.value;
      state.set('settings.sheetName', selectedSheet);
      
      // Fetch new sample text
      fetch(`/sample_text/${selectedSheet}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          // Update sample text in preview
          const dummyText = document.getElementById('dummy-text');
          if (dummyText) {
            let textSpan = dummyText.querySelector('span');
            if (!textSpan) {
              textSpan = document.createElement('span');
              dummyText.innerHTML = '';
              dummyText.appendChild(textSpan);
            }
            textSpan.textContent = data.sample_text;
            
            // Update global sample text variable
            window.sampleText = data.sample_text;
            
            // Update preview if selection box is visible
            const selectionBox = document.getElementById('selection-box');
            if (selectionBox && selectionBox.style.display !== 'none') {
              const previewContainer = document.getElementById('preview-container');
              if (previewContainer) {
                const imagePreview = new ImagePreview(previewContainer, data.sample_text);
                imagePreview.updatePreview();
              }
            }
          }
        })
        .catch(error => {
          console.error('Error fetching sample text:', error);
          showErrorToast(`Failed to fetch sample text: ${error.message}`);
        });
    });
  }
}

/**
 * Handle form submission
 * @param {Event} e - Form submit event
 */
function handleFormSubmit(e) {
  // Allow normal form submission - we're not doing AJAX for form submission
  // to maintain compatibility with the existing server-side implementation
  
  // Validate the file before submission
  const fileInput = document.getElementById('image_file');
  if (fileInput && fileInput.files.length > 0) {
    const file = fileInput.files[0];
    const validation = validateImageFile(file);
    
    if (!validation.valid) {
      e.preventDefault();
      showErrorToast(validation.message);
      return false;
    }
  } else {
    e.preventDefault();
    showErrorToast('Please select an image file');
    return false;
  }
  
  // Validate that selection has been made
  const textWidth = parseInt(document.getElementById('text_width').value, 10);
  const textHeight = parseInt(document.getElementById('text_height').value, 10);
  
  if (textWidth === 0 || textHeight === 0) {
    e.preventDefault();
    showErrorToast('Please select a text area on the image');
    return false;
  }
  
  // We could add more validation here, but this covers the critical cases
  return true;
} 