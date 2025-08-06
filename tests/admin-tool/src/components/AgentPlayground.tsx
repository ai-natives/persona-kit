import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import * as Tabs from '@radix-ui/react-tabs';
import { Copy, Download, Check } from 'lucide-react';
import { personaKitAPI } from '../api/personakit';

interface FrameworkTab {
  id: string;
  name: string;
  icon: string;
}

const frameworks: FrameworkTab[] = [
  { id: 'langchain', name: 'LangChain', icon: '🦜' },
  { id: 'autogen', name: 'AutoGen', icon: '🤖' },
  { id: 'crewai', name: 'CrewAI', icon: '👥' },
  { id: 'raw', name: 'Raw Prompt', icon: '📝' },
];

export const AgentPlayground: React.FC<{ personId: string }> = ({ personId }) => {
  const [selectedFramework, setSelectedFramework] = useState('langchain');
  const [copied, setCopied] = useState(false);

  const { data: personas } = useQuery({
    queryKey: ['active-personas', personId],
    queryFn: () => personaKitAPI.getActivePersonas(personId)
  });

  const selectedPersona = personas?.[0]; // Use first active persona

  const { data: template } = useQuery({
    queryKey: ['agent-template', selectedFramework, selectedPersona?.id],
    queryFn: () => selectedPersona 
      ? personaKitAPI.getAgentTemplate(selectedFramework, selectedPersona)
      : Promise.resolve(''),
    enabled: !!selectedPersona
  });

  const handleCopy = () => {
    if (template) {
      navigator.clipboard.writeText(template);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (template) {
      const blob = new Blob([template], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `persona-${selectedFramework}-${Date.now()}.py`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const getRawPrompt = () => {
    if (!selectedPersona) return '';
    
    return `You are a work optimization assistant with deep understanding of the user's work patterns:

## Work Style
- Optimal focus duration: ${selectedPersona.core.work_style?.focus_blocks?.optimal_duration || 'Unknown'} minutes
- Task switching tolerance: ${selectedPersona.core.work_style?.task_switching?.tolerance || 'Unknown'}
- Recovery time after interruptions: ${selectedPersona.core.work_style?.task_switching?.recovery_time || 'Unknown'} minutes

## Energy Profile
- Peak productivity times: ${selectedPersona.core.energy_profile?.peak_times?.join(', ') || 'Unknown'}
- Low energy periods: ${selectedPersona.core.energy_profile?.low_times?.join(', ') || 'Unknown'}

## Current Context
- Energy level: ${selectedPersona.overlay.current_state?.energy || 'Unknown'}
- Time of day: ${selectedPersona.overlay.current_state?.time_of_day || 'Unknown'}

Use this information to provide personalized, actionable productivity advice that fits the user's natural patterns.`;
  };

  if (!selectedPersona) {
    return (
      <div className="agent-playground empty">
        <p>No active personas found. Generate a persona first in the Persona Lab.</p>
      </div>
    );
  }

  return (
    <div className="agent-playground">
      <div className="playground-header">
        <h2>Agent Integration Playground</h2>
        <p>Transform personas into agent configurations</p>
      </div>

      <Tabs.Root value={selectedFramework} onValueChange={setSelectedFramework}>
        <Tabs.List className="framework-tabs">
          {frameworks.map(fw => (
            <Tabs.Trigger key={fw.id} value={fw.id} className="framework-tab">
              <span className="fw-icon">{fw.icon}</span>
              <span>{fw.name}</span>
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="template-container">
          <div className="template-header">
            <h3>Generated Integration Code</h3>
            <div className="template-actions">
              <button onClick={handleCopy} className="action-button">
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button onClick={handleDownload} className="action-button">
                <Download size={16} />
                Download
              </button>
            </div>
          </div>

          <Tabs.Content value="langchain" className="template-content">
            <pre className="code-display">
              <code>{template}</code>
            </pre>
          </Tabs.Content>

          <Tabs.Content value="autogen" className="template-content">
            <pre className="code-display">
              <code>{template}</code>
            </pre>
          </Tabs.Content>

          <Tabs.Content value="crewai" className="template-content">
            <pre className="code-display">
              <code>{template}</code>
            </pre>
          </Tabs.Content>

          <Tabs.Content value="raw" className="template-content">
            <pre className="code-display">
              <code>{getRawPrompt()}</code>
            </pre>
          </Tabs.Content>
        </div>

        <div className="integration-info">
          <h3>How to Use</h3>
          <div className="framework-instructions">
            {selectedFramework === 'langchain' && (
              <div>
                <p>1. Install LangChain: <code>pip install langchain</code></p>
                <p>2. Copy the code above into your Python file</p>
                <p>3. Use the system_message when creating your chat model</p>
                <p>4. The agent will now understand the user's work patterns</p>
              </div>
            )}
            {selectedFramework === 'autogen' && (
              <div>
                <p>1. Install AutoGen: <code>pip install pyautogen</code></p>
                <p>2. Use the user_profile when creating your AssistantAgent</p>
                <p>3. The agent will adapt its responses to the user's patterns</p>
              </div>
            )}
            {selectedFramework === 'crewai' && (
              <div>
                <p>1. Install CrewAI: <code>pip install crewai</code></p>
                <p>2. Use this agent configuration in your crew</p>
                <p>3. The agent will provide personalized productivity coaching</p>
              </div>
            )}
            {selectedFramework === 'raw' && (
              <div>
                <p>1. Copy this prompt as your system message</p>
                <p>2. Use with any LLM API (OpenAI, Anthropic, etc.)</p>
                <p>3. The model will understand the user's work patterns</p>
              </div>
            )}
          </div>
        </div>

        <div className="persona-summary">
          <h3>Active Persona Summary</h3>
          <div className="summary-content">
            <p><strong>Mapper:</strong> {selectedPersona.mapper_id}</p>
            <p><strong>Generated:</strong> {new Date(selectedPersona.created_at).toLocaleString()}</p>
            <p><strong>Expires:</strong> {new Date(selectedPersona.expires_at).toLocaleString()}</p>
            
            <h4>Current Suggestions</h4>
            {selectedPersona.overlay.suggestions?.map((sugg: any, idx: number) => (
              <div key={idx} className="mini-suggestion">
                <strong>{sugg.title}:</strong> {sugg.description}
              </div>
            ))}
          </div>
        </div>
      </Tabs.Root>
    </div>
  );
};