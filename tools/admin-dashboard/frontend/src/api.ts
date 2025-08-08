const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8104'

export async function fetchMetrics() {
  const response = await fetch(`${API_URL}/api/metrics/overview`)
  if (!response.ok) throw new Error('Failed to fetch metrics')
  return response.json()
}

export async function fetchActivityFeed(limit = 100, eventType?: string) {
  const params = new URLSearchParams({ limit: limit.toString() })
  if (eventType) params.append('event_type', eventType)
  
  const response = await fetch(`${API_URL}/api/activity/feed?${params}`)
  if (!response.ok) throw new Error('Failed to fetch activity feed')
  return response.json()
}

export async function fetchAppStats() {
  const response = await fetch(`${API_URL}/api/apps/stats`)
  if (!response.ok) throw new Error('Failed to fetch app stats')
  return response.json()
}

export async function fetchPersonTimeline(personId: string) {
  const response = await fetch(`${API_URL}/api/persons/${personId}/timeline`)
  if (!response.ok) throw new Error('Failed to fetch person timeline')
  return response.json()
}