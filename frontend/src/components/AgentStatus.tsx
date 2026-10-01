import type { Agent } from '../types/agent'
import { formatTime } from '../utils/labels'

export default function AgentStatus({ agents }: { agents: Agent[] }) {
  return (
    <section className="card" aria-live="polite">
      <h2>Agen</h2>
      {agents.length === 0 && <p>Belum ada agen terdaftar.</p>}
      {agents.map((agent) => (
        <dl className="kv" key={agent.id}>
          <dt>Agen</dt>
          <dd>{agent.agent_id}</dd>
          <dt>Status</dt>
          <dd className={agent.connected ? 'ok' : 'error'}>
            {agent.connected ? 'terhubung' : 'terputus'}
          </dd>
          <dt>Versi</dt>
          <dd>{agent.version}</dd>
          <dt>Terakhir terlihat</dt>
          <dd>{formatTime(agent.last_seen_at)}</dd>
        </dl>
      ))}
    </section>
  )
}
