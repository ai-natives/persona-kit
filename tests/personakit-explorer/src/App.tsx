import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import * as Tabs from '@radix-ui/react-tabs';
import { Brain, BarChart3, BookOpen } from 'lucide-react';
import { MindscapeExplorer } from './components/MindscapeExplorer';
import { NarrativesExplorer } from './components/NarrativesExplorer';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Mock person for development - Sato-san coaching scenario
const MOCK_PERSON_ID = "sato-san-pm-dx-project";

function App() {
  const [activeTab, setActiveTab] = useState('mindscape');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1>PersonaKit Explorer - Tech Coaching Assistant</h1>
            <div className="header-info">
              <span>Learner: Sato-san (Assistant PM, DX Project)</span>
              <span>Context: Learning to organize black-box tests</span>
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
              <Tabs.Trigger value="narratives" className="main-tab">
                <BookOpen size={18} />
                <span>Narratives</span>
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
              <Tabs.Content value="narratives">
                <NarrativesExplorer personId={MOCK_PERSON_ID} />
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
