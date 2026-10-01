import { useEffect, useRef } from 'react'
import { apiFetch, getToken } from '../api/client'
import type { DashboardEvent } from '../types/device'

const RECONNECT_MS = 3000

function socketUrl(token: string): string {
  const configured: string | undefined = import.meta.env.VITE_WS_BASE_URL
  const base = configured ?? window.location.origin.replace(/^http/, 'ws')
  return `${base}/ws/dashboard?token=${encodeURIComponent(token)}`
}

/**
 * Keeps a dashboard WebSocket open (reconnecting while mounted). `onEvent` receives live changes;
 * `onOpen` fires on every (re)connection so the caller can refetch what it may have missed.
 */
export function useDashboardSocket(
  onEvent: (event: DashboardEvent) => void,
  onOpen: () => void,
): void {
  const handlers = useRef({ onEvent, onOpen })
  useEffect(() => {
    handlers.current = { onEvent, onOpen }
  })

  useEffect(() => {
    let socket: WebSocket | null = null
    let timer: ReturnType<typeof setTimeout> | null = null
    let closed = false

    function connect() {
      const token = getToken()
      if (token === null || closed) return
      socket = new WebSocket(socketUrl(token))
      socket.onopen = () => handlers.current.onOpen()
      socket.onmessage = (message: MessageEvent<string>) => {
        try {
          handlers.current.onEvent(JSON.parse(message.data) as DashboardEvent)
        } catch {
          // ignore a malformed notification
        }
      }
      socket.onclose = () => {
        if (closed) return
        // A refused socket may mean an expired session: this call logs out and returns to /login on 401.
        void apiFetch('/api/auth/me')
          .catch(() => undefined)
          .finally(() => {
            if (!closed) timer = setTimeout(connect, RECONNECT_MS)
          })
      }
    }

    connect()
    return () => {
      closed = true
      if (timer !== null) clearTimeout(timer)
      socket?.close()
    }
  }, [])
}
