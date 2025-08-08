import { useEffect, useState } from 'react'
import { useCareerStore } from './stores/careerStore'
import { ProfileCard } from './components/ProfileCard'
import { JourneyMap } from './components/JourneyMap'
import { TaskPanel } from './components/TaskPanel'
import { OnboardingFlow } from './components/OnboardingFlow'
import { PersonProfile } from './types'

function App() {
  const [showOnboarding, setShowOnboarding] = useState(true) // Start with onboarding
  const [adaptationReasons, setAdaptationReasons] = useState<string[]>([])
  
  const {
    personProfile,
    careerPath,
    dailyTasks,
    isLoading,
    error,
    setPersonProfile,
    submitAssessment,
    fetchDailyTasks,
    completeMilestone,
    completeTask,
    submitFeedback
  } = useCareerStore()

  // Fetch daily tasks when profile changes
  useEffect(() => {
    if (personProfile?.person_id) {
      fetchDailyTasks(personProfile.person_id).then(() => {
        // Set adaptation reasons based on profile
        const reasons = []
        if (personProfile.networking_comfort === 'low') {
          reasons.push('1-on-1 networking tasks instead of group events')
        }
        if (personProfile.learning_style === 'visual') {
          reasons.push('Visual learning resources prioritized')
        }
        if (personProfile.risk_level <= 2) {
          reasons.push('Conservative, low-risk suggestions')
        }
        setAdaptationReasons(reasons)
      })
    }
  }, [personProfile, fetchDailyTasks])


  const handleAssessmentComplete = async (assessment: any) => {
    // Generate a unique person_id for this user
    const personId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const fullAssessment = {
      ...assessment,
      person_id: personId
    }
    
    // Create a profile from the assessment
    const profile: PersonProfile = {
      person_id: personId,
      name: 'Career Navigator User',
      current_role: assessment.current_role,
      target_role: assessment.target_role,
      risk_level: 3, // Will be set by PersonaKit
      learning_style: 'balanced',
      networking_comfort: 'medium'
    }
    
    setPersonProfile(profile)
    await submitAssessment(fullAssessment)
    setShowOnboarding(false)
  }

  const handleMilestoneComplete = async (milestoneId: string) => {
    if (personProfile) {
      await completeMilestone(personProfile.person_id, milestoneId)
      await submitFeedback(personProfile.person_id, 'milestone', milestoneId, true)
    }
  }

  const handleTaskComplete = async (taskId: string) => {
    completeTask(taskId)
    if (personProfile) {
      await submitFeedback(personProfile.person_id, 'task', taskId, true)
    }
  }

  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleAssessmentComplete} />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">Career Navigator</h1>
              <span className="text-sm text-gray-500">Powered by PersonaKit</span>
            </div>
            <div className="flex items-center gap-4">
              {personProfile && (
                <span className="text-sm text-gray-600">
                  Person ID: {personProfile.person_id.slice(0, 8)}...
                </span>
              )}
              <button
                onClick={() => {
                  setShowOnboarding(true)
                  useCareerStore.setState({ careerPath: null, personProfile: null })
                }}
                className="px-3 py-1 border rounded-md text-sm hover:bg-gray-50"
              >
                New Assessment
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left sidebar - Profile */}
          <div className="lg:col-span-1">
            {personProfile && <ProfileCard profile={personProfile} />}
            
            {!careerPath && (
              <button
                onClick={() => setShowOnboarding(true)}
                className="mt-4 w-full px-4 py-2 bg-nav-blue-500 text-white rounded-lg hover:bg-nav-blue-600 transition-colors"
              >
                Start Career Assessment
              </button>
            )}
          </div>

          {/* Center - Journey Map */}
          <div className="lg:col-span-2">
            {isLoading ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-nav-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Creating your personalized career path...</p>
              </div>
            ) : careerPath ? (
              <JourneyMap 
                careerPath={careerPath} 
                onCompleteMilestone={handleMilestoneComplete}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <h2 className="text-xl font-semibold mb-4">Welcome to Career Navigator!</h2>
                <p className="text-gray-600 mb-6">
                  Complete the assessment to get your personalized career transition plan.
                </p>
                <button
                  onClick={() => setShowOnboarding(true)}
                  className="px-6 py-3 bg-nav-blue-500 text-white rounded-lg hover:bg-nav-blue-600 transition-colors"
                >
                  Start Assessment
                </button>
              </div>
            )}
          </div>

          {/* Right sidebar - Daily Tasks */}
          <div className="lg:col-span-1">
            <TaskPanel 
              tasks={dailyTasks}
              adaptationReasons={adaptationReasons}
              onCompleteTask={handleTaskComplete}
            />
          </div>
        </div>

        {/* Info banner */}
        <div className="mt-8 p-4 bg-nav-blue-50 rounded-lg border border-nav-blue-200">
          <p className="text-sm text-nav-blue-900">
            <strong>PersonaKit Integration:</strong> This app creates a real PersonaKit persona based on your assessment. 
            Every action you take updates your profile, making future recommendations more personalized.
          </p>
        </div>
      </main>
    </div>
  )
}

export default App