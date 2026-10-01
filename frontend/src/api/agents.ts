import type { Agent } from '../types/agent'
import { apiJson } from './client'

export function listAgents(): Promise<Agent[]> {
  return apiJson<Agent[]>('/api/agents')
}
