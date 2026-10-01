import { useCallback, useEffect, useState } from 'react'
import { listAgents } from '../api/agents'
import { listDevices } from '../api/devices'
import { getHealth } from '../api/health'
import AgentStatus from '../components/AgentStatus'
import DeviceCard from '../components/DeviceCard'
import { useDashboardSocket } from '../hooks/useDashboardSocket'
import type { Agent } from '../types/agent'
import type { DashboardEvent, Device } from '../types/device'
import type { HealthResult } from '../types/health'

export default function Dashboard() {
  const [result, setResult] = useState<HealthResult | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [devices, setDevices] = useState<Device[]>([])

  const refresh = useCallback(() => {
    setResult(null)
    void getHealth().then(setResult)
  }, [])
  const loadAgents = useCallback(() => {
    void listAgents()
      .then(setAgents)
      .catch(() => undefined)
  }, [])
  const loadDevices = useCallback(() => {
    void listDevices()
      .then(setDevices)
      .catch(() => undefined)
  }, [])

  const handleEvent = useCallback(
    (event: DashboardEvent) => {
      if (event.type === 'devices_changed') {
        loadDevices()
        return
      }
      setAgents((current) => {
        if (!current.some((agent) => agent.agent_id === event.agent_id)) {
          loadAgents() // an agent that is not listed yet
          return current
        }
        return current.map((agent) =>
          agent.agent_id === event.agent_id ? { ...agent, connected: event.connected } : agent,
        )
      })
    },
    [loadAgents, loadDevices],
  )
  const handleOpen = useCallback(() => {
    loadAgents()
    loadDevices()
  }, [loadAgents, loadDevices])
  useDashboardSocket(handleEvent, handleOpen)

  useEffect(() => {
    refresh()
    loadAgents()
    loadDevices()
  }, [refresh, loadAgents, loadDevices])

  return (
    <>
      <h1>Dasbor</h1>
      <section className="card" aria-live="polite">
        <h2>Status layanan</h2>
        {result === null && <p>Memuat…</p>}
        {result?.kind === 'backend_unreachable' && (
          <p className="error">Backend tidak terjangkau.</p>
        )}
        {result?.kind === 'database_unreachable' && (
          <p className="error">Basis data tidak terjangkau.</p>
        )}
        {result?.kind === 'ok' && (
          <dl className="kv">
            <dt>Status</dt>
            <dd className="ok">{result.health.status}</dd>
            <dt>Lingkungan</dt>
            <dd>{result.health.app_env}</dd>
            <dt>Basis data</dt>
            <dd>{result.health.database === 'reachable' ? 'terjangkau' : 'tidak terjangkau'}</dd>
            <dt>Revisi Alembic</dt>
            <dd>{result.health.alembic_revision ?? 'belum dimigrasi'}</dd>
            <dt>Versi aplikasi</dt>
            <dd>{result.health.app_version}</dd>
          </dl>
        )}
        <p>
          <button type="button" className="secondary" onClick={refresh}>
            Muat ulang
          </button>
        </p>
      </section>
      <h2 style={{ marginTop: 24 }}>Agen dan perangkat</h2>
      <AgentStatus agents={agents} />
      {devices.length === 0 && <p>Belum ada perangkat terdeteksi.</p>}
      {devices.map((device) => (
        <DeviceCard device={device} key={device.id} />
      ))}
    </>
  )
}
