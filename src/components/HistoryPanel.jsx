import React, { useState } from 'react'
import './HistoryPanel.css'

function HistoryPanel({ history, onSelectItem, onClearHistory }) {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [isClearing, setIsClearing] = useState(false)

  const handleClearHistory = async () => {
    setIsClearing(true)
    try {
      await onClearHistory()
      setShowConfirmDialog(false)
    } catch (error) {
      console.error('Failed to clear history:', error)
    } finally {
      setIsClearing(false)
    }
  }

  if (!history || history.length === 0) {
    return (
      <div className="history-panel">
        <h2>History</h2>
        <p className="history-empty">No descriptions yet</p>
      </div>
    )
  }

  return (
    <div className="history-panel" role="region" aria-label="Description history">
      <div className="history-header">
        <h2>History</h2>
        <button
          onClick={() => setShowConfirmDialog(true)}
          className="clear-history-button"
          aria-label="Clear all history"
        >
          Clear History
        </button>
      </div>

      {showConfirmDialog && (
        <div className="confirm-dialog">
          <p>Are you sure you want to delete all history?</p>
          <div className="confirm-buttons">
            <button
              onClick={handleClearHistory}
              disabled={isClearing}
              className="confirm-yes"
            >
              {isClearing ? 'Deleting...' : 'Yes, Delete All'}
            </button>
            <button
              onClick={() => setShowConfirmDialog(false)}
              disabled={isClearing}
              className="confirm-no"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <ul className="history-list">
        {history.map((item) => (
          <li key={item.id} className="history-item">
            <button
              onClick={() => onSelectItem(item)}
              className="history-button"
              aria-label={`View description from ${new Date(item.created_at).toLocaleString()}`}
            >
              <div className="history-description-preview">
                {item.description.substring(0, 100)}
                {item.description.length > 100 ? '...' : ''}
              </div>
              <div className="history-date">
                {new Date(item.created_at).toLocaleString()}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default HistoryPanel

