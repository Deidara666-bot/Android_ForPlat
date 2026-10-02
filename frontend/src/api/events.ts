import type { ArtifactOut, CaseInfo, EventOut, EventType } from '../types/events'
import { apiJson } from './client'

export function getCase(caseId: string): Promise<CaseInfo> {
  return apiJson<CaseInfo>(`/api/cases/${encodeURIComponent(caseId)}`)
}

export function getCaseArtifacts(caseId: string): Promise<ArtifactOut[]> {
  return apiJson<ArtifactOut[]>(`/api/cases/${encodeURIComponent(caseId)}/artifacts`)
}

export function getCaseEvents(caseId: string, eventType?: EventType): Promise<EventOut[]> {
  const query = eventType === undefined ? '' : `?event_type=${encodeURIComponent(eventType)}`
  return apiJson<EventOut[]>(`/api/cases/${encodeURIComponent(caseId)}/events${query}`)
}
