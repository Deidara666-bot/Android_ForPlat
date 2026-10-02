// No imports on purpose: this file is run directly by node in the plan card's failing test.
// An observation time is never presented as the time an event happened.

export interface EventTimeInput {
  event_time: string | null
  observed_at: string
  temporal_semantics: string
}

export interface EventTimeLabel {
  label: string
  isEventTime: boolean
}

export function formatEventTime({ event_time, observed_at }: EventTimeInput): EventTimeLabel {
  if (event_time === null) {
    return {
      label: `Waktu kejadian tidak tersedia · teramati ${observed_at}`,
      isEventTime: false,
    }
  }
  return { label: `Waktu kejadian ${event_time}`, isEventTime: true }
}
