export interface CareerAssessment {
  person_id: string
  current_role: string
  target_role: string
  years_experience: number
  skills: string[]
  goals: string[]
  concerns: string[]
}

export interface CareerPath {
  person_id: string
  current_role: string
  target_role: string
  milestones: Milestone[]
  personalization_notes: string[]
  timeline_months: number
}

export interface Milestone {
  id: string
  title: string
  description: string
  duration_weeks: number
  risk_level: 'low' | 'medium' | 'high'
  tasks: string[]
  success_criteria: string
  completed?: boolean
}

export interface DailyTask {
  id: string
  category: string
  title: string
  description: string
  effort_minutes: number
  comfort_level?: string
  learning_style?: string
  completed?: boolean
}

export interface PersonProfile {
  person_id: string
  name: string
  current_role: string
  target_role: string
  risk_level: number
  learning_style: string
  networking_comfort: string
}