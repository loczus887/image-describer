# Image Describer Browser Extension

Manifest V3 browser extension for Image Describer.

## Installation

1. Open Chrome/Edge and navigate to `chrome://extensions/` (or `edge://extensions/`)
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` folder from this project

## Usage

### Method 1: Right-click on Image
1. Right-click on any image on a webpage
2. Select "Describe Image" from the context menu
3. The extension popup will open and process the image
4. Description will appear in the popup

### Method 2: Upload Image
1. Click the extension icon
2. Click "Choose File" or drag and drop an image
3. Wait for processing (may take a few minutes on first run)
4. Description will appear below

## Features

- **Context Menu Integration**: Right-click any image to describe it
- **File Upload**: Upload images directly from your computer
- **Text-to-Speech**: Click "Read Aloud" to hear the description
- **Error Handling**: Clear error messages if something goes wrong

## Requirements

- Backend server must be running on `http://localhost:8000`
- Start the backend with: `python -m uvicorn backend.api_controller:app --host 127.0.0.1 --port 8000`

## Troubleshooting

- **"Cannot connect" error**: Make sure backend is running on port 8000
- **No description appears**: Check browser console (F12) for errors
- **Slow processing**: First run downloads AI model (~990MB), subsequent runs are faster
- **CORS errors**: Backend should have CORS headers enabled (already configured)

## Notes

- The extension requires the backend API to be running
- First image description may take several minutes (model download)
- Images are processed locally using BLIP model
