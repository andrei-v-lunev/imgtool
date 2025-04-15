/**
 * Utility functions for handling file operations
 */

/**
 * Validates a file for image upload
 * @param {File} file - The file to validate
 * @returns {Object} - Result with valid flag and message
 */
export function validateImageFile(file) {
  // Check if a file was selected
  if (!file) {
    return { valid: false, message: 'No file selected' };
  }
  
  // Check file type
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif'];
  if (!allowedTypes.includes(file.type)) {
    return { 
      valid: false, 
      message: `Invalid file type. Allowed types: ${allowedTypes.map(t => t.split('/')[1]).join(', ')}` 
    };
  }
  
  // Check file size (max 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB in bytes
  if (file.size > maxSize) {
    return { 
      valid: false, 
      message: `File too large. Maximum size is ${Math.round(maxSize / (1024 * 1024))}MB` 
    };
  }
  
  return { valid: true };
}

/**
 * Creates an object URL for a file
 * @param {File} file - The file to create a URL for
 * @returns {Promise<string>} - URL to the file
 */
export function createFilePreview(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      resolve(event.target.result);
    };
    
    reader.onerror = (error) => {
      reject(error);
    };
    
    reader.readAsDataURL(file);
  });
}

/**
 * Gets a file's extension
 * @param {string} filename - The filename
 * @returns {string} - The file extension
 */
export function getFileExtension(filename) {
  return filename.split('.').pop().toLowerCase();
}

/**
 * Generates a sequential filename
 * @param {string} baseName - Base name for the file
 * @param {number} index - Index number
 * @param {number} startNumber - Starting number 
 * @param {string} extension - File extension
 * @returns {string} - Generated filename
 */
export function generateSequentialFilename(baseName, index, startNumber, extension) {
  // Ensure extension doesn't have a leading dot
  extension = extension.replace(/^\./, '');
  
  // Generate padded number (e.g., 001, 002, 003)
  const paddedNumber = (index + startNumber).toString().padStart(3, '0');
  
  return `${baseName}_${paddedNumber}.${extension}`;
} 