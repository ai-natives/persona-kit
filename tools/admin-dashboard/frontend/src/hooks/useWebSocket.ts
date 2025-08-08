import { useEffect, useState, useRef } from 'react'
import { ActivityEvent } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8104/ws/live'

export function useWebSocket() {
  const [events, setEvents] = useState<ActivityEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = () => {
    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping')
          }
        }, 30000)
        
        ws.addEventListener('close', () => {
          clearInterval(pingInterval)
        })
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          if (message.type === 'activity') {
            setEvents(prev => [message.data, ...prev].slice(0, 100)) // Keep last 100
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 3000)
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      // Retry after 3 seconds
      reconnectTimeoutRef.current = setTimeout(connect, 3000)
    }
  }

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return { events, isConnected }
}