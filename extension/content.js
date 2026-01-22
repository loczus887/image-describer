// Content script for extension
// Can be used to inject UI elements or interact with page images

console.log('Image Describer content script loaded');

// Example: Add describe button to images on page
function addDescribeButtons() {
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    if (!img.dataset.describerAdded) {
      img.dataset.describerAdded = 'true';
      // Could add overlay button here
    }
  });
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addDescribeButtons);
} else {
  addDescribeButtons();
}

