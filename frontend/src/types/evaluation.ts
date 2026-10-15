// Mirrors backend/app/schemas/evaluation.py.

export type EvidenceModeValue = 'installed_runtime' | 'apk_static'
export type RunPurposeValue = 'authoring' | 'holdout' | 'benign_control' | 'production'

export interface AnalyzeRequest {
  evidence_mode: EvidenceModeValue
  run_purpose: RunPurposeValue
  window_start?: string
  window_end?: string
  subjects?: string[]
}

export interface RunOut {
  id: string
  case_id: string
  evidence_mode: string
  run_purpose: string
  window_start: string | null
  window_end: string | null
  subjects: unknown[]
  rule_set_hash: string
  kb_hash: string
  code_commit: string
  created_at: string
}

export interface SubjectOut {
  package: string
  uid: number | null
  apk_sha256: string | null
}

export interface SupportingFactOut {
  id: string
  event_type: string
  object_type: string
  object_value: string
  predicate_value: boolean | null
  evidence_state: string
  temporal_semantics: string
  event_time: string | null
  observed_at: string
  artifact_id: string
}

export interface SourceRef {
  operation_id: string
  raw_source: string | null
  session_id: string
  evidence_ids: string[]
  availability_status: string
  reason: string | null
}

export interface SelectorJson {
  fact?: string
  operator?: string
  time_binding?: string
  window?: { start: string; end: string } | null
  sources?: SourceRef[] | null
  [key: string]: unknown
}

export interface ConditionResultOut {
  id: string
  condition_key: string
  role: string
  operator: string
  state: string
  reason: string | null
  conflict_reason: { fact_ids?: string[] } | null
  selector_json: SelectorJson
  facts: SupportingFactOut[]
}

export interface ProfileEvaluationOut {
  id: string
  profile_id: string
  claim_level: string | null
  evaluation_status: string
  outcome: string | null
  interpretation_status: string
  reason: string | null
  rule_id: string
  conditions: ConditionResultOut[]
}

export interface FamilyEvaluationOut {
  id: string
  family_id: string
  rule_version: number
  rule_status: string
  subject: SubjectOut
  evidence_mode: string
  run_purpose: string
  outcome: string
  matched_profile_ids: string[]
  interpretation_status: string
  reason: string | null
  profiles: ProfileEvaluationOut[]
}

export interface EvaluationsOut {
  run: RunOut | null
  families: FamilyEvaluationOut[]
}
