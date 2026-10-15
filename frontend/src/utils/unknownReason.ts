// No imports on purpose: this file is run directly by node in the plan card's failing test.
// An UNKNOWN condition is never shown without a reason; a missing reason is said out loud.

const REASON_LABEL: Record<string, string> = {
  availability_unavailable: 'sumber tidak tersedia',
  availability_denied: 'sumber ditolak',
  availability_unsupported: 'sumber tidak didukung',
  availability_failed: 'sumber gagal diperoleh',
  not_acquired: 'sumber belum diakuisisi',
  parse_incomplete: 'penguraian tidak lengkap',
  coverage_incomplete: 'cakupan tidak lengkap',
  conflicting_evidence: 'bukti bertentangan',
  no_applicable_profile: 'tidak ada profil yang berlaku',
}

export const REASON_MISSING = 'alasan tidak tersedia'

export interface UnknownReasonText {
  label: string
  raw: string | null
  note: string | null
}

/** `hasSources` is false when `selector_json.sources` is null (no producer of that fact exists). */
export function describeUnknownReason(reason: string | null, hasSources: boolean): UnknownReasonText {
  if (reason === null || reason === '') return { label: REASON_MISSING, raw: null, note: null }
  const label = REASON_LABEL[reason] ?? reason
  const note =
    reason === 'not_acquired' && !hasSources ? 'sumber belum tersedia di platform' : null
  return { label, raw: reason, note }
}

/** A condition bound to a run window while the run has none: the examiner must fill the window. */
export function needsWindowHint(
  reason: string | null,
  selector: { window?: unknown; time_binding?: string; operator?: string },
): boolean {
  if (reason !== 'coverage_incomplete') return false
  if (selector.window !== null && selector.window !== undefined) return false
  return (
    selector.time_binding === 'case_window' ||
    selector.time_binding === 'bucket_overlap' ||
    selector.operator === 'overlaps_window'
  )
}
