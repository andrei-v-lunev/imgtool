/**
 * Style Settings Component
 * Handles font, color, and text styling controls
 */
import { state } from '../state.js';

export class StyleSettings {
  /**
   * Create a new StyleSettings instance
   * @param {HTMLElement} container - Container for style settings
   */
  constructor(container) {
    this.container = container;
    
    // Font settings
    this.fontSelect = container.querySelector('#font_name');
    this.fontSize = container.querySelector('#font_size');
    this.fontSizeNumber = container.querySelector('#font_size_number');
    this.fontColor = container.querySelector('#font_color');
    this.fontColorHex = container.querySelector('#font_color_hex');
    
    // Alignment
    this.alignmentButtons = container.querySelectorAll('.alignment-buttons button');
    this.alignmentInput = container.querySelector('#alignment');
    
    // Background settings
    this.textBackground = container.querySelector('#text_background');
    this.backgroundSettings = container.querySelector('#background-settings');
    this.textBackgroundColor = container.querySelector('#text_background_color');
    this.textBackgroundColorHex = container.querySelector('#text_background_color_hex');
    this.bgVerticalPadding = container.querySelector('#bg_vertical_padding');
    this.bgVerticalPaddingNumber = container.querySelector('#bg_vertical_padding_number');
    this.bgHorizontalPadding = container.querySelector('#bg_horizontal_padding');
    this.bgHorizontalPaddingNumber = container.querySelector('#bg_horizontal_padding_number');
    this.bgCornerRadius = container.querySelector('#bg_corner_radius');
    this.bgCornerRadiusNumber = container.querySelector('#bg_corner_radius_number');
    
    // Base name and numbering
    this.baseName = container.querySelector('#baseName');
    this.startNumber = container.querySelector('#startNumber');
    this.startRow = container.querySelector('#startRow');
    
    this.init();
  }
  
  /**
   * Initialize style settings controls
   */
  init() {
    // Populate values from state
    this.syncWithState();
    
    // Setup font selector
    this.fontSelect.addEventListener('change', () => {
      state.set('settings.fontName', this.fontSelect.value);
    });
    
    // Setup font size
    this.setupRangeWithNumber('fontSize', 'font_size', 'font_size_number');
    
    // Setup font color
    this.setupColorPicker(this.fontColor, this.fontColorHex, 'settings.fontColor');
    
    // Setup alignment
    this.alignmentButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.alignmentButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        this.alignmentInput.value = button.dataset.align;
        state.set('settings.alignment', button.dataset.align);
      });
    });
    
    // Setup text background toggle
    this.textBackground.addEventListener('change', () => {
      const isChecked = this.textBackground.checked;
      this.backgroundSettings.style.display = isChecked ? 'block' : 'none';
      state.set('settings.textBackground', isChecked);
    });
    
    // Setup background color
    this.setupColorPicker(this.textBackgroundColor, this.textBackgroundColorHex, 'settings.textBackgroundColor');
    
    // Setup background padding controls
    this.setupRangeWithNumber('bgVerticalPadding', 'bg_vertical_padding', 'bg_vertical_padding_number');
    this.setupRangeWithNumber('bgHorizontalPadding', 'bg_horizontal_padding', 'bg_horizontal_padding_number');
    this.setupRangeWithNumber('bgCornerRadius', 'bg_corner_radius', 'bg_corner_radius_number');
    
    // Setup base name and numbering
    this.baseName.addEventListener('input', () => {
      state.set('settings.baseName', this.baseName.value);
    });
    
    this.startNumber.addEventListener('change', () => {
      state.set('settings.startNumber', parseInt(this.startNumber.value) || 1);
    });
    
    this.startRow.addEventListener('change', () => {
      state.set('settings.startRow', parseInt(this.startRow.value) || 1);
    });
    
    // Listen for state changes
    state.subscribe('settings', () => this.syncWithState());
  }
  
  /**
   * Setup a linked range input and number input
   * @param {string} stateProp - Property name in state.settings
   * @param {string} rangeId - ID of the range input
   * @param {string} numberId - ID of the number input
   */
  setupRangeWithNumber(stateProp, rangeId, numberId) {
    const range = document.getElementById(rangeId);
    const number = document.getElementById(numberId);
    
    if (!range || !number) return;
    
    range.addEventListener('input', () => {
      number.value = range.value;
      state.set(`settings.${stateProp}`, parseInt(range.value));
    });
    
    number.addEventListener('input', () => {
      range.value = number.value;
      state.set(`settings.${stateProp}`, parseInt(number.value));
    });
  }
  
  /**
   * Setup a color picker with hex input
   * @param {HTMLElement} colorPicker - Color picker input
   * @param {HTMLElement} hexInput - Hex color input
   * @param {string} stateProp - Property name in state
   */
  setupColorPicker(colorPicker, hexInput, stateProp) {
    if (!colorPicker || !hexInput) return;
    
    colorPicker.addEventListener('input', () => {
      hexInput.value = colorPicker.value;
      state.set(stateProp, colorPicker.value);
    });
    
    hexInput.addEventListener('input', () => {
      let hexValue = hexInput.value.trim();
      
      // Add # if missing
      if (hexValue.charAt(0) !== '#') {
        hexValue = '#' + hexValue;
      }
      
      // Validate hex code (both 3-char and 6-char format)
      if (/^#[0-9A-Fa-f]{3}$/.test(hexValue) || /^#[0-9A-Fa-f]{6}$/.test(hexValue)) {
        // Convert 3-char format to 6-char format if needed
        if (hexValue.length === 4) {
          const r = hexValue.charAt(1);
          const g = hexValue.charAt(2);
          const b = hexValue.charAt(3);
          hexValue = `#${r}${r}${g}${g}${b}${b}`;
        }
        
        colorPicker.value = hexValue;
        hexInput.value = hexValue;
        state.set(stateProp, hexValue);
      }
    });
  }
  
  /**
   * Synchronize UI with state values
   */
  syncWithState() {
    // Font settings
    if (this.fontSelect) {
      this.fontSelect.value = state.settings.fontName;
    }
    
    if (this.fontSize && this.fontSizeNumber) {
      this.fontSize.value = state.settings.fontSize;
      this.fontSizeNumber.value = state.settings.fontSize;
    }
    
    if (this.fontColor && this.fontColorHex) {
      this.fontColor.value = state.settings.fontColor;
      this.fontColorHex.value = state.settings.fontColor;
    }
    
    // Alignment
    if (this.alignmentInput) {
      this.alignmentInput.value = state.settings.alignment;
      
      this.alignmentButtons.forEach(button => {
        if (button.dataset.align === state.settings.alignment) {
          button.classList.add('active');
        } else {
          button.classList.remove('active');
        }
      });
    }
    
    // Background settings
    if (this.textBackground) {
      this.textBackground.checked = state.settings.textBackground;
      this.backgroundSettings.style.display = state.settings.textBackground ? 'block' : 'none';
    }
    
    if (this.textBackgroundColor && this.textBackgroundColorHex) {
      this.textBackgroundColor.value = state.settings.textBackgroundColor;
      this.textBackgroundColorHex.value = state.settings.textBackgroundColor;
    }
    
    if (this.bgVerticalPadding && this.bgVerticalPaddingNumber) {
      this.bgVerticalPadding.value = state.settings.bgVerticalPadding;
      this.bgVerticalPaddingNumber.value = state.settings.bgVerticalPadding;
    }
    
    if (this.bgHorizontalPadding && this.bgHorizontalPaddingNumber) {
      this.bgHorizontalPadding.value = state.settings.bgHorizontalPadding;
      this.bgHorizontalPaddingNumber.value = state.settings.bgHorizontalPadding;
    }
    
    if (this.bgCornerRadius && this.bgCornerRadiusNumber) {
      this.bgCornerRadius.value = state.settings.bgCornerRadius;
      this.bgCornerRadiusNumber.value = state.settings.bgCornerRadius;
    }
    
    // Base name and numbering
    if (this.baseName) {
      this.baseName.value = state.settings.baseName;
    }
    
    if (this.startNumber) {
      this.startNumber.value = state.settings.startNumber;
    }
    
    if (this.startRow) {
      this.startRow.value = state.settings.startRow;
    }
  }
  
  /**
   * Setup eyedropper for color picker
   * @param {string} colorPickerId - ID of the color picker
   * @param {string} hexInputId - ID of the hex input
   * @param {string} stateProp - Property name in state
   */
  setupEyedropper(colorPickerId, hexInputId, stateProp) {
    const colorPicker = document.getElementById(colorPickerId);
    const hexInput = document.getElementById(hexInputId);
    
    if (!colorPicker || !hexInput) return;
    
    // Create eyedropper button
    const eyedropperBtn = document.createElement('button');
    eyedropperBtn.type = 'button';
    eyedropperBtn.className = 'btn btn-icon eyedropper-btn';
    eyedropperBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 11L14 16M9 21L5 17M21 9l-9 9M9 3L3 9L12 18L18 12L9 3z"/></svg>';
    eyedropperBtn.title = 'Pick color from image';
    
    // Insert button after hex input
    hexInput.insertAdjacentElement('afterend', eyedropperBtn);
    
    // Add eyedropper functionality
    eyedropperBtn.addEventListener('click', () => {
      const previewImage = document.getElementById('preview-image');
      if (!previewImage || !previewImage.src) {
        alert('Please upload an image first');
        return;
      }
      
      const previewContainer = document.getElementById('preview-container');
      
      // Toggle eyedropper mode
      previewContainer.classList.toggle('eyedropper-mode');
      eyedropperBtn.classList.toggle('active');
      
      if (previewContainer.classList.contains('eyedropper-mode')) {
        // Change cursor
        previewImage.style.cursor = 'crosshair';
        
        // One-time click handler for color picking
        const pickColor = function(e) {
          e.preventDefault();
          
          // Get pixel color from canvas
          const rect = previewImage.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          
          // Create canvas to sample color
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          canvas.width = previewImage.naturalWidth;
          canvas.height = previewImage.naturalHeight;
          ctx.drawImage(previewImage, 0, 0, canvas.width, canvas.height);
          
          // Calculate the actual position in the original image
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
          const pixelX = Math.floor(x * scaleX);
          const pixelY = Math.floor(y * scaleY);
          
          // Get pixel data
          const pixelData = ctx.getImageData(pixelX, pixelY, 1, 1).data;
          
          // Convert to hex
          const hexColor = '#' + 
            ('0' + pixelData[0].toString(16)).slice(-2) +
            ('0' + pixelData[1].toString(16)).slice(-2) +
            ('0' + pixelData[2].toString(16)).slice(-2);
          
          // Update color picker and hex input
          colorPicker.value = hexColor;
          hexInput.value = hexColor;
          state.set(stateProp, hexColor);
          
          // Exit eyedropper mode
          previewContainer.classList.remove('eyedropper-mode');
          eyedropperBtn.classList.remove('active');
          previewImage.style.cursor = 'crosshair';
          
          // Remove this one-time handler
          previewImage.removeEventListener('click', pickColor);
        };
        
        previewImage.addEventListener('click', pickColor);
      }
    });
  }
} 