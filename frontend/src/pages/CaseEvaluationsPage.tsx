import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useParams } from 'react-router'
import { getEvaluations, runAnalysis } from '../api/analysis'
import { getCase } from '../api/events'
import EvaluationTable from '../components/EvaluationTable'
import type { CaseInfo } from '../types/events'
import type { EvaluationsOut, EvidenceModeValue, RunPurposeValue } from '../types/evaluation'
import { evidenceModeLabel, formatTime, runPurposeLabel } from '../utils/labels'

const MODES: EvidenceModeValue[] = ['installed_runtime', 'apk_static']
const PURPOSES: RunPurposeValue[] = ['authoring', 'benign_control', 'holdout', 'production']

// Working texts for the machine codes of 409/422 (the raw code is always shown next to them).
const ERROR_TEXT: Record<string, string> = {
  invalid_window: 'jendela tidak sah: awal dan akhir harus keduanya diisi, awal lebih dulu dari akhir',
  no_subjects: 'tidak ada subjek untuk dianalisis pada kasus ini',
  status_not_allowed: 'status aturan tidak mengizinkan tujuan run ini',
  code_commit_unverified: 'commit kode belum terverifikasi (perubahan belum di-commit atau tidak terbaca)',
  request_validation_failed: 'isian form tidak sah',
}

type State =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; caseInfo: CaseInfo; data: EvaluationsOut }

function toIso(local: string): string | undefined {
  if (local === '') return undefined
  const date = new Date(local)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

export default function CaseEvaluationsPage() {
  const { id = '' } = useParams()
  const [state, setState] = useState<State>({ kind: 'loading' })
  const [mode, setMode] = useState<EvidenceModeValue>('installed_runtime')
  const [purpose, setPurpose] = useState<RunPurposeValue>('authoring')
  const [windowStart, setWindowStart] = useState('')
  const [windowEnd, setWindowEnd] = useState('')
  const [subjects, setSubjects] = useState('')
  const [running, setRunning] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const [caseInfo, data] = await Promise.all([getCase(id), getEvaluations(id)])
      setState({ kind: 'ready', caseInfo, data })
    } catch {
      setState({ kind: 'error', message: 'Kasus atau hasil evaluasinya tidak dapat dimuat.' })
    }
  }, [id])

  useEffect(() => {
    setState({ kind: 'loading' })
    void load()
  }, [load])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    const names = subjects
      .split(/[\s,]+/)
      .map((name) => name.trim())
      .filter((name) => name !== '')
    const start = toIso(windowStart)
    const end = toIso(windowEnd)
    setRunning(true)
    try {
      const result = await runAnalysis(id, {
        evidence_mode: mode,
        run_purpose: purpose,
        ...(start !== undefined ? { window_start: start } : {}),
        ...(end !== undefined ? { window_end: end } : {}),
        ...(names.length > 0 ? { subjects: names } : {}),
      })
      if (!result.ok) {
        const text = ERROR_TEXT[result.code] ?? 'analisis ditolak'
        const extra = result.detail === null ? '' : ` · ${result.detail}`
        setFormError(`${text} (${result.code}, HTTP ${result.status}${extra})`)
        return
      }
      await load()
    } catch {
      setFormError('Analisis tidak dapat dijalankan (jaringan atau server).')
    } finally {
      setRunning(false)
    }
  }

  return (
    <>
      {state.kind === 'loading' && <p>Memuat…</p>}
      {state.kind === 'error' && <p className="error">{state.message}</p>}
      {state.kind === 'ready' && (
        <>
          <h1>Kasus {state.caseInfo.case_number}</h1>
          <p>{state.caseInfo.title}</p>

          <h2 style={{ marginTop: 24 }}>Analisis</h2>
          <form className="form" onSubmit={(event) => void onSubmit(event)}>
            <label>
              Mode bukti
              <select value={mode} onChange={(e) => setMode(e.target.value as EvidenceModeValue)}>
                {MODES.map((value) => (
                  <option key={value} value={value}>
                    {evidenceModeLabel(value)} ({value})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Tujuan run
              <select value={purpose} onChange={(e) => setPurpose(e.target.value as RunPurposeValue)}>
                {PURPOSES.map((value) => (
                  <option key={value} value={value}>
                    {runPurposeLabel(value)} ({value})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Jendela awal (opsional)
              <input
                type="datetime-local"
                value={windowStart}
                onChange={(e) => setWindowStart(e.target.value)}
              />
            </label>
            <label>
              Jendela akhir (opsional)
              <input
                type="datetime-local"
                value={windowEnd}
                onChange={(e) => setWindowEnd(e.target.value)}
              />
            </label>
            <label>
              Subjek (nama paket, dipisah koma; kosong = semua)
              <input value={subjects} onChange={(e) => setSubjects(e.target.value)} />
            </label>
            <button type="submit" disabled={running}>
              {running ? 'Menganalisis…' : 'Analisis'}
            </button>
            {formError !== null && <p className="error">{formError}</p>}
          </form>

          <h2 style={{ marginTop: 24 }}>Hasil evaluasi</h2>
          {state.data.run === null ? (
            <p>Belum ada analisis untuk kasus ini.</p>
          ) : (
            <>
              <dl className="kv" style={{ marginBottom: 12 }}>
                <dt>Run</dt>
                <dd>
                  <code>{state.data.run.id}</code>
                </dd>
                <dt>Dibuat</dt>
                <dd>{formatTime(state.data.run.created_at)}</dd>
                <dt>Mode · tujuan</dt>
                <dd>
                  {evidenceModeLabel(state.data.run.evidence_mode)} ·{' '}
                  {runPurposeLabel(state.data.run.run_purpose)}
                </dd>
                <dt>Jendela</dt>
                <dd>
                  {state.data.run.window_start === null || state.data.run.window_end === null
                    ? 'tidak diisi'
                    : `${state.data.run.window_start} → ${state.data.run.window_end}`}
                </dd>
                <dt>Commit kode</dt>
                <dd>
                  <code>{state.data.run.code_commit}</code>
                </dd>
              </dl>
              {state.data.families.length === 0 ? (
                <p>Run ini tidak memuat evaluasi keluarga.</p>
              ) : (
                <EvaluationTable families={state.data.families} />
              )}
            </>
          )}
        </>
      )}
    </>
  )
}
