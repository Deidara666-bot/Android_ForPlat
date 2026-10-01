import { Outlet, useNavigate } from 'react-router'
import { logout } from '../api/auth'

export default function AppShell() {
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    void navigate('/login')
  }

  return (
    <>
      <header className="shell-header">
        <strong>Android ForPlat</strong>
        <button type="button" className="secondary" onClick={handleLogout}>
          Keluar
        </button>
      </header>
      <main className="shell-main">
        <Outlet />
      </main>
    </>
  )
}
