import type { AnalyzeRequest, EvaluationsOut } from '../types/evaluation'
import { apiFetch, apiJson } from './client'

export function getEvaluations(caseId: string, runId?: string): Promise<EvaluationsOut> {
  const query = runId === undefined ? '' : `?run=${encodeURIComponent(runId)}`
  return apiJson<EvaluationsOut>(`/api/cases/${encodeURIComponent(caseId)}/evaluations${query}`)
}

export type AnalyzeResult =
  | { ok: true; runId: string }
  | { ok: false; status: number; code: string; detail: string | null }

// 409 and 422 carry a machine code (`status_not_allowed`, `invalid_window`, `no_subjects`, ...);
// it is returned as-is so the page can show it next to the Indonesian text.
export async function runAnalysis(caseId: string, body: AnalyzeRequest): Promise<AnalyzeResult> {
  const response = await apiFetch(`/api/cases/${encodeURIComponent(caseId)}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (response.ok) {
    const data = (await response.json()) as { correlation_run_id: string }
    return { ok: true, runId: data.correlation_run_id }
  }
  let code = `http_${response.status}`
  let detail: string | null = null
  try {
    const data = (await response.json()) as { detail?: unknown }
    const info = data.detail
    if (typeof info === 'object' && info !== null && !Array.isArray(info)) {
      const record = info as Record<string, unknown>
      if (typeof record.code === 'string') code = record.code
      const extra = record.path ?? record.message
      if (typeof extra === 'string') detail = extra
    } else if (typeof info === 'string') {
      code = info
    } else if (Array.isArray(info)) {
      code = 'request_validation_failed'
    }
  } catch {
    // body not JSON: keep the generic code
  }
  return { ok: false, status: response.status, code, detail }
}
