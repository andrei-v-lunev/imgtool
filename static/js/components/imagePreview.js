/**
 * Image Preview Component
 * Handles displaying the image and selecting text regions
 */
import { state } from '../state.js';

export class ImagePreview {
  /**
   * Create a new ImagePreview instance
   * @param {HTMLElement} container - Container for the preview
   * @param {string} sampleText - Sample text for preview
   */
  constructor(container, sampleText) {
    this.container = container;
    this.previewImage = container.querySelector('#preview-image');
    this.selectionBox = container.querySelector('#selection-box');
    this.dummyText = container.querySelector('#dummy-text');
    this.sampleText = sampleText;
    
    this.isSelecting = false;
    this.startX = 0;
    this.startY = 0;
    
    this.init();
  }
  
  /**
   * Initialize the preview
   */
  init() {
    // Add event listeners for selection
    this.container.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    this.container.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    document.addEventListener('mouseup', () => this.handleMouseUp());
    
    // Listen for state changes
    state.subscribe('image', (image) => {
      if (image && image.preview) {
        this.showPreview(image.preview);
      }
    });
    
    // Initial setup if there's an image in the state
    if (state.image && state.image.preview) {
      this.showPreview(state.image.preview);
    }
  }
  
  /**
   * Show an image preview
   * @param {string} src - Image source URL
   */
  showPreview(src) {
    // Reset selection
    this.hideSelection();
    
    // Set preview image source
    this.previewImage.src = src;
    
    // Show the preview section
    const previewSection = this.container.closest('.preview-section');
    if (previewSection) {
      previewSection.style.display = 'block';
    }
  }
  
  /**
   * Hide the selection box
   */
  hideSelection() {
    this.selectionBox.style.display = 'none';
    
    // Reset selection in state
    state.set('selection', {
      textX: 0,
      textY: 0,
      textWidth: 0,
      textHeight: 0
    });
  }
  
  /**
   * Handle mouse down on the preview image
   * @param {MouseEvent} e - Mouse event
   */
  handleMouseDown(e) {
    if (e.target !== this.previewImage) return;
    e.preventDefault();
    
    const rect = this.previewImage.getBoundingClientRect();
    const scaleX = this.previewImage.naturalWidth / rect.width;
    const scaleY = this.previewImage.naturalHeight / rect.height;
    
    this.startX = e.clientX - rect.left;
    this.startY = e.clientY - rect.top;
    
    this.isSelecting = true;
    this.selectionBox.style.display = 'block';
    this.selectionBox.style.left = this.startX + 'px';
    this.selectionBox.style.top = this.startY + 'px';
    this.selectionBox.style.width = '0px';
    this.selectionBox.style.height = '0px';
    
    // Store actual image coordinates in state
    state.selection.textX = Math.floor(this.startX * scaleX);
    state.selection.textY = Math.floor(this.startY * scaleY);
    
    // Update hidden form inputs (for backward compatibility)
    document.getElementById('text_x').value = state.selection.textX;
    document.getElementById('text_y').value = state.selection.textY;
  }
  
  /**
   * Handle mouse move during selection
   * @param {MouseEvent} e - Mouse event
   */
  handleMouseMove(e) {
    if (!this.isSelecting) return;
    e.preventDefault();
    
    const rect = this.previewImage.getBoundingClientRect();
    const scaleX = this.previewImage.naturalWidth / rect.width;
    const scaleY = this.previewImage.naturalHeight / rect.height;
    
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;
    
    const width = Math.abs(currentX - this.startX);
    const height = Math.abs(currentY - this.startY);
    const left = Math.min(this.startX, currentX);
    const top = Math.min(this.startY, currentY);
    
    this.selectionBox.style.left = left + 'px';
    this.selectionBox.style.top = top + 'px';
    this.selectionBox.style.width = width + 'px';
    this.selectionBox.style.height = height + 'px';
    
    // Update selection in state
    state.selection.textX = Math.floor(left * scaleX);
    state.selection.textY = Math.floor(top * scaleY);
    state.selection.textWidth = Math.floor(width * scaleX);
    state.selection.textHeight = Math.floor(height * scaleY);
    
    // Update hidden form inputs (for backward compatibility)
    document.getElementById('text_x').value = state.selection.textX;
    document.getElementById('text_y').value = state.selection.textY;
    document.getElementById('text_width').value = state.selection.textWidth;
    document.getElementById('text_height').value = state.selection.textHeight;
    
    this.updatePreview();
  }
  
  /**
   * Handle mouse up to finalize selection
   */
  handleMouseUp() {
    if (!this.isSelecting) return;
    
    this.isSelecting = false;
    
    // Ensure we have a minimum selection size
    if (state.selection.textWidth === 0 || state.selection.textHeight === 0) {
      const rect = this.previewImage.getBoundingClientRect();
      const scaleX = this.previewImage.naturalWidth / rect.width;
      const scaleY = this.previewImage.naturalHeight / rect.height;
      
      // Default to 100x50 pixels if selection is too small
      this.selectionBox.style.width = '100px';
      this.selectionBox.style.height = '50px';
      
      state.selection.textWidth = Math.floor(100 * scaleX);
      state.selection.textHeight = Math.floor(50 * scaleY);
      
      // Update hidden form inputs
      document.getElementById('text_width').value = state.selection.textWidth;
      document.getElementById('text_height').value = state.selection.textHeight;
    }
    
    this.updatePreview();
  }
  
  /**
   * Update the text preview in the selection box
   */
  updatePreview() {
    if (!this.selectionBox || this.selectionBox.style.display === 'none') return;
    
    // Get or create the text span element
    let textSpan = this.dummyText.querySelector('span');
    if (!textSpan) {
      textSpan = document.createElement('span');
      textSpan.textContent = this.sampleText;
      this.dummyText.innerHTML = '';
      this.dummyText.appendChild(textSpan);
    }
    
    // Apply current styles to the preview text
    textSpan.style.textAlign = state.settings.alignment;
    textSpan.style.color = state.settings.fontColor;
    textSpan.style.fontSize = state.settings.fontSize + 'px';
    
    // Try to match the font family
    const fontFamily = state.settings.fontName.replace(/\.(ttf|otf)$/i, '');
    textSpan.style.fontFamily = `"${fontFamily}", sans-serif`;
    
    // Apply text background if enabled
    if (state.settings.textBackground) {
      textSpan.style.backgroundColor = state.settings.textBackgroundColor;
      textSpan.style.padding = `${state.settings.bgVerticalPadding}px ${state.settings.bgHorizontalPadding}px`;
      textSpan.style.borderRadius = `${state.settings.bgCornerRadius}px`;
    } else {
      textSpan.style.backgroundColor = 'transparent';
      textSpan.style.padding = '0';
    }
  }
  
  /**
   * Show selection box at specific coordinates
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @param {number} width - Selection width
   * @param {number} height - Selection height
   */
  showSelectionAt(x, y, width, height) {
    // Show and position the selection box
    this.selectionBox.style.display = 'block';
    this.selectionBox.style.left = x + 'px';
    this.selectionBox.style.top = y + 'px';
    this.selectionBox.style.width = width + 'px';
    this.selectionBox.style.height = height + 'px';
    
    // Update selection in state
    state.selection.textX = x;
    state.selection.textY = y;
    state.selection.textWidth = width;
    state.selection.textHeight = height;
    
    // Create text span if it doesn't exist
    if (!this.dummyText.querySelector('span')) {
      const textSpan = document.createElement('span');
      textSpan.textContent = this.sampleText;
      this.dummyText.innerHTML = '';
      this.dummyText.appendChild(textSpan);
    }
    
    this.updatePreview();
  }
} 