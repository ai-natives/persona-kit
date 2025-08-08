import { useQuery } from '@tanstack/react-query'
import { fetchAppStats } from '../api'
import { AppStats } from '../types'
import { formatDistanceToNow } from 'date-fns'

const appIcons: Record<string, string> = {
  'career-navigator': '💼',
  'agno-coaching-ui': '📚',
  'personakit-explorer': '🧪',
}

function AppCard({ app }: { app: AppStats }) {
  return (
    <div className="bg-pk-surface border border-pk-border rounded-lg p-6 hover:border-pk-muted transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{appIcons[app.name] || '📱'}</span>
          <div>
            <h4 className="font-semibold capitalize">
              {app.name.replace(/-/g, ' ')}
            </h4>
            {app.last_activity && (
              <p className="text-xs text-pk-muted">
                Active {formatDistanceToNow(new Date(app.last_activity), { addSuffix: true })}
              </p>
            )}
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-pk-muted">Users</span>
          <span className="font-medium">{app.user_count}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-pk-muted">API/hr</span>
          <span className="font-medium">
            {(app.api_calls_per_hour / 1000).toFixed(1)}k
          </span>
        </div>
      </div>
      
      <button className="mt-4 text-xs text-pk-info hover:text-pk-text transition-colors">
        View Details →
      </button>
    </div>
  )
}

export function AppGrid() {
  const { data: apps, isLoading } = useQuery<AppStats[]>({
    queryKey: ['appStats'],
    queryFn: fetchAppStats,
  })

  if (isLoading) {
    return (
      <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Active Applications</h3>
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-pk-bg rounded-lg p-6 animate-pulse">
              <div className="h-8 w-32 bg-pk-border rounded mb-4"></div>
              <div className="space-y-2">
                <div className="h-4 w-full bg-pk-border rounded"></div>
                <div className="h-4 w-3/4 bg-pk-border rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Active Applications</h3>
      <div className="grid grid-cols-3 gap-4">
        {apps?.map((app) => (
          <AppCard key={app.name} app={app} />
        ))}
      </div>
    </div>
  )
}