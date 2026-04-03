import React from 'react'
import './BlindInput.css'
import SequenceRecognizer from './SequenceRecognizer.js'
import feedbackPlayer from './FeedbackPlayer.js'
import eventEmitter from './EventEmitter.js'
import { findMapping } from './mappings.js'

const PluginApi = window.PluginApi
const { Link } = PluginApi.libraries.ReactRouterDOM

export default function BlindInput() {
  const containerRef = React.useRef(null)
  const recognizerRef = React.useRef(null)

  // Initialize the sequence recognizer
  React.useEffect(() => {
    recognizerRef.current = new SequenceRecognizer(({ zone, sequence }) => {
      const mapping = findMapping(zone, sequence)

      if (mapping) {
        const [, , eventType, feedback] = mapping
        eventEmitter.emit(eventType, { zone, sequence })
        feedbackPlayer.play(feedback)
      } else {
        console.log('[BlindInput] No mapping for:', { zone, sequence })
        // Optionally play error feedback for unrecognized sequences
        // feedbackPlayer.play(['short_buzz'])
      }
    })

    return () => {
      if (recognizerRef.current) {
        recognizerRef.current.cancel()
      }
    }
  }, [])

  const getContainerHeight = () => {
    return containerRef.current ? containerRef.current.clientHeight : window.innerHeight
  }

  const handleTouchStart = (e) => {
    if (recognizerRef.current) {
      recognizerRef.current.handleTouchStart(e, getContainerHeight())
    }
  }

  const handleTouchMove = (e) => {
    if (recognizerRef.current) {
      recognizerRef.current.handleTouchMove(e)
    }
  }

  const handleTouchEnd = (e) => {
    if (recognizerRef.current) {
      recognizerRef.current.handleTouchEnd(e, getContainerHeight())
    }
  }

  return (
    <div
      ref={containerRef}
      className="blind-input-container"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Two colored zones */}
      <div className="blind-input-zone top" />
      <div className="blind-input-zone bottom" />

      {/* Settings link - only visible on desktop */}
      <Link to="/plugins/VRoom/settings" className="blind-input-settings-link">
        Settings
      </Link>
    </div>
  )
}
