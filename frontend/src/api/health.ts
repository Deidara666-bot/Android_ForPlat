import type { Health, HealthResult } from '../types/health'
import { apiFetch } from './client'

export async function getHealth(): Promise<HealthResult> {
  let response: Response
  try {
    response = await apiFetch('/api/health')
  } catch {
    return { kind: 'backend_unreachable' }
  }
  if (response.status === 503) return { kind: 'database_unreachable' }
  if (!response.ok) return { kind: 'backend_unreachable' }
  return { kind: 'ok', health: (await response.json()) as Health }
}
