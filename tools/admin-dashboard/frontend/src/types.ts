export interface ActivityEvent {
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR'
  event_type: string
  message: string
  details: Record<string, any>
  app_name?: string
  person_id?: string
}

export interface MetricSnapshot {
  timestamp: string
  active_users: number
  api_calls_per_hour: number
  avg_latency_ms: number
  trait_updates_per_hour: number
  error_rate: number
  active_apps: string[]
}

export interface AppStats {
  name: string
  user_count: number
  api_calls_per_hour: number
  last_activity?: string
}

export interface PersonTimeline {
  person_id: string
  events: ActivityEvent[]
  mindscape?: any
  active_personas?: any[]
}