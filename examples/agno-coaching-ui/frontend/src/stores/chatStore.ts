import { create } from 'zustand';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8100';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  adaptations?: string[];
}

export interface Profile {
  id: string;
  name: string;
  traits: {
    techLevel: string;
    learningStyle: string;
    preference: string;
  };
  description: string;
}

interface MemoryState {
  agno: {
    sessionTurns: number;
    messageCount: number;
    adaptations: string[];
  };
  personakit: {
    currentLearner: any;
    profileLoaded: boolean;
    usingDemoProfiles?: boolean;
  };
}

interface ChatState {
  messages: Message[];
  currentProfile: Profile | null;
  profiles: Profile[];
  isLoading: boolean;
  error: string | null;
  memoryState: MemoryState | null;
  
  // Actions
  sendMessage: (message: string) => Promise<void>;
  loadProfiles: () => Promise<void>;
  selectProfile: (profileId: string) => void;
  resetSession: () => Promise<void>;
  fetchMemoryState: () => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  currentProfile: null,
  profiles: [],
  isLoading: false,
  error: null,
  memoryState: null,

  sendMessage: async (message: string) => {
    set({ isLoading: true, error: null });
    
    const { currentProfile } = get();
    
    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message,
        person_id: currentProfile?.id,
      });

      const newMessage: Message = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        adaptations: response.data.adaptations,
      };

      set((state) => ({
        messages: [...state.messages, newMessage, assistantMessage],
        isLoading: false,
      }));

      // Update memory state
      get().fetchMemoryState();
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to send message',
        isLoading: false,
      });
    }
  },

  loadProfiles: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/profiles`);
      set({ profiles: response.data });
    } catch (error) {
      set({ error: 'Failed to load profiles' });
    }
  },

  selectProfile: (profileId: string) => {
    const profile = get().profiles.find((p) => p.id === profileId);
    if (profile) {
      set({ currentProfile: profile });
    }
  },

  resetSession: async () => {
    try {
      await axios.post(`${API_URL}/api/reset`);
      set({ messages: [], memoryState: null });
    } catch (error) {
      set({ error: 'Failed to reset session' });
    }
  },

  fetchMemoryState: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/memory`);
      set({ memoryState: response.data });
    } catch (error) {
      console.error('Failed to fetch memory state:', error);
    }
  },
}));