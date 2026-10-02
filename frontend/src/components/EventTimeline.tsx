import type { EventOut } from '../types/events'
import { formatEventTime } from '../utils/eventTime'
import {
  epistemicClassLabel,
  evidenceStateLabel,
  parseStatusLabel,
  temporalSemanticsLabel,
} from '../utils/labels'

function subjectText(event: EventOut): string {
  const parts: string[] = []
  if (event.subject_package !== null) parts.push(event.subject_package)
  if (event.subject_uid !== null) parts.push(`UID ${event.subject_uid}`)
  return parts.length > 0 ? parts.join(' · ') : 'tanpa subjek'
}

// Events are shown in the order the API returns them; the list is never re-sorted here.
export default function EventTimeline({ events }: { events: EventOut[] }) {
  return (
    <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {events.map((event) => {
        const time = formatEventTime(event)
        const { provenance } = event
        return (
          <li className="card event" key={event.id}>
            <h3 style={{ margin: 0 }}>
              <code>{event.event_type}</code>
            </h3>
            <dl className="kv" style={{ marginTop: 8 }}>
              <dt>Kelas</dt>
              <dd>
                {epistemicClassLabel(event.epistemic_class)} (<code>{event.epistemic_class}</code>)
              </dd>
              <dt>Subjek</dt>
              <dd>{subjectText(event)}</dd>
              <dt>Objek</dt>
              <dd>
                {event.object_type}: <code>{event.object_value}</code>
              </dd>
              <dt>Waktu</dt>
              <dd className={time.isEventTime ? undefined : 'muted'}>{time.label}</dd>
              <dt>Semantik waktu</dt>
              <dd>
                {temporalSemanticsLabel(event.temporal_semantics)} (
                <code>{event.temporal_semantics}</code>)
              </dd>
              <dt>Keadaan bukti</dt>
              <dd>
                {evidenceStateLabel(event.evidence_state)} (<code>{event.evidence_state}</code>)
              </dd>
            </dl>
            <details>
              <summary>Asal-usul</summary>
              <dl className="kv" style={{ marginTop: 8 }}>
                <dt>Operasi</dt>
                <dd>
                  <code>{provenance.operation_id}</code>
                </dd>
                <dt>Diperoleh pada</dt>
                <dd>{provenance.acquired_at}</dd>
                <dt>Sesi akuisisi</dt>
                <dd>
                  <code>{provenance.acquisition_session_id}</code>
                </dd>
                <dt>Bukti mentah</dt>
                <dd>
                  <code>{provenance.evidence_id}</code>
                </dd>
                <dt>SHA-256 agen</dt>
                <dd>
                  <code>{provenance.sha256_agent ?? 'tidak ada'}</code>
                </dd>
                <dt>SHA-256 server</dt>
                <dd>
                  <code>{provenance.sha256_server ?? 'tidak ada'}</code>
                </dd>
                <dt>Artefak</dt>
                <dd>
                  <code>{provenance.artifact_id}</code> · {provenance.artifact_type} ·{' '}
                  {parseStatusLabel(provenance.parse_status)}
                </dd>
                <dt>Pengurai</dt>
                <dd>
                  {provenance.parser_name} v{provenance.parser_version}
                </dd>
                <dt>Nilai mentah</dt>
                <dd>
                  <code>{provenance.raw_value}</code>
                </dd>
              </dl>
            </details>
          </li>
        )
      })}
    </ol>
  )
}
