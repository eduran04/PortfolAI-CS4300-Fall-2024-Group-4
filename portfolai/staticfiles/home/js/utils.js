/**
 * Utility Functions
 * Core helper functions used across the application
 */

/**
 * Extract a cookie value by name
 * @param {string} name - The name of the cookie to retrieve
 * @returns {string|null} The cookie value or null if not found
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Convert markdown-style formatting to HTML
 * @param {string} analysis - The analysis text to format
 * @returns {string} Formatted HTML content
 */
function formatAnalysisContent(analysis) {
  // Convert markdown-style formatting to HTML with more robust patterns
  let formatted = analysis
    // Bold text (**text** or __text__) - more flexible matching
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/__([^_]+)__/g, '<strong>$1</strong>')
    // Italic text (*text* or _text_) - more flexible matching
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    // Headers (#### Header, ### Header, ## Header)
    .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    // Bullet points (- item or • item)
    .replace(/^[-•] (.*$)/gm, '<li>$1</li>')
    // Numbered lists (1. item, 2. item, etc.)
    .replace(/^(\d+)\. (.*$)/gm, '<li>$1. $2</li>')
    // Line breaks - handle multiple newlines
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br>');
  
  // Wrap in paragraphs
  formatted = '<p>' + formatted + '</p>';
  
  // Convert list items to proper lists
  formatted = formatted.replace(/(<li>.*<\/li>)/g, (match) => {
    return '<ul>' + match + '</ul>';
  });
  
  // Clean up duplicate list wrappers
  formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
  
  // Clean up empty paragraphs
  formatted = formatted.replace(/<p><\/p>/g, '');
  formatted = formatted.replace(/<p><br><\/p>/g, '');
  
  return formatted;
}

// Global CSRF token for API requests
const csrftoken = getCookie('csrftoken');
