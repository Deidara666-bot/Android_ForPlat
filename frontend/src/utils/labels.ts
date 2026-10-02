// UI labels (Indonesian, locked equivalents of 01_BREAKDOWN 4.7), kept in one module for consistency.
const CONNECTION_STATE: Record<string, string> = {
  connected: 'terhubung',
  disconnected: 'terputus',
  unknown: 'tidak diketahui',
}

export function connectionStateLabel(state: string): string {
  return CONNECTION_STATE[state] ?? 'tidak diketahui'
}

export function formatTime(value: string | null): string {
  if (value === null) return 'belum pernah terlihat'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('id-ID')
}

// Locked equivalents (01_BREAKDOWN 4.7.3): epistemic class and availability status.
const EPISTEMIC_CLASS: Record<string, string> = {
  identity_attribute: 'atribut identitas',
  capability_state: 'kapabilitas',
  execution_observed: 'eksekusi teramati',
  data_present: 'keberadaan data',
}

const AVAILABILITY_STATUS: Record<string, string> = {
  acquired: 'diperoleh',
  unavailable: 'tidak tersedia',
  denied: 'ditolak',
  unsupported: 'tidak didukung',
  failed: 'gagal',
}

// Not locked in 4.7 yet; the raw value is always shown next to these working labels.
const EVIDENCE_STATE: Record<string, string> = {
  observed_true: 'teramati ada',
  observed_false: 'teramati tidak ada',
  unknown_unavailable: 'tidak diketahui (bukti tidak tersedia)',
}

const TEMPORAL_SEMANTICS: Record<string, string> = {
  historical_event: 'kejadian historis',
  current_state: 'keadaan saat ini',
  aggregated_window: 'jendela agregat',
  unknown: 'tidak diketahui',
}

const PARSE_STATUS: Record<string, string> = {
  parsed: 'terurai',
  failed: 'gagal diurai',
  empty: 'kosong',
}

export const epistemicClassLabel = (value: string): string => EPISTEMIC_CLASS[value] ?? value
export const availabilityLabel = (value: string): string => AVAILABILITY_STATUS[value] ?? value
export const evidenceStateLabel = (value: string): string => EVIDENCE_STATE[value] ?? value
export const temporalSemanticsLabel = (value: string): string => TEMPORAL_SEMANTICS[value] ?? value
export const parseStatusLabel = (value: string): string => PARSE_STATUS[value] ?? value
