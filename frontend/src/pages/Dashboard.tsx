import { useCallback, useEffect, useState } from 'react'
import { getHealth } from '../api/health'
import type { HealthResult } from '../types/health'

export default function Dashboard() {
  const [result, setResult] = useState<HealthResult | null>(null)

  const refresh = useCallback(() => {
    setResult(null)
    void getHealth().then(setResult)
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return (
    <>
      <h1>Dasbor</h1>
      <section className="card" aria-live="polite">
        <h2>Status layanan</h2>
        {result === null && <p>Memuat…</p>}
        {result?.kind === 'backend_unreachable' && (
          <p className="error">Backend tidak terjangkau.</p>
        )}
        {result?.kind === 'database_unreachable' && (
          <p className="error">Basis data tidak terjangkau.</p>
        )}
        {result?.kind === 'ok' && (
          <dl className="kv">
            <dt>Status</dt>
            <dd className="ok">{result.health.status}</dd>
            <dt>Lingkungan</dt>
            <dd>{result.health.app_env}</dd>
            <dt>Basis data</dt>
            <dd>{result.health.database === 'reachable' ? 'terjangkau' : 'tidak terjangkau'}</dd>
            <dt>Revisi Alembic</dt>
            <dd>{result.health.alembic_revision ?? 'belum dimigrasi'}</dd>
            <dt>Versi aplikasi</dt>
            <dd>{result.health.app_version}</dd>
          </dl>
        )}
        <p>
          <button type="button" className="secondary" onClick={refresh}>
            Muat ulang
          </button>
        </p>
      </section>
    </>
  )
}
