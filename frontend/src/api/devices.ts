import type { Device } from '../types/device'
import { apiJson } from './client'

export function listDevices(): Promise<Device[]> {
  return apiJson<Device[]>('/api/devices')
}
