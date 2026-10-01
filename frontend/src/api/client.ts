const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ''
const TOKEN_KEY = 'forplat_access_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string | null): void {
  try {
    if (token === null) localStorage.removeItem(TOKEN_KEY)
    else localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // storage unavailable: the session just will not persist
  }
}

/**
 * `auth: false` skips the Bearer header and the expired-session handling (used by login itself,
 * where a 401 means "wrong credentials", not "session expired").
 */
export async function apiFetch(
  path: string,
  init: RequestInit = {},
  { auth = true }: { auth?: boolean } = {},
): Promise<Response> {
  const headers = new Headers(init.headers)
  const token = auth ? getToken() : null
  if (token !== null) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  if (token !== null && response.status === 401) {
    setToken(null)
    window.location.assign('/login')
  }
  return response
}

export async function apiJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await apiFetch(path, init)
  if (!response.ok) throw new ApiError(response.status, response.statusText)
  return (await response.json()) as T
}
