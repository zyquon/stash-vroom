// Gesture types (zone-independent)
export const GESTURE = {
  TAP: 'tap',
  LONG: 'long',
  SWIPE_UP: 'swipe_up',
  SWIPE_DOWN: 'swipe_down',
  SWIPE_LEFT: 'swipe_left',
  SWIPE_RIGHT: 'swipe_right',
}

// Zones
export const ZONE = {
  TOP: 'top',
  BOTTOM: 'bottom',
  ANY: '*',  // Wildcard for mappings that apply to any zone
}

// Feedback types
export const FEEDBACK = {
  SHORT_BUZZ: 'short_buzz',
  LONG_BUZZ: 'long_buzz',
  SHORT_BEEP: 'short_beep',
  LONG_BEEP: 'long_beep',
}

// Zone colors (for visual distinction)
export const ZONE_COLORS = {
  TOP: '#1a237e',     // Deep blue
  BOTTOM: '#bf360c',  // Deep orange
}

// Timing config
export const TIMING = {
  TAP_MAX_MS: 300,
  LONG_PRESS_MIN_MS: 500,
  SWIPE_MIN_PX: 50,
  SEQUENCE_TIMEOUT_MS: 600,  // Finalize sequence after this idle time
}

// Four-column mappings: [zone, sequence, event_type, feedback_array]
export const INPUT_MAPPINGS = [
  // Single tap
  ['top',    ['tap'],                   'PlayPause',    ['short_buzz']],
  ['bottom', ['tap'],                   'Skip',         ['short_buzz']],

  // Double tap
  ['top',    ['tap', 'tap'],            'Favorite',     ['short_beep', 'short_buzz']],
  ['bottom', ['tap', 'tap'],            'Unfavorite',   ['short_beep', 'short_buzz']],

  // Triple tap
  ['top',    ['tap', 'tap', 'tap'],     'MarkAsNew',    ['short_buzz', 'short_buzz', 'long_buzz']],
  ['bottom', ['tap', 'tap', 'tap'],     'MarkAsOld',    ['short_buzz', 'short_buzz', 'long_buzz']],

  // Long press
  ['top',    ['long'],                  'ModeSwitch',   ['long_buzz']],
  ['bottom', ['long'],                  'Cancel',       ['long_buzz', 'long_buzz']],

  // Swipe up/down (zone-specific)
  ['top',    ['swipe_up'],              'RatingUp',     ['short_beep']],
  ['top',    ['swipe_down'],            'RatingDown',   ['long_beep']],
  ['bottom', ['swipe_up'],              'VolumeUp',     ['short_beep']],
  ['bottom', ['swipe_down'],            'VolumeDown',   ['long_beep']],

  // Swipe left/right (any zone)
  ['*',      ['swipe_left'],            'Previous',     ['short_buzz', 'short_buzz']],
  ['*',      ['swipe_right'],           'Next',         ['short_buzz', 'short_buzz']],

  // Combo: tap then swipe
  ['top',    ['tap', 'swipe_up'],       'RatingMax',    ['short_beep', 'short_beep', 'short_beep']],
  ['bottom', ['tap', 'swipe_down'],     'RatingMin',    ['long_beep', 'long_beep']],
]

// Helper: Find mapping for a zone and sequence
export function findMapping(zone, sequence) {
  for (const mapping of INPUT_MAPPINGS) {
    const [mappingZone, mappingSequence] = mapping

    // Zone must match exactly or be wildcard '*'
    const zoneMatches = mappingZone === zone || mappingZone === '*'

    if (zoneMatches && sequencesEqual(sequence, mappingSequence)) {
      return mapping
    }
  }
  return null
}

function sequencesEqual(a, b) {
  return a.length === b.length && a.every((v, i) => v === b[i])
}
