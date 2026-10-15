import type { SelectorJson } from '../types/evaluation'
import { availabilityLabel } from '../utils/labels'
import { describeUnknownReason, needsWindowHint } from '../utils/unknownReason'

// An UNKNOWN condition always carries its reason; a missing one is stated, never hidden.
export default function MissingEvidenceBadge({
  reason,
  selector,
}: {
  reason: string | null
  selector: SelectorJson
}) {
  const sources = selector.sources ?? null
  const text = describeUnknownReason(reason, sources !== null)
  return (
    <div className="missing">
      <span className="badge" data-testid="unknown-reason">
        {text.label}
        {text.raw !== null && (
          <>
            {' '}
            (<code>{text.raw}</code>)
          </>
        )}
      </span>
      {text.note !== null && <div className="muted">{text.note}</div>}
      {needsWindowHint(reason, selector) && (
        <div className="muted">Isi jendela waktu pada form Analisis, lalu jalankan ulang.</div>
      )}
      {sources !== null && sources.length > 0 && (
        <ul className="sources">
          {sources.map((source) => (
            <li key={`${source.session_id}-${source.raw_source ?? source.operation_id}`}>
              <code>{source.operation_id}</code>
              {source.raw_source !== null && <> · <code>{source.raw_source}</code></>} ·{' '}
              {availabilityLabel(source.availability_status)} (
              <code>{source.availability_status}</code>)
              {source.reason !== null && <> · {source.reason}</>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
