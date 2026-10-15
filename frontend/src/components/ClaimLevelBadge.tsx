import { claimLevelLabel } from '../utils/labels'

// The badge names the claim level of a profile; it is not a verdict and has no severity colour.
export default function ClaimLevelBadge({ level }: { level: string | null }) {
  if (level === null) return <span className="badge muted">tingkat klaim tidak ada</span>
  return (
    <span className="badge" title={level}>
      {claimLevelLabel(level)} (<code>{level}</code>)
    </span>
  )
}
