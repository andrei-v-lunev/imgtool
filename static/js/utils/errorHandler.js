/**
 * Error handling utilities
 */

/**
 * Initialize global error handling
 * Captures uncaught errors and rejections
 */
export function initErrorHandling() {
  // Capture uncaught errors
  window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
    showErrorToast(`Error: ${event.message}`);
    
    // Log the error
    logError(event.error || event);
  });
  
  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showErrorToast(`Async Error: ${event.reason.message || 'Promise rejected'}`);
    
    // Log the error
    logError(event.reason);
  });
}

/**
 * Show a toast notification for errors
 * @param {string} message - Error message to display
 */
export function showErrorToast(message) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '20px';
    toastContainer.style.right = '20px';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.style.backgroundColor = '#f44336';
  toast.style.color = 'white';
  toast.style.padding = '12px 16px';
  toast.style.borderRadius = '4px';
  toast.style.marginTop = '8px';
  toast.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  toast.style.minWidth = '250px';
  toast.style.maxWidth = '400px';
  toast.style.wordBreak = 'break-word';
  
  // Add message
  toast.textContent = message;
  
  // Add close button
  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '&times;';
  closeBtn.style.float = 'right';
  closeBtn.style.background = 'none';
  closeBtn.style.border = 'none';
  closeBtn.style.color = 'white';
  closeBtn.style.fontSize = '20px';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.marginLeft = '10px';
  closeBtn.style.marginRight = '-8px';
  closeBtn.style.marginTop = '-4px';
  closeBtn.onclick = () => toastContainer.removeChild(toast);
  
  toast.insertBefore(closeBtn, toast.firstChild);
  
  // Add toast to container
  toastContainer.appendChild(toast);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toastContainer.removeChild(toast);
    }
  }, 5000);
}

/**
 * Show a success toast notification
 * @param {string} message - Success message to display
 */
export function showSuccessToast(message) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '20px';
    toastContainer.style.right = '20px';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toast = document.createElement('div');
  toast.className = 'success-toast';
  toast.style.backgroundColor = '#4CAF50';
  toast.style.color = 'white';
  toast.style.padding = '12px 16px';
  toast.style.borderRadius = '4px';
  toast.style.marginTop = '8px';
  toast.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  toast.style.minWidth = '250px';
  toast.style.maxWidth = '400px';
  
  // Add message
  toast.textContent = message;
  
  // Add toast to container
  toastContainer.appendChild(toast);
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toastContainer.removeChild(toast);
    }
  }, 3000);
}

/**
 * Log errors to the server or analytics service
 * @param {Error|string} error - Error to log
 */
export function logError(error) {
  // In a real app, this would send the error to a server
  // For now, we'll just log to console
  console.error('Logged error:', error);
  
  // Example of how to send to a server:
  /*
  fetch('/api/error-log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: error.message || String(error),
      stack: error.stack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    })
  }).catch(e => console.error('Failed to log error:', e));
  */
} 