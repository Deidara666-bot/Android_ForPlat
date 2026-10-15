import type { FamilyEvaluationOut } from '../types/evaluation'
import {
  evaluationStatusLabel,
  interpretationStatusLabel,
  outcomeLabel,
} from '../utils/labels'
import ClaimLevelBadge from './ClaimLevelBadge'
import ConditionResultTable from './ConditionResultTable'

// Every profile can be opened, whether matched, not matched, insufficient or skipped.
export default function FamilyProfilePanel({ family }: { family: FamilyEvaluationOut }) {
  return (
    <div className="panel">
      {family.reason !== null && (
        <p className="muted">
          Alasan keluarga: <code>{family.reason}</code>
        </p>
      )}
      {family.profiles.length === 0 && <p className="muted">Tidak ada profil pada keluarga ini.</p>}
      {family.profiles.map((profile) => (
        <details className="card profile" key={profile.id}>
          <summary>
            <code>{profile.profile_id}</code> ·{' '}
            {profile.outcome === null ? (
              <>
                {evaluationStatusLabel(profile.evaluation_status)} (
                <code>{profile.evaluation_status}</code>)
              </>
            ) : (
              <>
                {outcomeLabel(profile.outcome)} (<code>{profile.outcome}</code>)
              </>
            )}{' '}
            · <ClaimLevelBadge level={profile.claim_level} />
          </summary>
          <dl className="kv" style={{ marginTop: 8 }}>
            <dt>Status evaluasi</dt>
            <dd>
              {evaluationStatusLabel(profile.evaluation_status)} (
              <code>{profile.evaluation_status}</code>)
            </dd>
            <dt>Interpretasi</dt>
            <dd>
              {interpretationStatusLabel(profile.interpretation_status)} (
              <code>{profile.interpretation_status}</code>)
            </dd>
            {profile.reason !== null && (
              <>
                <dt>Alasan</dt>
                <dd>
                  <code>{profile.reason}</code>
                </dd>
              </>
            )}
            <dt>Aturan</dt>
            <dd>
              <code>{profile.rule_id}</code>
            </dd>
          </dl>
          {profile.evaluation_status === 'skipped_not_applicable' ? (
            <p className="muted">Profil tidak berlaku pada mode / tujuan run ini; kondisi tidak dievaluasi.</p>
          ) : (
            <ConditionResultTable conditions={profile.conditions} />
          )}
        </details>
      ))}
    </div>
  )
}
