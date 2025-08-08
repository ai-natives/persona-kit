import { DailyTask } from '../types'
import clsx from 'clsx'

interface TaskPanelProps {
  tasks: DailyTask[]
  adaptationReasons: string[]
  onCompleteTask: (taskId: string) => void
}

const categoryIcons: Record<string, string> = {
  networking: '🤝',
  learning: '📚',
  project: '🛠️',
  skill: '💡',
  reflection: '📝'
}

export function TaskPanel({ tasks, adaptationReasons, onCompleteTask }: TaskPanelProps) {
  const completedCount = tasks.filter(t => t.completed).length

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-xl font-semibold mb-2">Today's Tasks</h3>
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Personalized for your style and comfort level
          </p>
          <div className="text-sm">
            <span className="font-medium">{completedCount}</span>
            <span className="text-gray-500"> / {tasks.length} completed</span>
          </div>
        </div>
      </div>

      {adaptationReasons.length > 0 && (
        <div className="mb-4 p-3 bg-nav-green-50 rounded-lg border border-nav-green-200">
          <p className="text-sm font-medium text-nav-green-900 mb-1">
            Adapted for you:
          </p>
          <ul className="space-y-1">
            {adaptationReasons.map((reason, i) => (
              <li key={i} className="text-xs text-nav-green-800 flex items-start gap-2">
                <span>✓</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onComplete={() => onCompleteTask(task.id)}
          />
        ))}
      </div>

      {tasks.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No tasks available yet.</p>
          <p className="text-sm mt-2">Complete your assessment to get personalized daily tasks.</p>
        </div>
      )}
    </div>
  )
}

function TaskCard({ task, onComplete }: { task: DailyTask; onComplete: () => void }) {
  return (
    <div className={clsx(
      'border rounded-lg p-4 transition-all',
      task.completed ? 'bg-gray-50 opacity-75' : 'hover:shadow-sm'
    )}>
      <div className="flex items-start gap-3">
        <div className="text-2xl mt-1">
          {categoryIcons[task.category] || '📌'}
        </div>
        <div className="flex-1">
          <h4 className={clsx(
            'font-medium mb-1',
            task.completed && 'line-through text-gray-500'
          )}>
            {task.title}
          </h4>
          <p className="text-sm text-gray-600 mb-2">{task.description}</p>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>⏱️ {task.effort_minutes} min</span>
            {task.comfort_level && (
              <span className="capitalize">Comfort: {task.comfort_level}</span>
            )}
            {task.learning_style && (
              <span className="capitalize">Style: {task.learning_style}</span>
            )}
          </div>
        </div>
        {!task.completed && (
          <button
            onClick={onComplete}
            className="px-3 py-1 bg-nav-green-500 text-white rounded text-sm hover:bg-nav-green-600 transition-colors"
          >
            Done
          </button>
        )}
      </div>
    </div>
  )
}