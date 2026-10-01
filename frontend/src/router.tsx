import { createBrowserRouter, redirect } from 'react-router'
import { isLoggedIn } from './api/auth'
import AppShell from './components/AppShell'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'

function requireLogin() {
  if (!isLoggedIn()) return redirect('/login')
  return null
}

export const router = createBrowserRouter([
  { path: '/', loader: () => redirect('/dashboard') },
  { path: '/login', element: <Login /> },
  {
    element: <AppShell />,
    loader: requireLogin,
    children: [{ path: '/dashboard', element: <Dashboard /> }],
  },
])
