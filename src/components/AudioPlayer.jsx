import React, { useState, useEffect } from 'react'
import './AudioPlayer.css'

function AudioPlayer({ text }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isSupported, setIsSupported] = useState(false)

  useEffect(() => {
    // Check if Web Speech API is supported
    setIsSupported('speechSynthesis' in window)
  }, [])

  const speak = () => {
    if (!isSupported || !text) return

    if (isPlaying) {
      window.speechSynthesis.cancel()
      setIsPlaying(false)
    } else {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'en-US'
      utterance.rate = 1.0
      utterance.pitch = 1.0
      utterance.volume = 1.0

      utterance.onend = () => {
        setIsPlaying(false)
      }

      utterance.onerror = () => {
        setIsPlaying(false)
      }

      window.speechSynthesis.speak(utterance)
      setIsPlaying(true)
    }
  }

  const stop = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsPlaying(false)
    }
  }

  if (!isSupported) {
    return null
  }

  return (
    <div className="audio-player">
      <button
        onClick={speak}
        className="audio-button"
        aria-label={isPlaying ? 'Stop reading' : 'Read description aloud'}
      >
        {isPlaying ? '⏸️ Stop' : '🔊 Read Aloud'}
      </button>
      {isPlaying && (
        <button
          onClick={stop}
          className="audio-button stop-button"
          aria-label="Stop reading"
        >
          Stop
        </button>
      )}
    </div>
  )
}

export default AudioPlayer

