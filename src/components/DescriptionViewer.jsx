import React from 'react'
import './DescriptionViewer.css'

function DescriptionViewer({ description }) {
  return (
    <div className="description-viewer" role="region" aria-label="Image description">
      <h2>Description</h2>
      <p className="description-text">{description}</p>
    </div>
  )
}

export default DescriptionViewer

