import { CareerPath, Milestone } from '../types'
import clsx from 'clsx'

interface JourneyMapProps {
  careerPath: CareerPath
  onCompleteMilestone: (milestoneId: string) => void
}

const riskColors = {
  low: 'bg-green-100 text-green-800 border-green-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  high: 'bg-red-100 text-red-800 border-red-300'
}

export function JourneyMap({ careerPath, onCompleteMilestone }: JourneyMapProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Your Career Journey</h2>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>From: <strong>{careerPath.current_role}</strong></span>
          <span>→</span>
          <span>To: <strong>{careerPath.target_role}</strong></span>
          <span className="ml-auto">Timeline: {careerPath.timeline_months} months</span>
        </div>
      </div>

      <div className="space-y-4">
        {careerPath.milestones.map((milestone, index) => (
          <MilestoneCard
            key={milestone.id}
            milestone={milestone}
            index={index}
            onComplete={() => onCompleteMilestone(milestone.id)}
          />
        ))}
      </div>

      {careerPath.personalization_notes.length > 0 && (
        <div className="mt-6 p-4 bg-nav-blue-50 rounded-lg">
          <h3 className="font-semibold text-nav-blue-900 mb-2">
            Why this path works for you:
          </h3>
          <ul className="space-y-1">
            {careerPath.personalization_notes.map((note, i) => (
              <li key={i} className="text-sm text-nav-blue-800 flex items-start gap-2">
                <span>•</span>
                <span>{note}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function MilestoneCard({ 
  milestone, 
  index, 
  onComplete 
}: { 
  milestone: Milestone
  index: number
  onComplete: () => void 
}) {
  return (
    <div className={clsx(
      'border rounded-lg p-4 transition-all',
      milestone.completed ? 'bg-gray-50 opacity-75' : 'hover:shadow-md'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className={clsx(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            milestone.completed ? 'bg-green-500 text-white' : 'bg-gray-200'
          )}>
            {milestone.completed ? '✓' : index + 1}
          </div>
          <div>
            <h3 className="font-semibold text-lg">{milestone.title}</h3>
            <p className="text-gray-600 text-sm mt-1">{milestone.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={clsx(
            'px-2 py-1 rounded text-xs font-medium',
            riskColors[milestone.risk_level]
          )}>
            {milestone.risk_level} risk
          </span>
          <span className="text-sm text-gray-500">
            {milestone.duration_weeks} weeks
          </span>
        </div>
      </div>

      <div className="ml-11">
        <div className="mb-3">
          <h4 className="text-sm font-medium text-gray-700 mb-1">Tasks:</h4>
          <ul className="space-y-1">
            {milestone.tasks.map((task, i) => (
              <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                <span className="text-nav-blue-500">→</span>
                <span>{task}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mb-3">
          <h4 className="text-sm font-medium text-gray-700 mb-1">Success Criteria:</h4>
          <p className="text-sm text-gray-600">{milestone.success_criteria}</p>
        </div>

        {!milestone.completed && (
          <button
            onClick={onComplete}
            className="mt-2 px-4 py-2 bg-nav-blue-500 text-white rounded hover:bg-nav-blue-600 transition-colors text-sm"
          >
            Mark Complete
          </button>
        )}
      </div>
    </div>
  )
}