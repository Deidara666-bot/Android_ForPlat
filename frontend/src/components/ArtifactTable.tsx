import type { ArtifactOut } from '../types/events'
import { availabilityLabel, parseStatusLabel } from '../utils/labels'

// Failed and empty artifacts are listed like the others, with their parse note visible.
export default function ArtifactTable({ artifacts }: { artifacts: ArtifactOut[] }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Tipe</th>
            <th>Subjek</th>
            <th>Nilai mentah</th>
            <th>Status urai</th>
            <th>Catatan urai</th>
            <th>Pengurai</th>
            <th>Bukti</th>
          </tr>
        </thead>
        <tbody>
          {artifacts.map((artifact) => (
            <tr key={artifact.id}>
              <td>{artifact.artifact_type}</td>
              <td>{artifact.subject_key ?? '—'}</td>
              <td>
                <code>{artifact.raw_value === '' ? '(kosong)' : artifact.raw_value}</code>
              </td>
              <td className={artifact.parse_status === 'failed' ? 'error' : undefined}>
                {parseStatusLabel(artifact.parse_status)}
              </td>
              <td>{artifact.parse_note === '' ? '—' : artifact.parse_note}</td>
              <td>
                {artifact.parser_name} v{artifact.parser_version}
              </td>
              <td>
                <code>{artifact.provenance.operation_id}</code>
                <br />
                {availabilityLabel(artifact.provenance.availability_status)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
