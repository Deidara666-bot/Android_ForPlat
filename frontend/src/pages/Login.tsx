import { useState, type SubmitEvent } from 'react'
import { useNavigate } from 'react-router'
import { login } from '../api/auth'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (await login(email, password)) {
        void navigate('/dashboard')
      } else {
        setError('E-mail atau kata sandi salah.')
      }
    } catch {
      setError('Server tidak terjangkau. Coba lagi.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="shell-main">
      <h1>Masuk pemeriksa</h1>
      <form className="form" onSubmit={(event) => void handleSubmit(event)}>
        <label>
          E-mail
          <input
            type="text"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Kata sandi
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        {error !== null && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={busy}>
          Masuk
        </button>
      </form>
    </main>
  )
}
