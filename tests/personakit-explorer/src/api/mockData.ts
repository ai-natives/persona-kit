// Mock data for PersonaKit Explorer - Coaching Scenario
// Sato-san: Tech-averse assistant PM learning to organize black-box tests

export const mockPersonId = "sato-san-pm-dx-project";

export const mockMindscape = {
  person_id: mockPersonId,
  version: 42,
  traits: {
    "sdlc_knowledge.understanding": {
      value: "beginner",
      confidence: 0.85,
      sample_size: 12
    },
    "sdlc_knowledge.testing_phase": {
      value: "unclear_on_timing",
      confidence: 0.78,
      sample_size: 8
    },
    "project_management.dx_context": {
      value: {
        understands_goals: "partially",
        knows_her_role: "uncertain",
        developer_collaboration: "intimidated"
      },
      confidence: 0.80,
      sample_size: 15
    },
    "learning_style.preference": {
      value: "visual_examples",
      confidence: 0.92,
      sample_size: 18
    },
    "learning_style.pace": {
      value: "step_by_step",
      confidence: 0.88,
      sample_size: 10
    },
    "testing_knowledge.concepts": {
      value: {
        black_box: "beginner",
        test_cases: "learning",
        test_organization: "needs_guidance",
        functional_specs: "overwhelmed"
      },
      confidence: 0.90,
      sample_size: 20
    },
    "communication.patterns": {
      value: {
        asks_questions: "frequently",
        question_types: ["how_to", "clarification", "validation"],
        prefers_verbal: true,
        needs_visual_aids: true
      },
      confidence: 0.85,
      sample_size: 25
    },
    "progress.testing_skills": {
      value: {
        understands_black_box: true,
        can_identify_test_scenarios: "with_help",
        can_write_test_cases: "learning",
        can_organize_tests: false
      },
      confidence: 0.95,
      sample_size: 15
    },
    "challenges.current": {
      value: ["sdlc_timing", "developer_collaboration", "requirements_format", "agile_ceremonies"],
      confidence: 0.93,
      sample_size: 30
    },
    "coaching.effective_approaches": {
      value: {
        visual_examples: "very_effective",
        templates: "helpful",
        pair_work: "preferred",
        written_instructions: "overwhelming"
      },
      confidence: 0.87,
      sample_size: 12
    }
  },
  created_at: "2024-01-01T09:00:00Z",
  updated_at: new Date().toISOString()
};

export const mockObservations = [
  {
    id: "obs-001",
    person_id: mockPersonId,
    type: "work_session" as const,
    content: {
      start: "2024-01-15T09:00:00Z",
      end: "2024-01-15T09:45:00Z",
      duration_minutes: 45,
      activity: "coaching_session",
      topic: "SDLC and Testing in DX Projects",
      questions_asked: 5,
      notes: "Sato-san confused about when to write test cases in sprint cycle. Doesn't understand her role vs developers."
    },
    created_at: "2024-01-15T09:45:00Z"
  },
  {
    id: "obs-002",
    person_id: mockPersonId,
    type: "user_input" as const,
    content: {
      type: "question",
      text: "What's a user story? The developers keep asking me to write acceptance criteria but I don't know what format they want.",
      context: "Sprint planning meeting",
      timestamp: "2024-01-15T10:30:00Z"
    },
    created_at: "2024-01-15T10:30:00Z"
  },
  {
    id: "obs-003",
    person_id: mockPersonId,
    type: "work_session" as const,
    content: {
      start: "2024-01-16T14:00:00Z",
      end: "2024-01-16T14:30:00Z",
      duration_minutes: 30,
      activity: "practice_exercise",
      achievement: "Wrote first user story with acceptance criteria",
      assistance_level: "high",
      notes: "Needed template and examples. Still unsure about technical details vs business requirements."
    },
    created_at: "2024-01-16T14:30:00Z"
  },
  {
    id: "obs-004",
    person_id: mockPersonId,
    type: "user_input" as const,
    content: {
      type: "self_reflection",
      text: "I feel like I'm always one step behind in sprint meetings. By the time I understand what we're building, developers are already coding",
      confidence: "struggling",
      timestamp: "2024-01-17T11:00:00Z"
    },
    created_at: "2024-01-17T11:00:00Z"
  },
  {
    id: "obs-005",
    person_id: mockPersonId,
    type: "work_session" as const,
    content: {
      start: "2024-01-18T09:30:00Z",
      end: "2024-01-18T10:00:00Z",
      duration_minutes: 30,
      activity: "sdlc_mapping",
      topic: "When to write test cases in Agile sprints",
      breakthrough: "Realized she needs to be involved during story refinement, not after coding starts",
      notes: "Major aha moment - timing was her biggest confusion"
    },
    created_at: "2024-01-18T10:00:00Z"
  }
];

export const mockPersona = {
  id: "persona-001",
  person_id: mockPersonId,
  mapper_id: "tech_coaching_assistant",
  core: {
    learner_profile: {
      tech_comfort: "low",
      learning_style: "visual",
      pace_preference: "step_by_step",
      current_skill: "beginner"
    },
    communication_needs: {
      prefers_verbal: true,
      needs_visuals: true,
      question_frequency: "high",
      validation_seeking: true
    }
  },
  overlay: {
    current_context: {
      task: "organizing_test_cases",
      confidence_level: "building",
      recent_success: "created_first_test_case"
    },
    suggestions: [
      {
        type: "teaching_approach",
        title: "Visual SDLC Timeline",
        description: "Create a visual timeline showing when testing activities happen in each sprint phase",
        reason: "Visual learner + needs clarity on timing + SDLC confusion"
      },
      {
        type: "process_improvement", 
        title: "Join Sprint Refinement Sessions",
        description: "Participate in story refinement to understand requirements before development starts",
        reason: "Currently getting requirements too late + needs context earlier in process"
      },
      {
        type: "confidence_building",
        title: "Highlight Recent Progress",
        description: "Reference her successful test case creation and color-coding suggestion",
        reason: "Building confidence + shows ownership emerging"
      }
    ]
  },
  expires_at: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4 hours
  created_at: new Date().toISOString()
};

export const mockMappers = [
  {
    id: "tech_coaching_assistant",
    name: "Tech Coaching Assistant",
    description: "Provides personalized coaching strategies for tech-averse learners",
    required_traits: [
      "tech_comfort.spreadsheets",
      "learning_style.preference",
      "testing_knowledge.concepts"
    ],
    optional_traits: [
      "communication.patterns",
      "progress.testing_skills",
      "coaching.effective_approaches"
    ]
  },
  {
    id: "test_organization_guide",
    name: "Test Organization Guide",
    description: "Helps organize and structure test cases based on learner capabilities",
    required_traits: [
      "testing_knowledge.concepts",
      "tech_comfort.tools",
      "challenges.current"
    ],
    optional_traits: [
      "learning_style.pace",
      "progress.testing_skills"
    ]
  },
  {
    id: "confidence_builder",
    name: "Confidence Builder Coach",
    description: "Focuses on building technical confidence through achievable milestones",
    required_traits: [
      "progress.testing_skills",
      "challenges.current",
      "coaching.effective_approaches"
    ],
    optional_traits: [
      "communication.patterns",
      "tech_comfort.documentation"
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

// Agent framework templates - removed for now as they don't align with use case
export const mockAgentTemplates = {
  langchain: "// Agent integration coming soon",
  autogen: "// Agent integration coming soon", 
  crewai: "// Agent integration coming soon"
};