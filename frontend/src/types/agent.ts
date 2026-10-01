export interface Agent {
  id: string
  agent_id: string
  version: string
  last_seen_at: string | null
  connected: boolean
}
