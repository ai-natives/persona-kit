import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MetricsStrip } from './components/MetricsStrip'
import { LiveFeed } from './components/LiveFeed'
// import { AppGrid } from './components/AppGrid'  // Disabled - only shows hardcoded data
import { useWebSocket } from './hooks/useWebSocket'
import { fetchActivityFeed } from './api'
import { ActivityEvent } from './types'

type View = 'overview' | 'logs' | 'metrics' | 'traces' | 'alerts'

function App() {
  const [currentView, setCurrentView] = useState<View>('overview')
  const { events: wsEvents, isConnected } = useWebSocket()
  
  // Also fetch initial events
  const { data: initialEvents = [] } = useQuery<ActivityEvent[]>({
    queryKey: ['activityFeed'],
    queryFn: () => fetchActivityFeed(50),
    refetchInterval: false, // Don't refetch, we have WebSocket
  })
  
  // Combine WebSocket events with initial events
  const allEvents = [...wsEvents, ...initialEvents].slice(0, 100)

  return (
    <div className="min-h-screen bg-pk-bg text-pk-text">
      {/* Top Navigation */}
      <nav className="bg-pk-surface border-b border-pk-border">
        <div className="px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold">PersonaKit Admin</h1>
            <div className="flex gap-1">
              {(['overview', 'logs', 'metrics', 'traces', 'alerts'] as View[]).map((view) => (
                <button
                  key={view}
                  onClick={() => setCurrentView(view)}
                  className={`px-4 py-2 text-sm capitalize rounded transition-colors ${
                    currentView === view
                      ? 'bg-pk-bg text-pk-text'
                      : 'text-pk-muted hover:text-pk-text'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-pk-success' : 'bg-pk-error'}`} />
              <span className="text-sm text-pk-muted">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button className="p-2 hover:bg-pk-bg rounded">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            <button className="p-2 hover:bg-pk-bg rounded">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {currentView === 'overview' && (
          <>
            {/* Metrics Strip */}
            <MetricsStrip />

            {/* Main Grid */}
            <div className="grid grid-cols-1 gap-6">
              {/* Live Feed - Full width since AppGrid is disabled */}
              <LiveFeed events={allEvents} />

              {/* App Grid - Disabled for now since it only shows hardcoded data */}
              {/* <AppGrid /> */}
            </div>
          </>
        )}

        {currentView === 'logs' && (
          <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Logs View</h2>
            <p className="text-pk-muted">Detailed logging interface coming soon...</p>
          </div>
        )}

        {currentView === 'metrics' && (
          <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Metrics View</h2>
            <p className="text-pk-muted">Time-series graphs and analytics coming soon...</p>
          </div>
        )}

        {currentView === 'traces' && (
          <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Traces View</h2>
            <p className="text-pk-muted">APM-style trace analysis coming soon...</p>
          </div>
        )}

        {currentView === 'alerts' && (
          <div className="bg-pk-surface border border-pk-border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Alerts Configuration</h2>
            <p className="text-pk-muted">Alert management coming soon...</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App