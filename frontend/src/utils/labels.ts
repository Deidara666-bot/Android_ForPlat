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

// Evaluation labels: outcome / condition state follow 4.7; the rest are working labels (REF ENGINE
// "Label kerja UI"), always shown with the raw value.
const OUTCOME: Record<string, string> = {
  matched: 'terpenuhi',
  not_matched: 'tidak terpenuhi',
  insufficient_evidence: 'bukti tidak memadai',
}

const CONDITION_STATE: Record<string, string> = {
  TRUE: 'terpenuhi',
  FALSE: 'tidak terpenuhi',
  UNKNOWN: 'tidak diketahui',
}

const CONDITION_ROLE: Record<string, string> = {
  required: 'wajib',
  optional: 'opsional',
  contextual: 'kontekstual',
  exclusionary: 'eksklusioner',
}

const EVALUATION_STATUS: Record<string, string> = {
  evaluated: 'dievaluasi',
  skipped_not_applicable: 'tidak berlaku',
}

const INTERPRETATION_STATUS: Record<string, string> = {
  normal: 'normal',
  constrained: 'tertahan',
}

const CLAIM_LEVEL: Record<string, string> = {
  identity: 'identitas',
  capability: 'kapabilitas',
  observed_activity: 'aktivitas teramati',
  contextual_cooccurrence: 'ko-okurensi kontekstual',
}

const EVIDENCE_MODE: Record<string, string> = {
  installed_runtime: 'runtime terpasang',
  apk_static: 'APK statis',
}

const RUN_PURPOSE: Record<string, string> = {
  authoring: 'authoring',
  holdout: 'holdout',
  benign_control: 'kontrol benign',
  production: 'produksi',
}

export const outcomeLabel = (value: string): string => OUTCOME[value] ?? value
export const conditionStateLabel = (value: string): string => CONDITION_STATE[value] ?? value
export const conditionRoleLabel = (value: string): string => CONDITION_ROLE[value] ?? value
export const evaluationStatusLabel = (value: string): string => EVALUATION_STATUS[value] ?? value
export const interpretationStatusLabel = (value: string): string =>
  INTERPRETATION_STATUS[value] ?? value
export const claimLevelLabel = (value: string): string => CLAIM_LEVEL[value] ?? value
export const evidenceModeLabel = (value: string): string => EVIDENCE_MODE[value] ?? value
export const runPurposeLabel = (value: string): string => RUN_PURPOSE[value] ?? value

export const epistemicClassLabel =(value: string): string => EPISTEMIC_CLASS[value] ?? value
export const availabilityLabel = (value: string): string => AVAILABILITY_STATUS[value] ?? value
export const evidenceStateLabel = (value: string): string => EVIDENCE_STATE[value] ?? value
export const temporalSemanticsLabel = (value: string): string => TEMPORAL_SEMANTICS[value] ?? value
export const parseStatusLabel = (value: string): string => PARSE_STATUS[value] ?? value
