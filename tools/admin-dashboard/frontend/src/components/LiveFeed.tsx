import { format } from 'date-fns'
import { ActivityEvent } from '../types'
import clsx from 'clsx'

const eventIcons: Record<string, string> = {
  observation_created: '🟢',
  trait_updated: '🟣',
  persona_generated: '🔵',
  narrative_created: '🟡',
  error: '🔴',
}

const levelColors: Record<string, string> = {
  INFO: 'text-pk-info',
  WARNING: 'text-pk-warning',
  ERROR: 'text-pk-error',
}

interface LiveFeedProps {
  events: ActivityEvent[]
  autoScroll?: boolean
}

export function LiveFeed({ events, autoScroll = true }: LiveFeedProps) {
  return (
    <div className="bg-pk-surface border border-pk-border rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-pk-border flex justify-between items-center">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          Live Feed
          <span className="text-xs text-pk-muted">{events.length} events</span>
        </h3>
        <div className="flex items-center gap-2 text-sm text-pk-muted">
          <span>Auto-scroll</span>
          <input type="checkbox" checked={autoScroll} readOnly className="ml-1" />
        </div>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="p-8 text-center text-pk-muted">
            Waiting for activity...
          </div>
        ) : (
          <div className="divide-y divide-pk-border">
            {events.map((event, index) => (
              <div key={index} className="p-4 hover:bg-pk-bg/50 transition-colors">
                <div className="flex gap-4">
                  <div className="text-xs text-pk-muted whitespace-nowrap pt-0.5">
                    {format(new Date(event.timestamp), 'HH:mm:ss.SSS')}
                  </div>
                  <div className={clsx('text-xs font-bold w-12', levelColors[event.level])}>
                    {event.level}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start gap-2">
                      <span className="text-lg leading-none">
                        {eventIcons[event.event_type] || '⚪'}
                      </span>
                      <div className="flex-1">
                        <div className="text-sm">{event.message}</div>
                        {event.person_id && (
                          <div className="text-xs text-pk-muted mt-1">
                            person_id: {event.person_id}
                          </div>
                        )}
                        {event.details && Object.keys(event.details).length > 0 && (
                          <div className="text-xs text-pk-muted mt-1 font-mono">
                            {Object.entries(event.details)
                              .filter(([key]) => key !== 'id' && key !== 'person_id')
                              .map(([key, value]) => (
                                <div key={key}>
                                  {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                                </div>
                              ))
                            }
                          </div>
                        )}
                        {event.app_name && (
                          <div className="text-xs text-pk-info mt-1">
                            app: {event.app_name}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}