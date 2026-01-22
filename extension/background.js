// Service worker for Manifest V3
chrome.runtime.onInstalled.addListener(() => {
  console.log('Image Describer extension installed');
  
  // Create context menu for right-clicking images
  chrome.contextMenus.create({
    id: 'describeImage',
    title: 'Describe Image',
    contexts: ['image']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'describeImage' && info.srcUrl) {
    // Store the image URL in storage
    chrome.storage.local.set({ pendingImageUrl: info.srcUrl }, () => {
      // Try to open the popup (may not work in all contexts)
      chrome.action.openPopup().catch(() => {
        // If openPopup fails, send a message instead
        // The popup will check storage when it opens
        console.log('Popup will check for pending image on next open');
      });
    });
  }
});

