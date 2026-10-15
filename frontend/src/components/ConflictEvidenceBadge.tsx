// A conflict lists every fact id named in `conflict_reason`; none is dropped or preferred.
export default function ConflictEvidenceBadge({
  conflict,
}: {
  conflict: { fact_ids?: string[] } | null
}) {
  if (conflict === null) return null
  const ids = conflict.fact_ids ?? []
  return (
    <div className="conflict">
      <span className="badge">bukti bertentangan (<code>conflicting_evidence</code>)</span>
      {ids.length === 0 ? (
        <div className="muted">id fakta tidak tersedia</div>
      ) : (
        <ul className="sources">
          {ids.map((id) => (
            <li key={id}>
              <code>{id}</code>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
