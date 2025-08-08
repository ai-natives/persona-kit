import { useQuery } from '@tanstack/react-query'
import { fetchMetrics } from '../api'
import { MetricSnapshot } from '../types'
import clsx from 'clsx'

function MetricCard({ 
  label, 
  value, 
  unit = '', 
  trend 
}: { 
  label: string
  value: number | string
  unit?: string
  trend?: number
}) {
  return (
    <div className="metric-card">
      <div className="text-pk-muted text-xs uppercase tracking-wider mb-1">{label}</div>
      <div className="text-2xl font-bold">
        {value}{unit}
      </div>
      {trend !== undefined && (
        <div className={clsx(
          'text-sm mt-1',
          trend > 0 ? 'text-pk-success' : trend < 0 ? 'text-pk-error' : 'text-pk-muted'
        )}>
          {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}

export function MetricsStrip() {
  const { data: metrics, isLoading } = useQuery<MetricSnapshot>({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-5 gap-4 mb-8">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="metric-card animate-pulse">
            <div className="h-4 w-20 bg-pk-border rounded mb-2"></div>
            <div className="h-8 w-24 bg-pk-border rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-5 gap-4 mb-8">
      <MetricCard 
        label="Active Users" 
        value={metrics?.active_users || 0}
        trend={12}
      />
      <MetricCard 
        label="API Calls" 
        value={`${((metrics?.api_calls_per_hour || 0) / 1000).toFixed(1)}k`}
        unit="/hr"
        trend={8}
      />
      <MetricCard 
        label="Avg Latency" 
        value={(metrics?.avg_latency_ms || 0).toFixed(0)}
        unit="ms"
        trend={-5}
      />
      <MetricCard 
        label="Trait Updates" 
        value={metrics?.trait_updates_per_hour || 0}
        unit="/hr"
        trend={15}
      />
      <MetricCard 
        label="Error Rate" 
        value={(metrics?.error_rate || 0).toFixed(2)}
        unit="%"
        trend={0}
      />
    </div>
  )
}