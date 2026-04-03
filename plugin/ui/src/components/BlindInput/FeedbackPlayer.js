import { FEEDBACK } from './mappings.js'

class FeedbackPlayer {
  constructor() {
    this.hapticSupported = 'vibrate' in navigator
  }

  // Play a sequence of feedback items
  play(feedbackArray) {
    if (!feedbackArray || feedbackArray.length === 0) return

    feedbackArray.forEach((item, i) => {
      setTimeout(() => this.playOne(item), i * 150)
    })
  }

  playOne(type) {
    switch (type) {
      case FEEDBACK.SHORT_BUZZ:
        this.vibrate(50)
        break
      case FEEDBACK.LONG_BUZZ:
        this.vibrate(200)
        break
      case FEEDBACK.SHORT_BEEP:
        console.log('[Audio] Would play: short_beep')
        // TODO: Web Audio API or audio file
        // this.playTone(880, 100)  // A5, 100ms
        break
      case FEEDBACK.LONG_BEEP:
        console.log('[Audio] Would play: long_beep')
        // TODO: Web Audio API or audio file
        // this.playTone(440, 300)  // A4, 300ms
        break
      default:
        console.warn('[FeedbackPlayer] Unknown feedback type:', type)
    }
  }

  vibrate(ms) {
    if (this.hapticSupported) {
      navigator.vibrate(ms)
    } else {
      console.log(`[Haptic] Would vibrate: ${ms}ms`)
    }
  }

  // Stub for future Web Audio API implementation
  playTone(frequency, durationMs) {
    console.log(`[Audio] Would play tone: ${frequency}Hz for ${durationMs}ms`)
    // Future implementation:
    // const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    // const oscillator = audioCtx.createOscillator()
    // oscillator.type = 'sine'
    // oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime)
    // oscillator.connect(audioCtx.destination)
    // oscillator.start()
    // oscillator.stop(audioCtx.currentTime + durationMs / 1000)
  }

  stop() {
    if (this.hapticSupported) {
      navigator.vibrate(0)
    }
  }
}

// Export singleton instance
export default new FeedbackPlayer()
