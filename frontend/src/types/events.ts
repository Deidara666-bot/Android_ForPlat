// Closed event_type catalog: must stay identical to EVENT_TYPE_CATALOG in the backend (REF §EVT).
export const EVENT_TYPES = [
  'package_observed_installed',
  'uid_observed',
  'apk_identity_observed',
  'apk_endpoint_reference_observed',
  'scenario_subject_binding_observed',
  'synthetic_exclusion_marker_observed',
  'permission_observed_requested',
  'sensitive_communication_capability_observed_granted',
  'sensitive_communication_capability_observed_declared',
  'accessibility_service_observed_declared',
  'special_access_capability_observed_enabled',
  'special_access_capability_observed_declared',
  'event_trigger_capability_observed_declared',
  'service_observed_declared',
  'event_trigger_execution_observed',
  'app_usage_observed',
  'activity_observed_resumed',
  'process_observed_running',
  'uid_network_activity_observed',
  'local_endpoint_request_observed',
  'lab_network_flow_observed',
  'sms_record_observed',
  'contact_record_observed',
  'call_log_record_observed',
  'notification_context_observed',
] as const

export type EventType = (typeof EVENT_TYPES)[number]

export type EpistemicClass =
  | 'identity_attribute'
  | 'capability_state'
  | 'execution_observed'
  | 'data_present'

export type TemporalSemantics = 'historical_event' | 'current_state' | 'aggregated_window' | 'unknown'

export type EvidenceState = 'observed_true' | 'observed_false' | 'unknown_unavailable'

export type ParseStatus = 'parsed' | 'failed' | 'empty'

export type AvailabilityStatus = 'acquired' | 'unavailable' | 'denied' | 'unsupported' | 'failed'

export interface CaseInfo {
  id: string
  case_number: string
  title: string
  created_by: string
  created_at: string
}

export interface ArtifactProvenance {
  evidence_id: string
  acquisition_session_id: string
  operation_id: string
  sha256_agent: string | null
  sha256_server: string | null
  acquired_at: string
  availability_status: AvailabilityStatus
}

export interface ArtifactOut {
  id: string
  evidence_id: string
  artifact_type: string
  parser_name: string
  parser_version: string
  subject_key: string | null
  raw_value: string
  parsed_value_json: Record<string, unknown>
  parse_status: ParseStatus
  parse_note: string
  provenance: ArtifactProvenance
}

export interface EventProvenance {
  artifact_id: string
  artifact_type: string
  raw_value: string
  parser_name: string
  parser_version: string
  parse_status: ParseStatus
  evidence_id: string
  acquisition_session_id: string
  operation_id: string
  sha256_agent: string | null
  sha256_server: string | null
  acquired_at: string
}

export interface EventOut {
  id: string
  case_id: string
  artifact_id: string
  event_type: EventType
  epistemic_class: EpistemicClass
  subject_package: string | null
  subject_uid: number | null
  object_type: string
  object_value: string
  predicate_value: boolean | null
  event_time: string | null
  observed_at: string
  window_start: string | null
  window_end: string | null
  temporal_semantics: TemporalSemantics
  evidence_state: EvidenceState
  context_json: Record<string, unknown>
  provenance: EventProvenance
}
