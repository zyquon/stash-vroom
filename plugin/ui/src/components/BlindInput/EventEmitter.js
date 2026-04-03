// Stub for server communication - logs events to console
class EventEmitter {
  constructor() {
    this.events = []
    this.maxEvents = 100  // Keep last 100 events in memory
  }

  emit(eventType, details) {
    const event = {
      timestamp: new Date().toISOString(),
      eventType,
      details,
      sent: false  // Will be true when server communication is implemented
    }

    this.events.push(event)

    // Trim old events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents)
    }

    // Log to console (stub for server)
    console.log(`[Event] ${eventType}`, {
      zone: details.zone,
      sequence: details.sequence.join(' -> '),
      timestamp: event.timestamp
    })

    // TODO: Send to server via WebSocket or HTTP
    // this.sendToServer(event)
  }

  sendToServer(event) {
    // STUB: Future implementation
    // Could use WebSocket for real-time, or batch HTTP requests
    console.log('[EventEmitter] Would send to server:', event)
  }

  getRecentEvents(count = 10) {
    return this.events.slice(-count)
  }

  clearEvents() {
    this.events = []
  }
}

// Export singleton instance
export default new EventEmitter()
