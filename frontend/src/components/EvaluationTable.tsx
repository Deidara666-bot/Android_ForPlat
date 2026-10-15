import type { FamilyEvaluationOut } from '../types/evaluation'
import {
  evidenceModeLabel,
  interpretationStatusLabel,
  outcomeLabel,
  runPurposeLabel,
} from '../utils/labels'
import FamilyProfilePanel from './FamilyProfilePanel'

function subjectText(family: FamilyEvaluationOut): string {
  const { subject } = family
  const parts = [subject.package]
  if (subject.uid !== null) parts.push(`UID ${subject.uid}`)
  return parts.join(' · ')
}

// Level 1: one card per (family, subject); levels 2 and 3 open inside it.
export default function EvaluationTable({ families }: { families: FamilyEvaluationOut[] }) {
  return (
    <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {families.map((family) => (
        <li className="card event" key={family.id}>
          <details>
            <summary>
              <strong>
                <code>{family.family_id}</code>
              </strong>{' '}
              · {subjectText(family)} · {outcomeLabel(family.outcome)} (<code>{family.outcome}</code>)
            </summary>
            <dl className="kv" style={{ marginTop: 8 }}>
              <dt>Subjek</dt>
              <dd>{subjectText(family)}</dd>
              {family.subject.apk_sha256 !== null && (
                <>
                  <dt>SHA-256 APK</dt>
                  <dd>
                    <code>{family.subject.apk_sha256}</code>
                  </dd>
                </>
              )}
              <dt>Mode</dt>
              <dd>
                {evidenceModeLabel(family.evidence_mode)} (<code>{family.evidence_mode}</code>) ·{' '}
                {runPurposeLabel(family.run_purpose)} (<code>{family.run_purpose}</code>)
              </dd>
              <dt>Versi aturan</dt>
              <dd>
                v{family.rule_version} · <code>{family.rule_status}</code>
              </dd>
              <dt>Interpretasi</dt>
              <dd>
                {interpretationStatusLabel(family.interpretation_status)} (
                <code>{family.interpretation_status}</code>)
              </dd>
              <dt>Profil terpenuhi</dt>
              <dd>
                {family.matched_profile_ids.length === 0
                  ? '—'
                  : family.matched_profile_ids.join(', ')}
              </dd>
            </dl>
            <FamilyProfilePanel family={family} />
          </details>
        </li>
      ))}
    </ol>
  )
}
