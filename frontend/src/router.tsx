import { createBrowserRouter, redirect } from 'react-router'
import { isLoggedIn } from './api/auth'
import AppShell from './components/AppShell'
import CaseEvaluationsPage from './pages/CaseEvaluationsPage'
import CaseEventsPage from './pages/CaseEventsPage'
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
    children: [
      { path: '/dashboard', element: <Dashboard /> },
      { path: '/cases/:id/events', element: <CaseEventsPage /> },
      { path: '/cases/:id/evaluations', element: <CaseEvaluationsPage /> },
    ],
  },
])
