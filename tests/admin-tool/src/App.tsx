import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import * as Tabs from '@radix-ui/react-tabs';
import { Brain, FlaskConical, Bot, BarChart3 } from 'lucide-react';
import { MindscapeExplorer } from './components/MindscapeExplorer';
import { PersonaLab } from './components/PersonaLab';
import { AgentPlayground } from './components/AgentPlayground';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Mock person for development
const MOCK_PERSON_ID = "550e8400-e29b-41d4-a716-446655440001";

function App() {
  const [activeTab, setActiveTab] = useState('mindscape');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1>PersonaKit Admin Tool</h1>
            <div className="header-info">
              <span>Person ID: {MOCK_PERSON_ID.slice(0, 8)}...</span>
              <span>Environment: Development (Mock Data)</span>
            </div>
          </div>
        </header>

        <main className="app-main">
          <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
            <Tabs.List className="main-tabs">
              <Tabs.Trigger value="mindscape" className="main-tab">
                <Brain size={18} />
                <span>Mindscapes</span>
              </Tabs.Trigger>
              <Tabs.Trigger value="personas" className="main-tab">
                <FlaskConical size={18} />
                <span>Persona Lab</span>
              </Tabs.Trigger>
              <Tabs.Trigger value="agents" className="main-tab">
                <Bot size={18} />
                <span>Agent Integration</span>
              </Tabs.Trigger>
              <Tabs.Trigger value="analytics" className="main-tab" disabled>
                <BarChart3 size={18} />
                <span>Analytics</span>
                <span className="coming-soon">Coming Soon</span>
              </Tabs.Trigger>
            </Tabs.List>

            <div className="tab-content">
              <Tabs.Content value="mindscape">
                <MindscapeExplorer personId={MOCK_PERSON_ID} />
              </Tabs.Content>
              <Tabs.Content value="personas">
                <PersonaLab personId={MOCK_PERSON_ID} />
              </Tabs.Content>
              <Tabs.Content value="agents">
                <AgentPlayground personId={MOCK_PERSON_ID} />
              </Tabs.Content>
              <Tabs.Content value="analytics">
                <div className="placeholder">
                  <h2>Analytics Dashboard</h2>
                  <p>Coming soon: Trait coverage, mapper usage, and feedback analysis</p>
                </div>
              </Tabs.Content>
            </div>
          </Tabs.Root>
        </main>
      </div>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App
