import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import * as Select from '@radix-ui/react-select';
import { ChevronDown, Play, Clock, Calendar, Battery } from 'lucide-react';
import { personaKitAPI, Persona } from '../api/personakit';

interface ContextControlsProps {
  context: Record<string, any>;
  onChange: (context: Record<string, any>) => void;
}

const ContextControls: React.FC<ContextControlsProps> = ({ context, onChange }) => {
  return (
    <div className="context-controls">
      <h3>Context Simulator</h3>
      
      <div className="control-group">
        <label><Clock size={14} /> Time of Day</label>
        <Select.Root 
          value={context.time_of_day || 'morning'}
          onValueChange={(value) => onChange({ ...context, time_of_day: value })}
        >
          <Select.Trigger className="select-trigger">
            <Select.Value />
            <ChevronDown size={16} />
          </Select.Trigger>
          <Select.Portal>
            <Select.Content className="select-content">
              <Select.Item value="early_morning" className="select-item">
                <Select.ItemText>Early Morning (5-8 AM)</Select.ItemText>
              </Select.Item>
              <Select.Item value="morning" className="select-item">
                <Select.ItemText>Morning (8-12 PM)</Select.ItemText>
              </Select.Item>
              <Select.Item value="afternoon" className="select-item">
                <Select.ItemText>Afternoon (12-5 PM)</Select.ItemText>
              </Select.Item>
              <Select.Item value="evening" className="select-item">
                <Select.ItemText>Evening (5-9 PM)</Select.ItemText>
              </Select.Item>
              <Select.Item value="night" className="select-item">
                <Select.ItemText>Night (9 PM-5 AM)</Select.ItemText>
              </Select.Item>
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </div>

      <div className="control-group">
        <label><Battery size={14} /> Energy Level</label>
        <Select.Root 
          value={context.energy_level || 'medium'}
          onValueChange={(value) => onChange({ ...context, energy_level: value })}
        >
          <Select.Trigger className="select-trigger">
            <Select.Value />
            <ChevronDown size={16} />
          </Select.Trigger>
          <Select.Portal>
            <Select.Content className="select-content">
              <Select.Item value="low" className="select-item">
                <Select.ItemText>Low</Select.ItemText>
              </Select.Item>
              <Select.Item value="medium" className="select-item">
                <Select.ItemText>Medium</Select.ItemText>
              </Select.Item>
              <Select.Item value="high" className="select-item">
                <Select.ItemText>High</Select.ItemText>
              </Select.Item>
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </div>

      <div className="control-group">
        <label><Calendar size={14} /> Day Type</label>
        <Select.Root 
          value={context.day_type || 'weekday'}
          onValueChange={(value) => onChange({ ...context, day_type: value })}
        >
          <Select.Trigger className="select-trigger">
            <Select.Value />
            <ChevronDown size={16} />
          </Select.Trigger>
          <Select.Portal>
            <Select.Content className="select-content">
              <Select.Item value="weekday" className="select-item">
                <Select.ItemText>Weekday</Select.ItemText>
              </Select.Item>
              <Select.Item value="weekend" className="select-item">
                <Select.ItemText>Weekend</Select.ItemText>
              </Select.Item>
              <Select.Item value="holiday" className="select-item">
                <Select.ItemText>Holiday</Select.ItemText>
              </Select.Item>
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </div>

      <div className="control-group">
        <label>Custom Context (JSON)</label>
        <textarea
          className="context-json"
          value={JSON.stringify(context, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              onChange(parsed);
            } catch (err) {
              // Invalid JSON, ignore
            }
          }}
        />
      </div>
    </div>
  );
};

interface PersonaPreviewProps {
  persona: Persona | null;
}

const PersonaPreview: React.FC<PersonaPreviewProps> = ({ persona }) => {
  if (!persona) {
    return (
      <div className="persona-preview empty">
        <p>Click "Generate Persona" to see the result</p>
      </div>
    );
  }

  return (
    <div className="persona-preview">
      <div className="preview-header">
        <h3>Generated Persona</h3>
        <span className="persona-id">{persona.id}</span>
      </div>

      <div className="preview-section">
        <h4>Core Traits</h4>
        <pre className="json-display">
          {JSON.stringify(persona.core, null, 2)}
        </pre>
      </div>

      <div className="preview-section">
        <h4>Current Overlay</h4>
        <pre className="json-display">
          {JSON.stringify(persona.overlay, null, 2)}
        </pre>
      </div>

      <div className="preview-section">
        <h4>Suggestions</h4>
        {persona.overlay.suggestions?.map((suggestion: any, idx: number) => (
          <div key={idx} className="suggestion-card">
            <h5>{suggestion.title}</h5>
            <p>{suggestion.description}</p>
            <span className="suggestion-reason">{suggestion.reason}</span>
          </div>
        ))}
      </div>

      <div className="preview-meta">
        <p>Expires: {new Date(persona.expires_at).toLocaleString()}</p>
        <p>Mapper: {persona.mapper_id}</p>
      </div>
    </div>
  );
};

export const PersonaLab: React.FC<{ personId: string }> = ({ personId }) => {
  const [selectedMapper, setSelectedMapper] = useState('daily_work_optimizer');
  const [context, setContext] = useState<Record<string, any>>({
    time_of_day: 'morning',
    energy_level: 'high',
    day_type: 'weekday'
  });
  const [generatedPersona, setGeneratedPersona] = useState<Persona | null>(null);

  const { data: mappers } = useQuery({
    queryKey: ['mappers'],
    queryFn: () => personaKitAPI.listMappers()
  });

  const generateMutation = useMutation({
    mutationFn: () => personaKitAPI.generatePersona(personId, selectedMapper, context),
    onSuccess: (persona) => {
      setGeneratedPersona(persona);
    }
  });

  const selectedMapperInfo = mappers?.find(m => m.id === selectedMapper);

  return (
    <div className="persona-lab">
      <div className="lab-header">
        <h2>Persona Laboratory</h2>
        <p>Experiment with different contexts and mappers</p>
      </div>

      <div className="lab-content">
        <div className="configuration-panel">
          <div className="mapper-selector">
            <h3>Select Mapper</h3>
            <Select.Root value={selectedMapper} onValueChange={setSelectedMapper}>
              <Select.Trigger className="select-trigger large">
                <Select.Value />
                <ChevronDown size={16} />
              </Select.Trigger>
              <Select.Portal>
                <Select.Content className="select-content">
                  {mappers?.map(mapper => (
                    <Select.Item key={mapper.id} value={mapper.id} className="select-item">
                      <Select.ItemText>
                        <div className="mapper-option">
                          <strong>{mapper.name}</strong>
                          <span>{mapper.description}</span>
                        </div>
                      </Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Portal>
            </Select.Root>

            {selectedMapperInfo && (
              <div className="mapper-info">
                <h4>Required Traits</h4>
                <ul className="trait-list required">
                  {selectedMapperInfo.required_traits.map(trait => (
                    <li key={trait}>{trait}</li>
                  ))}
                </ul>
                
                {selectedMapperInfo.optional_traits.length > 0 && (
                  <>
                    <h4>Optional Traits</h4>
                    <ul className="trait-list optional">
                      {selectedMapperInfo.optional_traits.map(trait => (
                        <li key={trait}>{trait}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </div>

          <ContextControls context={context} onChange={setContext} />

          <button 
            className="generate-button"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
          >
            <Play size={16} />
            {generateMutation.isPending ? 'Generating...' : 'Generate Persona'}
          </button>
        </div>

        <div className="preview-panel">
          <PersonaPreview persona={generatedPersona} />
        </div>
      </div>
    </div>
  );
};