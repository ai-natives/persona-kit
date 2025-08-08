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

export interface Narrative {
  id: string;
  person_id: string;
  narrative_type: 'self_observation' | 'curation';
  raw_text: string;
  tags: string[];
  context?: Record<string, any>;
  trait_path?: string;
  curation_action?: string;
  created_at: string;
  updated_at: string;
}

export interface NarrativeSearchResult {
  narrative: Narrative;
  similarity_score: number;
  excerpt?: string;
}

export interface NarrativeInfluence {
  persona_id: string;
  mapper_name: string;
  created_at: string;
  narratives: Array<{
    narrative_id: string;
    excerpt: string;
    relevance_score: number;
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

  async getMindscapeHistory(_personId: string, limit = 10): Promise<Mindscape[]> {
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

  async getObservations(_personId: string, limit = 20): Promise<Observation[]> {
    await delay(250);
    return mockObservations.slice(0, limit);
  },

  async getTraitTimeline(_personId: string, traitName: string): Promise<TraitTimeline> {
    await delay(200);
    return {
      ...mockTraitTimeline,
      trait_name: traitName
    };
  },

  async generatePersona(personId: string, mapperId: string, context?: Record<string, any>): Promise<Persona> {
    await delay(500);
    
    // Get recent narratives to show influence
    const narratives = await this.getNarratives(personId);
    const relevantNarratives = narratives.slice(0, 2).map(n => ({
      id: n.id,
      excerpt: n.raw_text.substring(0, 100) + '...',
      influence: n.narrative_type === 'curation' ? 'direct' : 'contextual'
    }));
    
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
      },
      // Add narrative context
      narrative_context: {
        narratives_used: relevantNarratives,
        influence_summary: "Persona adapted based on Sato-san's expressed anxieties and learning preferences"
      }
    } as any;
  },

  async getActivePersonas(_personId: string): Promise<Persona[]> {
    await delay(300);
    return [mockPersona];
  },

  async listMappers(): Promise<Mapper[]> {
    await delay(200);
    return mockMappers;
  },

  async getAgentTemplate(framework: string, _persona: Persona): Promise<string> {
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
    
    // Apply mindscape overrides if provided (unused for now)

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
  },

  // Narrative endpoints
  async getNarratives(personId: string, type?: 'self_observation' | 'curation'): Promise<Narrative[]> {
    await delay(300);
    // Return mock narratives
    const mockNarratives: Narrative[] = [
      {
        id: 'narr-1',
        person_id: personId,
        narrative_type: 'self_observation',
        raw_text: "I don't understand what 'black-box testing' means or how it's different from just checking if something works. The developers keep using terms I don't know.",
        tags: ['testing', 'terminology', 'confused'],
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'narr-2',
        person_id: personId,
        narrative_type: 'self_observation',
        raw_text: "When developers say 'functional specifications', I'm not sure what level of detail they need. Should I write user stories? Test scenarios? I feel lost in these planning meetings.",
        tags: ['specifications', 'planning', 'sdlc', 'uncertainty'],
        created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'narr-3',
        person_id: personId,
        narrative_type: 'curation',
        raw_text: "I now understand that black-box testing means testing without seeing the code - just inputs and outputs. This makes more sense for my role since I don't need to read code.",
        tags: ['progress', 'testing', 'understanding'],
        trait_path: 'testing_knowledge.concepts.black_box',
        curation_action: 'update',
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'narr-4',
        person_id: personId,
        narrative_type: 'self_observation',
        raw_text: "I wish someone would explain the whole software development lifecycle to me - where does testing fit? When do I need to prepare test cases? I feel like I'm always behind.",
        tags: ['sdlc', 'timing', 'process', 'workflow'],
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ];

    if (type) {
      return mockNarratives.filter(n => n.narrative_type === type);
    }
    return mockNarratives;
  },

  async searchNarratives(personId: string, query: string): Promise<NarrativeSearchResult[]> {
    await delay(400);
    const narratives = await this.getNarratives(personId);
    
    // Simple mock search - in reality this would use semantic search
    const results = narratives
      .filter(n => n.raw_text.toLowerCase().includes(query.toLowerCase()))
      .map(n => ({
        narrative: n,
        similarity_score: Math.random() * 0.5 + 0.5, // Mock scores between 0.5-1.0
        excerpt: n.raw_text.substring(0, 100) + '...'
      }))
      .sort((a, b) => b.similarity_score - a.similarity_score);
    
    return results;
  },

  async createNarrative(personId: string, data: {
    type: 'self_observation' | 'curation';
    text: string;
    tags?: string[];
    traitPath?: string;
  }): Promise<Narrative> {
    await delay(500);
    
    const narrative: Narrative = {
      id: `narr-${Date.now()}`,
      person_id: personId,
      narrative_type: data.type,
      raw_text: data.text,
      tags: data.tags || [],
      ...(data.type === 'curation' && data.traitPath && {
        trait_path: data.traitPath,
        curation_action: 'correct'
      }),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return narrative;
  },

  async getNarrativeInfluences(_personId: string): Promise<NarrativeInfluence[]> {
    await delay(350);
    
    // Mock influence data
    return [
      {
        persona_id: 'persona-1',
        mapper_name: 'Tech Coaching Assistant',
        created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        narratives: [
          {
            narrative_id: 'narr-1',
            excerpt: "I get really anxious when I see spreadsheets with too many columns...",
            relevance_score: 0.95
          },
          {
            narrative_id: 'narr-2',
            excerpt: "I understand things much better when someone shows me an example first...",
            relevance_score: 0.89
          }
        ]
      },
      {
        persona_id: 'persona-2',
        mapper_name: 'Confidence Builder Coach',
        created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
        narratives: [
          {
            narrative_id: 'narr-3',
            excerpt: "I'm actually getting more comfortable with Google Sheets now...",
            relevance_score: 0.92
          }
        ]
      }
    ];
  }
};