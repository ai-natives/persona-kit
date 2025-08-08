import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronRight, ChevronDown, Clock, BarChart, Info, MessageSquare, User, Calendar } from 'lucide-react';
import { personaKitAPI } from '../api/personakit';

interface TraitNodeProps {
  name: string;
  trait: {
    value: any;
    confidence: number;
    sample_size: number;
    timestamp?: string;
  };
  level: number;
}

const TraitNode: React.FC<TraitNodeProps> = ({ name, trait, level }) => {
  const [expanded, setExpanded] = useState(false);
  const isObject = typeof trait.value === 'object' && trait.value !== null;
  
  return (
    <div className="trait-node" style={{ marginLeft: `${level * 20}px` }}>
      <div 
        className="trait-header"
        onClick={() => isObject && setExpanded(!expanded)}
        style={{ cursor: isObject ? 'pointer' : 'default' }}
      >
        {isObject && (expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}
        <span className="trait-name">{name}</span>
        <div className="trait-badges">
          <span className="confidence-badge" title="Confidence">
            {(trait.confidence * 100).toFixed(0)}%
          </span>
          <span className="sample-badge" title="Sample size">
            n={trait.sample_size}
          </span>
        </div>
      </div>
      
      {!isObject && (
        <div className="trait-value">
          {JSON.stringify(trait.value)}
        </div>
      )}
      
      {isObject && expanded && (
        <div className="trait-children">
          {Object.entries(trait.value).map(([key, value]) => (
            <div key={key} className="trait-child">
              <span className="child-key">{key}:</span>
              <span className="child-value">{JSON.stringify(value)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface TraitTimelineProps {
  personId: string;
  traitName: string;
}

const TraitTimeline: React.FC<TraitTimelineProps> = ({ personId, traitName }) => {
  const { data: timeline } = useQuery({
    queryKey: ['trait-timeline', personId, traitName],
    queryFn: () => personaKitAPI.getTraitTimeline(personId, traitName),
    enabled: !!traitName
  });

  if (!timeline) return null;

  const maxValue = Math.max(...timeline.timeline.map(t => 
    typeof t.value === 'number' ? t.value : 0
  ));

  return (
    <div className="trait-timeline">
      <h3><Clock size={16} /> Timeline for {traitName}</h3>
      <div className="timeline-chart">
        {timeline.timeline.map((point, idx) => (
          <div key={idx} className="timeline-point">
            <div 
              className="timeline-bar"
              style={{ 
                height: `${(point.value / maxValue) * 100}%`,
                opacity: point.confidence
              }}
              title={`Value: ${point.value}, Confidence: ${(point.confidence * 100).toFixed(0)}%`}
            />
            <div className="timeline-date">
              {new Date(point.timestamp).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const MindscapeExplorer: React.FC<{ personId: string }> = ({ personId }) => {
  const [selectedTrait, setSelectedTrait] = useState<string>('');
  
  const { data: mindscape, isLoading } = useQuery({
    queryKey: ['mindscape', personId],
    queryFn: () => personaKitAPI.getMindscape(personId)
  });

  const { data: observations } = useQuery({
    queryKey: ['observations', personId],
    queryFn: () => personaKitAPI.getObservations(personId, 10)
  });

  if (isLoading) return <div>Loading mindscape...</div>;
  if (!mindscape) return <div>No mindscape found</div>;

  // Group traits by category
  const traitsByCategory = Object.entries(mindscape.traits).reduce((acc, [name, trait]) => {
    const category = name.split('.')[0];
    if (!acc[category]) acc[category] = {};
    acc[category][name] = trait;
    return acc;
  }, {} as Record<string, any>);

  return (
    <div className="mindscape-explorer">
      <div className="explorer-header">
        <h2>Mindscape v{mindscape.version}</h2>
        <div className="header-info">
          <span><Info size={14} /> {Object.keys(mindscape.traits).length} traits</span>
          <span><BarChart size={14} /> Last updated: {new Date(mindscape.updated_at).toLocaleString()}</span>
        </div>
      </div>

      <div className="explorer-content">
        <div className="traits-panel">
          <h3>Traits</h3>
          {Object.entries(traitsByCategory).map(([category, traits]) => (
            <div key={category} className="trait-category">
              <h4>{category}</h4>
              {Object.entries(traits).map(([name, trait]) => (
                <div key={name} onClick={() => setSelectedTrait(name)}>
                  <TraitNode name={name} trait={trait as any} level={0} />
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="detail-panel">
          {selectedTrait && (
            <>
              <div className="trait-detail">
                <h3>{selectedTrait}</h3>
                <div className="detail-content">
                  <p><strong>Value:</strong> {JSON.stringify(mindscape.traits[selectedTrait].value, null, 2)}</p>
                  <p><strong>Confidence:</strong> {(mindscape.traits[selectedTrait].confidence * 100).toFixed(0)}%</p>
                  <p><strong>Sample Size:</strong> {mindscape.traits[selectedTrait].sample_size}</p>
                </div>
              </div>

              <TraitTimeline personId={personId} traitName={selectedTrait} />

              <div className="contributing-observations">
                <h3>
                  <Info size={16} />
                  Contributing Observations
                </h3>
                {observations?.filter(obs => {
                  // Filter observations that might relate to this trait
                  const traitCategory = selectedTrait.split('.')[0];
                  return JSON.stringify(obs.content).toLowerCase().includes(traitCategory);
                }).slice(0, 5).map(obs => (
                  <ObservationCard key={obs.id} observation={obs} />
                ))}
                {observations?.filter(obs => {
                  const traitCategory = selectedTrait.split('.')[0];
                  return JSON.stringify(obs.content).toLowerCase().includes(traitCategory);
                }).length === 0 && (
                  <p className="no-observations">No direct observations for this trait yet</p>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ObservationCard({ observation }: { observation: any }) {
  const [expanded, setExpanded] = useState(false);
  
  const getObservationIcon = (type: string) => {
    switch(type) {
      case 'work_session':
        return <Clock size={14} />;
      case 'user_input':
        return <MessageSquare size={14} />;
      case 'calendar_event':
        return <Calendar size={14} />;
      default:
        return <Info size={14} />;
    }
  };

  const getObservationSummary = (obs: any) => {
    if (obs.type === 'work_session' && obs.content.activity === 'coaching_session') {
      return `Coaching: ${obs.content.topic}`;
    } else if (obs.type === 'user_input' && obs.content.type === 'question') {
      return `Question: "${obs.content.text}"`;
    } else if (obs.type === 'user_input' && obs.content.type === 'self_reflection') {
      return `Reflection: "${obs.content.text}"`;
    } else if (obs.type === 'work_session' && obs.content.achievement) {
      return `Achievement: ${obs.content.achievement}`;
    }
    return `${obs.type}: ${JSON.stringify(obs.content).substring(0, 50)}...`;
  };

  return (
    <div className="observation-card" onClick={() => setExpanded(!expanded)}>
      <div className="observation-header">
        <div className="obs-type-icon">
          {getObservationIcon(observation.type)}
          <span>{getObservationSummary(observation)}</span>
        </div>
        <span className="obs-time">{new Date(observation.created_at).toLocaleDateString()}</span>
      </div>
      {expanded && (
        <div className="observation-details">
          {observation.content.notes && (
            <p className="obs-notes">{observation.content.notes}</p>
          )}
          {observation.content.questions_asked && (
            <p className="obs-questions">Questions: {observation.content.questions_asked}</p>
          )}
          {observation.content.breakthrough && (
            <p className="obs-breakthrough">💡 {observation.content.breakthrough}</p>
          )}
        </div>
      )}
    </div>
  );
};