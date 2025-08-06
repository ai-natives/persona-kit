// Mock data for admin tool development
// This allows us to work independently without conflicting with the main implementation

export const mockPersonId = "550e8400-e29b-41d4-a716-446655440001";

export const mockMindscape = {
  person_id: mockPersonId,
  version: 42,
  traits: {
    "work.focus_duration": {
      value: 75,
      confidence: 0.85,
      sample_size: 42
    },
    "work.energy_patterns": {
      value: {
        high_energy_slots: ["09:00-11:00", "15:00-17:00"],
        low_energy_slots: ["13:00-14:00"],
      },
      confidence: 0.72,
      sample_size: 28
    },
    "productivity.peak_hours": {
      value: {
        primary: { start: "09:00", end: "11:00", confidence: 0.9 },
        secondary: { start: "15:00", end: "17:00", confidence: 0.7 }
      },
      confidence: 0.88,
      sample_size: 35
    },
    "work.task_switching_cost": {
      value: "medium",
      confidence: 0.65,
      sample_size: 18
    },
    "preferences.work_environment": {
      value: {
        music: true,
        quiet_needed: false,
        collaborative: true
      },
      confidence: 0.80,
      sample_size: 25
    },
    "current_state.energy_level": {
      value: "high",
      confidence: 1.0,
      sample_size: 1,
      timestamp: new Date().toISOString()
    }
  },
  created_at: "2024-01-01T09:00:00Z",
  updated_at: new Date().toISOString()
};

export const mockObservations = [
  {
    id: "obs-001",
    person_id: mockPersonId,
    type: "work_session",
    content: {
      start: "2024-01-15T09:00:00Z",
      end: "2024-01-15T11:00:00Z",
      duration_minutes: 120,
      productivity_score: 5,
      interruptions: 0,
      activity: "coding"
    },
    created_at: "2024-01-15T11:00:00Z"
  },
  {
    id: "obs-002",
    person_id: mockPersonId,
    type: "user_input",
    content: {
      type: "energy_check",
      energy_level: "high",
      timestamp: "2024-01-15T09:00:00Z"
    },
    created_at: "2024-01-15T09:00:00Z"
  },
  {
    id: "obs-003",
    person_id: mockPersonId,
    type: "calendar_event",
    content: {
      id: "evt_001",
      type: "meeting",
      title: "Team Standup",
      start: "2024-01-15T10:00:00Z",
      end: "2024-01-15T10:30:00Z",
      duration_minutes: 30,
      attendees: 5
    },
    created_at: "2024-01-15T10:30:00Z"
  }
];

export const mockPersona = {
  id: "persona-001",
  person_id: mockPersonId,
  mapper_id: "daily_work_optimizer",
  core: {
    work_style: {
      focus_blocks: {
        optimal_duration: 75,
        confidence: 0.85
      },
      task_switching: {
        tolerance: "medium",
        recovery_time: 15
      }
    },
    energy_profile: {
      peak_times: ["09:00-11:00", "15:00-17:00"],
      low_times: ["13:00-14:00"]
    }
  },
  overlay: {
    current_state: {
      energy: "high",
      time_of_day: "morning",
      day_type: "weekday"
    },
    suggestions: [
      {
        type: "deep_work",
        title: "Deep Work Window",
        description: "Block the next 90 minutes for your most challenging work",
        reason: "High energy + peak productivity time"
      },
      {
        type: "task_order",
        title: "Start with Complex Tasks",
        description: "Tackle analytical or creative work first",
        reason: "Morning hours show highest focus scores"
      }
    ]
  },
  expires_at: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4 hours
  created_at: new Date().toISOString()
};

export const mockMappers = [
  {
    id: "daily_work_optimizer",
    name: "Daily Work Optimizer",
    description: "Optimizes daily work patterns based on energy and productivity",
    required_traits: [
      "work.focus_duration",
      "work.energy_patterns",
      "productivity.peak_hours"
    ],
    optional_traits: [
      "work.task_switching_cost",
      "preferences.work_environment"
    ]
  },
  {
    id: "meeting_scheduler",
    name: "Meeting Scheduler",
    description: "Suggests optimal meeting times based on energy and recovery needs",
    required_traits: [
      "work.energy_patterns",
      "work.meeting_recovery_time"
    ],
    optional_traits: [
      "preferences.meeting_format"
    ]
  }
];

export const mockTraitTimeline = {
  trait_name: "work.focus_duration",
  timeline: [
    { timestamp: "2024-01-01T09:00:00Z", value: 60, confidence: 0.7, sample_size: 10 },
    { timestamp: "2024-01-05T09:00:00Z", value: 65, confidence: 0.75, sample_size: 20 },
    { timestamp: "2024-01-10T09:00:00Z", value: 70, confidence: 0.8, sample_size: 30 },
    { timestamp: "2024-01-15T09:00:00Z", value: 75, confidence: 0.85, sample_size: 42 }
  ]
};

// Agent framework templates
export const mockAgentTemplates = {
  langchain: `from langchain import SystemMessage

persona = ${JSON.stringify(mockPersona.core, null, 2)}

system_message = SystemMessage(
    content=f"""You are a work optimization assistant with the following understanding of the user's work patterns:
    
    Focus Duration: {persona['work_style']['focus_blocks']['optimal_duration']} minutes
    Peak Productivity: {', '.join(persona['energy_profile']['peak_times'])}
    Task Switching Tolerance: {persona['work_style']['task_switching']['tolerance']}
    
    Use this information to provide personalized productivity advice."""
)`,
  
  autogen: `user_profile = {
    "name": "Work Optimizer",
    "work_patterns": ${JSON.stringify(mockPersona.core, null, 2)},
    "system_message": "You help optimize work patterns based on personal productivity data."
}`,

  crewai: `from crewai import Agent

productivity_agent = Agent(
    role='Personal Productivity Coach',
    goal='Optimize work patterns based on individual traits',
    backstory="""You understand that this person works best in ${mockPersona.core.work_style.focus_blocks.optimal_duration}-minute focus blocks
    and has peak productivity during ${mockPersona.core.energy_profile.peak_times.join(' and ')}.
    They have ${mockPersona.core.work_style.task_switching.tolerance} tolerance for task switching.""",
    allow_delegation=False
)`
};