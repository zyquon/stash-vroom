import { GESTURE, TIMING } from './mappings.js'

export default class SequenceRecognizer {
  constructor(onSequenceComplete) {
    this.onSequenceComplete = onSequenceComplete

    // Current sequence state
    this.currentZone = null
    this.currentSequence = []
    this.sequenceTimeout = null

    // Touch tracking for gesture detection
    this.touchStart = null
    this.longPressTimer = null
  }

  // Get zone from Y coordinate
  getZone(touchY, containerHeight) {
    return touchY < containerHeight / 2 ? 'top' : 'bottom'
  }

  // Add a gesture to the current sequence
  addGesture(gestureType, zone) {
    // First gesture in sequence sets the zone
    if (this.currentSequence.length === 0) {
      this.currentZone = zone
    }
    this.currentSequence.push(gestureType)
    this.resetSequenceTimeout()
  }

  resetSequenceTimeout() {
    clearTimeout(this.sequenceTimeout)
    this.sequenceTimeout = setTimeout(() => {
      this.finalizeSequence()
    }, TIMING.SEQUENCE_TIMEOUT_MS)
  }

  finalizeSequence() {
    if (this.currentSequence.length > 0) {
      this.onSequenceComplete({
        zone: this.currentZone,
        sequence: [...this.currentSequence]
      })
      this.currentZone = null
      this.currentSequence = []
    }
  }

  // Cancel any pending sequence
  cancel() {
    clearTimeout(this.sequenceTimeout)
    clearTimeout(this.longPressTimer)
    this.currentZone = null
    this.currentSequence = []
    this.touchStart = null
  }

  // Touch event handlers
  handleTouchStart(e, containerHeight) {
    e.preventDefault()

    const touch = e.touches[0]
    const zone = this.getZone(touch.clientY, containerHeight)

    this.touchStart = {
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now(),
      zone: zone
    }

    // Start long press detection
    this.longPressTimer = setTimeout(() => {
      if (this.touchStart) {
        this.addGesture(GESTURE.LONG, this.touchStart.zone)
        this.touchStart = null  // Consume the touch
      }
    }, TIMING.LONG_PRESS_MIN_MS)
  }

  handleTouchMove(e) {
    e.preventDefault()

    // Cancel long press if finger moves significantly
    if (this.touchStart && this.longPressTimer) {
      const touch = e.touches[0]
      const dx = Math.abs(touch.clientX - this.touchStart.x)
      const dy = Math.abs(touch.clientY - this.touchStart.y)

      if (dx > 20 || dy > 20) {
        clearTimeout(this.longPressTimer)
        this.longPressTimer = null
      }
    }
  }

  handleTouchEnd(e, containerHeight) {
    e.preventDefault()

    clearTimeout(this.longPressTimer)
    this.longPressTimer = null

    if (!this.touchStart) return  // Was consumed by long press

    const touch = e.changedTouches[0]
    const duration = Date.now() - this.touchStart.time
    const dx = touch.clientX - this.touchStart.x
    const dy = touch.clientY - this.touchStart.y
    const distance = Math.sqrt(dx * dx + dy * dy)

    // Check for swipe
    if (distance > TIMING.SWIPE_MIN_PX) {
      const swipeType = this.getSwipeDirection(dx, dy)
      this.addGesture(swipeType, this.touchStart.zone)
      this.touchStart = null
      return
    }

    // Check for tap (short duration, didn't move much)
    if (duration < TIMING.TAP_MAX_MS && distance < 20) {
      this.addGesture(GESTURE.TAP, this.touchStart.zone)
    }

    this.touchStart = null
  }

  getSwipeDirection(dx, dy) {
    const absDx = Math.abs(dx)
    const absDy = Math.abs(dy)

    if (absDx > absDy) {
      return dx > 0 ? GESTURE.SWIPE_RIGHT : GESTURE.SWIPE_LEFT
    } else {
      return dy > 0 ? GESTURE.SWIPE_DOWN : GESTURE.SWIPE_UP
    }
  }
}
