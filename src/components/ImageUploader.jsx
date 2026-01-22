import React, { useRef } from 'react'
import './ImageUploader.css'

function ImageUploader({ onUpload, loading, loadingMessage }) {
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onUpload(file)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      onUpload(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  return (
    <div
      className="image-uploader"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
        id="image-upload-input"
        aria-label="Upload image file"
        style={{ display: 'none' }}
      />
      <label htmlFor="image-upload-input" className="upload-label">
        <div className="upload-content">
          {loading ? (
            <>
              <div className="spinner" aria-label="Processing"></div>
              <p>Processing image...</p>
              {loadingMessage && <p className="loading-message" style={{fontSize: '0.875rem', color: 'var(--text-secondary)', fontStyle: 'italic'}}>{loadingMessage}</p>}
            </>
          ) : (
            <>
              <span className="upload-icon">📷</span>
              <p>Click to upload or drag and drop</p>
              <p className="upload-hint">PNG, JPG, WEBP, GIF up to 10MB</p>
            </>
          )}
        </div>
      </label>
    </div>
  )
}

export default ImageUploader

