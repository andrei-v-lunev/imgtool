/**
 * Basic reactive state management for the app
 */
export const state = {
  image: null,
  selection: {
    textX: 0,
    textY: 0,
    textWidth: 0, 
    textHeight: 0
  },
  settings: {
    baseName: 'image',
    startNumber: 1,
    startRow: 1,
    sheetName: 'Sheet1',
    fontName: 'ProximaNova-Bold.ttf',
    fontSize: 24,
    fontColor: '#ffffff',
    textBackground: false,
    textBackgroundColor: '#000000',
    bgVerticalPadding: 10,
    bgHorizontalPadding: 20,
    bgCornerRadius: 5,
    alignment: 'center'
  },
  _listeners: {},
  
  /**
   * Subscribe to changes in a specific part of the state
   * @param {string} key - The state key to watch
   * @param {Function} callback - Function to call when state changes
   * @returns {Function} - Unsubscribe function
   */
  subscribe(key, callback) {
    this._listeners[key] = this._listeners[key] || [];
    this._listeners[key].push(callback);
    return () => {
      this._listeners[key] = this._listeners[key].filter(cb => cb !== callback);
    };
  },
  
  /**
   * Update a state value and notify listeners
   * @param {string} key - The state key to update
   * @param {*} value - The new value
   */
  set(key, value) {
    // Handle nested path with dot notation (e.g., 'settings.fontSize')
    if (key.includes('.')) {
      const [parentKey, childKey] = key.split('.');
      this[parentKey][childKey] = value;
      
      // Call listeners for both the specific path and the parent object
      (this._listeners[key] || []).forEach(cb => cb(value));
      (this._listeners[parentKey] || []).forEach(cb => cb(this[parentKey]));
    } else {
      this[key] = value;
      (this._listeners[key] || []).forEach(cb => cb(value));
    }
    
    // Also notify for anything watching 'all'
    (this._listeners['all'] || []).forEach(cb => cb(this));
    
    // Save persistent settings
    if (key.startsWith('settings.')) {
      this.saveSettings();
    }
  },
  
  /**
   * Load saved settings from localStorage
   */
  loadSettings() {
    try {
      const savedSettings = JSON.parse(localStorage.getItem('imgtoolSettings') || '{}');
      Object.entries(savedSettings).forEach(([key, value]) => {
        if (this.settings.hasOwnProperty(key)) {
          this.settings[key] = value;
        }
      });
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  },
  
  /**
   * Save settings to localStorage
   */
  saveSettings() {
    try {
      localStorage.setItem('imgtoolSettings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  }
};

// Initialize by loading saved settings
state.loadSettings(); 