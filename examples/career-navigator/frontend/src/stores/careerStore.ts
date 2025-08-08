import { create } from 'zustand'
import { CareerAssessment, CareerPath, DailyTask, PersonProfile } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8103'

interface CareerStore {
  // State
  personProfile: PersonProfile | null
  careerPath: CareerPath | null
  dailyTasks: DailyTask[]
  isLoading: boolean
  error: string | null

  // Actions
  setPersonProfile: (profile: PersonProfile) => void
  submitAssessment: (assessment: CareerAssessment) => Promise<void>
  fetchDailyTasks: (personId: string) => Promise<void>
  completeMilestone: (personId: string, milestoneId: string) => Promise<void>
  completeTask: (taskId: string) => void
  submitFeedback: (personId: string, itemType: string, itemId: string, helpful: boolean) => Promise<void>
}

export const useCareerStore = create<CareerStore>((set, get) => ({
  // Initial state
  personProfile: null,
  careerPath: null,
  dailyTasks: [],
  isLoading: false,
  error: null,

  // Actions
  setPersonProfile: (profile) => set({ personProfile: profile }),

  submitAssessment: async (assessment) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`${API_URL}/api/career/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessment)
      })
      
      if (!response.ok) throw new Error('Failed to submit assessment')
      
      const careerPath = await response.json()
      set({ careerPath, isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  fetchDailyTasks: async (personId) => {
    try {
      const response = await fetch(`${API_URL}/api/career/tasks/${personId}`)
      if (!response.ok) throw new Error('Failed to fetch tasks')
      
      const data = await response.json()
      set({ dailyTasks: data.tasks })
    } catch (error) {
      set({ error: error.message })
    }
  },

  completeMilestone: async (personId, milestoneId) => {
    try {
      const response = await fetch(`${API_URL}/api/career/milestone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ person_id: personId, milestone_id: milestoneId })
      })
      
      if (!response.ok) throw new Error('Failed to complete milestone')
      
      // Update local state
      const { careerPath } = get()
      if (careerPath) {
        const updatedMilestones = careerPath.milestones.map(m =>
          m.id === milestoneId ? { ...m, completed: true } : m
        )
        set({ careerPath: { ...careerPath, milestones: updatedMilestones } })
      }
    } catch (error) {
      set({ error: error.message })
    }
  },

  completeTask: (taskId) => {
    const { dailyTasks } = get()
    const updatedTasks = dailyTasks.map(t =>
      t.id === taskId ? { ...t, completed: true } : t
    )
    set({ dailyTasks: updatedTasks })
  },

  submitFeedback: async (personId, itemType, itemId, helpful) => {
    try {
      const response = await fetch(`${API_URL}/api/career/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ person_id: personId, item_type: itemType, item_id: itemId, helpful })
      })
      
      if (!response.ok) throw new Error('Failed to submit feedback')
    } catch (error) {
      console.error('Feedback error:', error)
    }
  }
}))