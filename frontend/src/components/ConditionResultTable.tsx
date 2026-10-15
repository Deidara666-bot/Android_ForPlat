import type { ConditionResultOut } from '../types/evaluation'
import { conditionRoleLabel, conditionStateLabel, evidenceStateLabel } from '../utils/labels'
import ConflictEvidenceBadge from './ConflictEvidenceBadge'
import MissingEvidenceBadge from './MissingEvidenceBadge'

// Every condition is listed, TRUE, FALSE and UNKNOWN alike; supporting facts open per condition.
export default function ConditionResultTable({ conditions }: { conditions: ConditionResultOut[] }) {
  if (conditions.length === 0) return <p className="muted">Tidak ada kondisi yang dievaluasi.</p>
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Kondisi</th>
            <th>Peran</th>
            <th>Operator</th>
            <th>Keadaan</th>
            <th>Alasan / fakta penopang</th>
          </tr>
        </thead>
        <tbody>
          {conditions.map((condition) => (
            <tr key={condition.id}>
              <td>
                <code>{condition.condition_key}</code>
                <br />
                <code>{condition.selector_json.fact ?? ''}</code>
              </td>
              <td>
                {conditionRoleLabel(condition.role)} (<code>{condition.role}</code>)
              </td>
              <td>
                <code>{condition.operator}</code>
              </td>
              <td>
                {conditionStateLabel(condition.state)} (<code>{condition.state}</code>)
              </td>
              <td>
                {condition.state === 'UNKNOWN' && (
                  <MissingEvidenceBadge reason={condition.reason} selector={condition.selector_json} />
                )}
                <ConflictEvidenceBadge conflict={condition.conflict_reason} />
                {condition.facts.length > 0 && (
                  <details>
                    <summary>Fakta penopang ({condition.facts.length})</summary>
                    <ul className="sources">
                      {condition.facts.map((fact) => (
                        <li key={fact.id}>
                          <code>{fact.event_type}</code> · {fact.object_type}:{' '}
                          <code>{fact.object_value}</code>
                          {fact.predicate_value !== null && (
                            <> · predicate_value=<code>{String(fact.predicate_value)}</code></>
                          )}{' '}
                          · {evidenceStateLabel(fact.evidence_state)} (<code>{fact.evidence_state}</code>)
                          <br />
                          <span className="muted">
                            fakta <code>{fact.id}</code> · artefak <code>{fact.artifact_id}</code>
                          </span>
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
