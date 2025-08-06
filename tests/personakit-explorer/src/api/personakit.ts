// Mock PersonaKit API for admin tool development
import { 
  mockMindscape, 
  mockObservations, 
  mockPersona, 
  mockMappers,
  mockTraitTimeline,
  mockAgentTemplates,
  mockPersonId 
} from './mockData';

// Simulate network delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export interface Mindscape {
  person_id: string;
  version: number;
  traits: Record<string, {
    value: any;
    confidence: number;
    sample_size: number;
    timestamp?: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface Observation {
  id: string;
  person_id: string;
  type: 'work_session' | 'user_input' | 'calendar_event';
  content: Record<string, any>;
  created_at: string;
}

export interface Persona {
  id: string;
  person_id: string;
  mapper_id: string;
  core: Record<string, any>;
  overlay: Record<string, any>;
  expires_at: string;
  created_at: string;
}

export interface Mapper {
  id: string;
  name: string;
  description: string;
  required_traits: string[];
  optional_traits: string[];
}

export interface TraitTimeline {
  trait_name: string;
  timeline: Array<{
    timestamp: string;
    value: any;
    confidence: number;
    sample_size: number;
  }>;
}

// Mock API client
export const personaKitAPI = {
  async getMindscape(personId: string): Promise<Mindscape> {
    await delay(300);
    if (personId !== mockPersonId) {
      throw new Error('Person not found');
    }
    return mockMindscape;
  },

  async getMindscapeHistory(personId: string, limit = 10): Promise<Mindscape[]> {
    await delay(400);
    // Generate historical versions
    const history = [];
    for (let i = 0; i < Math.min(limit, 5); i++) {
      const version = mockMindscape.version - i;
      history.push({
        ...mockMindscape,
        version,
        traits: {
          ...mockMindscape.traits,
          "work.focus_duration": {
            ...mockMindscape.traits["work.focus_duration"],
            value: 75 - (i * 5), // Simulate improvement over time
            sample_size: 42 - (i * 8)
          }
        },
        updated_at: new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toISOString()
      });
    }
    return history;
  },

  async getObservations(personId: string, limit = 20): Promise<Observation[]> {
    await delay(250);
    return mockObservations.slice(0, limit);
  },

  async getTraitTimeline(personId: string, traitName: string): Promise<TraitTimeline> {
    await delay(200);
    return {
      ...mockTraitTimeline,
      trait_name: traitName
    };
  },

  async generatePersona(personId: string, mapperId: string, context?: Record<string, any>): Promise<Persona> {
    await delay(500);
    return {
      ...mockPersona,
      id: `persona-${Date.now()}`,
      mapper_id: mapperId,
      created_at: new Date().toISOString(),
      overlay: {
        ...mockPersona.overlay,
        current_state: {
          ...mockPersona.overlay.current_state,
          ...context
        }
      }
    };
  },

  async getActivePersonas(personId: string): Promise<Persona[]> {
    await delay(300);
    return [mockPersona];
  },

  async listMappers(): Promise<Mapper[]> {
    await delay(200);
    return mockMappers;
  },

  async getAgentTemplate(framework: string, persona: Persona): Promise<string> {
    await delay(150);
    const templates = mockAgentTemplates as Record<string, string>;
    return templates[framework] || 'Template not found';
  },

  async simulatePersona(request: {
    person_id: string;
    mapper_id: string;
    context: Record<string, any>;
    mindscape_overrides?: Record<string, any>;
  }): Promise<Persona> {
    await delay(600);
    
    // Apply mindscape overrides if provided
    const simulatedMindscape = request.mindscape_overrides 
      ? { ...mockMindscape, traits: { ...mockMindscape.traits, ...request.mindscape_overrides } }
      : mockMindscape;

    // Generate persona based on context
    const timeOfDay = request.context.time_of_day || 'morning';
    const energyLevel = request.context.energy_level || 'medium';
    
    return {
      ...mockPersona,
      id: `persona-sim-${Date.now()}`,
      overlay: {
        current_state: {
          energy: energyLevel,
          time_of_day: timeOfDay,
          ...request.context
        },
        suggestions: [
          {
            type: "contextual",
            title: `${timeOfDay === 'morning' ? 'Morning' : 'Afternoon'} Optimization`,
            description: `Based on ${energyLevel} energy and ${timeOfDay} context`,
            reason: "Simulated suggestion based on context"
          }
        ]
      }
    };
  }
};