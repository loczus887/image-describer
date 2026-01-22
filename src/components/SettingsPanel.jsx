import React from 'react'
import './SettingsPanel.css'

function SettingsPanel({
  highContrast,
  fontSize,
  audioEnabled,
  onHighContrastChange,
  onFontSizeChange,
  onAudioEnabledChange,
  onClose,
}) {
  return (
    <div className="settings-panel-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>Settings</h2>
          <button
            onClick={onClose}
            className="settings-close"
            aria-label="Close settings"
          >
            ×
          </button>
        </div>

        <div className="settings-content">
          <div className="setting-group">
            <label htmlFor="high-contrast">
              <input
                type="checkbox"
                id="high-contrast"
                checked={highContrast}
                onChange={(e) => onHighContrastChange(e.target.checked)}
              />
              <span>High Contrast Mode</span>
            </label>
          </div>

          <div className="setting-group">
            <label htmlFor="font-size">Font Size</label>
            <select
              id="font-size"
              value={fontSize}
              onChange={(e) => onFontSizeChange(e.target.value)}
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
              <option value="xlarge">Extra Large</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="audio-enabled">
              <input
                type="checkbox"
                id="audio-enabled"
                checked={audioEnabled}
                onChange={(e) => onAudioEnabledChange(e.target.checked)}
              />
              <span>Enable Audio Reading</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPanel

