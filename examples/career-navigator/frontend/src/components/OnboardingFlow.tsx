import { useState } from 'react'
import * as Slider from '@radix-ui/react-slider'
import * as RadioGroup from '@radix-ui/react-radio-group'
import { CareerAssessment } from '../types'

interface OnboardingFlowProps {
  onComplete: (assessment: CareerAssessment) => void
}

export function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState(1)
  const [assessment, setAssessment] = useState<Partial<CareerAssessment>>({
    person_id: `person-${Date.now()}`, // Generate unique ID
    current_role: '',
    target_role: '',
    years_experience: 5,
    skills: [],
    goals: [],
    concerns: []
  })

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1)
    } else {
      // Submit assessment
      onComplete(assessment as CareerAssessment)
    }
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return assessment.current_role && assessment.target_role
      case 2:
        return assessment.skills && assessment.skills.length > 0
      case 3:
        return assessment.goals && assessment.goals.length > 0
      case 4:
        return true
      default:
        return false
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`w-1/4 h-2 ${
                  s <= step ? 'bg-nav-blue-500' : 'bg-gray-200'
                } ${s < 4 ? 'mr-2' : ''}`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-600 text-center">Step {step} of 4</p>
        </div>

        {/* Step content */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Career Transition Goals</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Current Role</label>
                <input
                  type="text"
                  value={assessment.current_role}
                  onChange={(e) => setAssessment({ ...assessment, current_role: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-nav-blue-500 focus:border-transparent"
                  placeholder="e.g., Senior Developer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Target Role</label>
                <input
                  type="text"
                  value={assessment.target_role}
                  onChange={(e) => setAssessment({ ...assessment, target_role: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-nav-blue-500 focus:border-transparent"
                  placeholder="e.g., Tech Lead"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Years of Experience: {assessment.years_experience}
                </label>
                <Slider.Root
                  value={[assessment.years_experience || 5]}
                  onValueChange={(value) => setAssessment({ ...assessment, years_experience: value[0] })}
                  max={20}
                  step={1}
                  className="relative flex items-center select-none touch-none w-full h-5"
                >
                  <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
                    <Slider.Range className="absolute bg-nav-blue-500 rounded-full h-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-5 h-5 bg-white border-2 border-nav-blue-500 rounded-full hover:shadow-lg focus:outline-none focus:shadow-lg" />
                </Slider.Root>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Your Skills</h2>
            <p className="text-gray-600 mb-4">Select your current skills (choose all that apply)</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                'Project Management', 'Team Leadership', 'Technical Architecture',
                'Code Review', 'Mentoring', 'Public Speaking', 'Stakeholder Management',
                'Agile/Scrum', 'System Design', 'Documentation'
              ].map((skill) => (
                <label key={skill} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={assessment.skills?.includes(skill)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAssessment({ ...assessment, skills: [...(assessment.skills || []), skill] })
                      } else {
                        setAssessment({ ...assessment, skills: assessment.skills?.filter(s => s !== skill) })
                      }
                    }}
                    className="rounded text-nav-blue-500"
                  />
                  <span>{skill}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Goals & Aspirations</h2>
            <p className="text-gray-600 mb-4">What do you hope to achieve?</p>
            <div className="space-y-3">
              {[
                'Lead larger teams',
                'Make architectural decisions',
                'Increase compensation',
                'Work on more impactful projects',
                'Improve work-life balance',
                'Learn new technologies'
              ].map((goal) => (
                <label key={goal} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={assessment.goals?.includes(goal)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAssessment({ ...assessment, goals: [...(assessment.goals || []), goal] })
                      } else {
                        setAssessment({ ...assessment, goals: assessment.goals?.filter(g => g !== goal) })
                      }
                    }}
                    className="rounded text-nav-blue-500"
                  />
                  <span>{goal}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Concerns & Challenges</h2>
            <p className="text-gray-600 mb-4">What worries you about this transition?</p>
            <div className="space-y-3">
              {[
                'Lack of leadership experience',
                'Imposter syndrome',
                'Work-life balance',
                'Technical skills gaps',
                'Networking challenges',
                'Fear of failure'
              ].map((concern) => (
                <label key={concern} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={assessment.concerns?.includes(concern)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAssessment({ ...assessment, concerns: [...(assessment.concerns || []), concern] })
                      } else {
                        setAssessment({ ...assessment, concerns: assessment.concerns?.filter(c => c !== concern) })
                      }
                    }}
                    className="rounded text-nav-blue-500"
                  />
                  <span>{concern}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex justify-between">
          <button
            onClick={() => setStep(step - 1)}
            disabled={step === 1}
            className="px-6 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="px-6 py-2 bg-nav-blue-500 text-white rounded-lg hover:bg-nav-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {step === 4 ? 'Create My Path' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  )
}