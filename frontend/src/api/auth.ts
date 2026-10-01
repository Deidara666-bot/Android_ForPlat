import { apiFetch, getToken, setToken } from './client'

export function isLoggedIn(): boolean {
  return getToken() !== null
}

export function logout(): void {
  setToken(null)
}

/** Returns true on success; false when the credentials are rejected. */
export async function login(email: string, password: string): Promise<boolean> {
  const response = await apiFetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (response.status === 401) return false
  if (!response.ok) throw new Error(`Login gagal (${response.status})`)
  const body = (await response.json()) as { access_token: string }
  setToken(body.access_token)
  return true
}
