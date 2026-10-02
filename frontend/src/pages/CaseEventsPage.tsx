import { useEffect, useState } from 'react'
import { useParams } from 'react-router'
import { getCase, getCaseArtifacts, getCaseEvents } from '../api/events'
import ArtifactTable from '../components/ArtifactTable'
import EventTimeline from '../components/EventTimeline'
import { EVENT_TYPES } from '../types/events'
import type { ArtifactOut, CaseInfo, EventOut, EventType } from '../types/events'

type Loaded = { caseInfo: CaseInfo; events: EventOut[]; artifacts: ArtifactOut[] }
type State = { kind: 'loading' } | { kind: 'error'; message: string } | ({ kind: 'ready' } & Loaded)

function isEventType(value: string): value is EventType {
  return (EVENT_TYPES as readonly string[]).includes(value)
}

export default function CaseEventsPage() {
  const { id = '' } = useParams()
  const [filter, setFilter] = useState<EventType | ''>('')
  const [state, setState] = useState<State>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false
    setState({ kind: 'loading' })
    Promise.all([
      getCase(id),
      getCaseEvents(id, filter === '' ? undefined : filter),
      getCaseArtifacts(id),
    ])
      .then(([caseInfo, events, artifacts]) => {
        if (!cancelled) setState({ kind: 'ready', caseInfo, events, artifacts })
      })
      .catch(() => {
        if (!cancelled) setState({ kind: 'error', message: 'Kasus atau datanya tidak dapat dimuat.' })
      })
    return () => {
      cancelled = true
    }
  }, [id, filter])

  return (
    <>
      {state.kind === 'loading' && <p>Memuat…</p>}
      {state.kind === 'error' && <p className="error">{state.message}</p>}
      {state.kind === 'ready' && (
        <>
          <h1>Kasus {state.caseInfo.case_number}</h1>
          <p>{state.caseInfo.title}</p>

          <h2 style={{ marginTop: 24 }}>Fakta ternormalisasi</h2>
          <p>
            <label>
              Jenis fakta{' '}
              <select
                value={filter}
                onChange={(event) => {
                  const value = event.target.value
                  setFilter(isEventType(value) ? value : '')
                }}
              >
                <option value="">Semua</option>
                {EVENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>
          </p>
          {state.events.length === 0 ? (
            <p>Belum ada fakta ternormalisasi untuk kasus ini.</p>
          ) : (
            <EventTimeline events={state.events} />
          )}

          <h2 style={{ marginTop: 24 }}>Artefak</h2>
          {state.artifacts.length === 0 ? (
            <p>Belum ada artefak untuk kasus ini.</p>
          ) : (
            <ArtifactTable artifacts={state.artifacts} />
          )}
        </>
      )}
    </>
  )
}
