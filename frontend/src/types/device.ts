export interface Device {
  id: string
  serial: string
  manufacturer: string
  model: string
  android_version: string
  api_level: number
  device_build: string
  connection_state: string
  last_seen_at: string
}

export type DashboardEvent =
  | { type: 'agent_status'; agent_id: string; connected: boolean }
  | { type: 'devices_changed' }
