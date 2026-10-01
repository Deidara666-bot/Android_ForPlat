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
