/**
 * File Uploader Component
 * Handles file selection, drag-and-drop, and validation
 */
import { state } from '../state.js';
import { validateImageFile, createFilePreview } from '../utils/fileUtils.js';

export class FileUploader {
  /**
   * Create a new FileUploader instance
   * @param {HTMLElement} container - Container element for the uploader
   * @param {Function} onFileChange - Callback when a valid file is selected
   */
  constructor(container, onFileChange) {
    this.container = container;
    this.onFileChange = onFileChange;
    this.fileInput = container.querySelector('input[type="file"]');
    this.fileLabel = container.querySelector('.file-input-label');
    
    this.init();
  }
  
  /**
   * Initialize the file uploader
   */
  init() {
    // Add file change handler
    this.fileInput.addEventListener('change', (e) => this.handleFileChange(e));
    
    // Setup drag and drop
    this.setupDragAndDrop();
  }
  
  /**
   * Handle file selection
   * @param {Event} e - The change event
   */
  handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate the file
    const validation = validateImageFile(file);
    if (!validation.valid) {
      alert(validation.message);
      // Clear the file input
      this.fileInput.value = '';
      return;
    }
    
    // Update the label with the filename
    this.fileLabel.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 5v14m-7-7l7-7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>${file.name}</span>
    `;
    
    // Create a preview and store the file
    createFilePreview(file)
      .then(preview => {
        // Store the file and preview in the state
        state.set('image', { file, preview });
        
        // Call the callback
        if (this.onFileChange) {
          this.onFileChange(file, preview);
        }
      });
  }
  
  /**
   * Setup drag and drop functionality
   */
  setupDragAndDrop() {
    const preventDefaults = (e) => {
      e.preventDefault();
      e.stopPropagation();
    };
    
    const highlight = () => {
      this.container.classList.add('highlight');
    };
    
    const unhighlight = () => {
      this.container.classList.remove('highlight');
    };
    
    const handleDrop = (e) => {
      preventDefaults(e);
      unhighlight();
      
      const dt = e.dataTransfer;
      const file = dt.files[0];
      
      if (!file) return;
      
      // Validate the file
      const validation = validateImageFile(file);
      if (!validation.valid) {
        alert(validation.message);
        return;
      }
      
      // Set the file in the input element
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      this.fileInput.files = dataTransfer.files;
      
      // Trigger the change event
      this.fileInput.dispatchEvent(new Event('change'));
    };
    
    // Add event listeners
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      this.container.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
      this.container.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
      this.container.addEventListener(eventName, unhighlight, false);
    });
    
    this.container.addEventListener('drop', handleDrop, false);
  }
} 