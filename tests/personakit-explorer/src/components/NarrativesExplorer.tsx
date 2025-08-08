import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as Tabs from '@radix-ui/react-tabs';
import { 
  FileText, 
  Search, 
  Plus, 
  Edit3, 
  Tag,
  MessageSquare,
  Sparkles,
  Clock
} from 'lucide-react';
import { personaKitAPI } from '../api/personakit';

interface NarrativesExplorerProps {
  personId: string;
}

export function NarrativesExplorer({ personId }: NarrativesExplorerProps) {
  const [activeSubTab, setActiveSubTab] = useState('browse');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<'all' | 'self_observation' | 'curation'>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  
  const queryClient = useQueryClient();

  // Fetch narratives
  const { data: narratives, isLoading, error } = useQuery({
    queryKey: ['narratives', personId, selectedType],
    queryFn: () => personaKitAPI.getNarratives(personId, selectedType === 'all' ? undefined : selectedType),
  });

  // Search narratives
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ['narratives-search', personId, searchQuery],
    queryFn: () => personaKitAPI.searchNarratives(personId, searchQuery),
    enabled: searchQuery.length > 2,
  });

  // Create narrative mutation
  const createNarrative = useMutation({
    mutationFn: (data: { type: 'self_observation' | 'curation', text: string, tags?: string[], traitPath?: string }) => 
      personaKitAPI.createNarrative(personId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['narratives'] });
      setShowAddModal(false);
    },
  });

  return (
    <div className="narratives-explorer">
      <div className="component-header">
        <h2>Narratives</h2>
        <p>Browse, search, and manage self-observations and curations</p>
      </div>

      <Tabs.Root value={activeSubTab} onValueChange={setActiveSubTab}>
        <div className="sub-tabs-container">
          <Tabs.List className="sub-tabs">
            <Tabs.Trigger value="browse" className="sub-tab">
              <FileText size={16} />
              Browse
            </Tabs.Trigger>
            <Tabs.Trigger value="search" className="sub-tab">
              <Search size={16} />
              Semantic Search
            </Tabs.Trigger>
            <Tabs.Trigger value="influence" className="sub-tab">
              <Sparkles size={16} />
              Influence Analysis
            </Tabs.Trigger>
          </Tabs.List>

          <button 
            className="button primary"
            onClick={() => setShowAddModal(true)}
          >
            <Plus size={16} />
            Add Narrative
          </button>
        </div>

        <Tabs.Content value="browse" className="sub-tab-content">
          <div className="narrative-filters">
            <div className="filter-group">
              <label>Type:</label>
              <select 
                value={selectedType} 
                onChange={(e) => setSelectedType(e.target.value as any)}
                className="select"
              >
                <option value="all">All Narratives</option>
                <option value="self_observation">Self Observations</option>
                <option value="curation">Curations</option>
              </select>
            </div>
          </div>

          <div className="narratives-list">
            {isLoading ? (
              <div className="loading">Loading narratives...</div>
            ) : error ? (
              <div className="error">Error loading narratives</div>
            ) : narratives?.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} strokeWidth={1} />
                <p>No narratives found</p>
                <button className="button secondary" onClick={() => setShowAddModal(true)}>
                  Add your first narrative
                </button>
              </div>
            ) : (
              narratives?.map((narrative) => (
                <NarrativeCard key={narrative.id} narrative={narrative} />
              ))
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content value="search" className="sub-tab-content">
          <div className="search-container">
            <div className="search-input-wrapper">
              <Search size={20} />
              <input
                type="text"
                placeholder="Search narratives semantically..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
            
            {searchQuery.length > 0 && searchQuery.length <= 2 && (
              <p className="hint">Type at least 3 characters to search</p>
            )}

            {isSearching && (
              <div className="loading">Searching...</div>
            )}

            {searchResults && (
              <div className="search-results">
                <h3>Search Results ({searchResults.length})</h3>
                {searchResults.map((result) => (
                  <div key={result.narrative.id} className="search-result">
                    <div className="similarity-score">
                      {(result.similarity_score * 100).toFixed(0)}%
                    </div>
                    <NarrativeCard narrative={result.narrative} excerpt={result.excerpt} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content value="influence" className="sub-tab-content">
          <NarrativeInfluence personId={personId} />
        </Tabs.Content>
      </Tabs.Root>

      {showAddModal && (
        <AddNarrativeModal
          onClose={() => setShowAddModal(false)}
          onSubmit={(data) => createNarrative.mutate(data)}
          isLoading={createNarrative.isPending}
        />
      )}
    </div>
  );
}

function NarrativeCard({ narrative, excerpt }: { narrative: any, excerpt?: string }) {
  const typeIcon = narrative.narrative_type === 'curation' ? <Edit3 size={16} /> : <MessageSquare size={16} />;
  const typeClass = narrative.narrative_type === 'curation' ? 'curation' : 'self-observation';
  
  return (
    <div className={`narrative-card ${typeClass}`}>
      <div className="narrative-header">
        <div className="narrative-type">
          {typeIcon}
          <span>{narrative.narrative_type === 'curation' ? 'Curation' : 'Self Observation'}</span>
        </div>
        <div className="narrative-meta">
          <Clock size={14} />
          <span>{new Date(narrative.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      
      <div className="narrative-content">
        <p>{excerpt || narrative.raw_text}</p>
      </div>
      
      {narrative.tags && narrative.tags.length > 0 && (
        <div className="narrative-tags">
          <Tag size={14} />
          {narrative.tags.map((tag: string) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}
      
      {narrative.trait_path && (
        <div className="narrative-trait">
          <span className="trait-label">Curates:</span>
          <code>{narrative.trait_path}</code>
        </div>
      )}
    </div>
  );
}

function NarrativeInfluence({ personId }: { personId: string }) {
  const { data: influences, isLoading } = useQuery({
    queryKey: ['narrative-influences', personId],
    queryFn: () => personaKitAPI.getNarrativeInfluences(personId),
  });

  if (isLoading) return <div className="loading">Loading influence data...</div>;

  return (
    <div className="influence-analysis">
      <h3>Narrative Influence on Recent Personas</h3>
      <p className="section-description">
        See which narratives have influenced persona generation and their relevance scores.
      </p>

      {influences?.map((influence) => (
        <div key={influence.persona_id} className="influence-item">
          <div className="influence-header">
            <h4>Persona: {influence.mapper_name}</h4>
            <span className="influence-date">
              {new Date(influence.created_at).toLocaleDateString()}
            </span>
          </div>
          
          <div className="influenced-narratives">
            {influence.narratives.map((item) => (
              <div key={item.narrative_id} className="influenced-narrative">
                <div className="relevance-bar">
                  <div 
                    className="relevance-fill"
                    style={{ width: `${item.relevance_score * 100}%` }}
                  />
                </div>
                <p className="narrative-preview">{item.excerpt}</p>
                <span className="relevance-score">
                  {(item.relevance_score * 100).toFixed(0)}% relevant
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AddNarrativeModal({ 
  onClose, 
  onSubmit, 
  isLoading 
}: { 
  onClose: () => void, 
  onSubmit: (data: any) => void,
  isLoading: boolean 
}) {
  const [type, setType] = useState<'self_observation' | 'curation'>('self_observation');
  const [text, setText] = useState('');
  const [tags, setTags] = useState('');
  const [traitPath, setTraitPath] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      type,
      text,
      tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      ...(type === 'curation' && { traitPath }),
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Narrative</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="narrative-form">
          <div className="form-group">
            <label>Type</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  value="self_observation"
                  checked={type === 'self_observation'}
                  onChange={(e) => setType(e.target.value as any)}
                />
                Self Observation
              </label>
              <label>
                <input
                  type="radio"
                  value="curation"
                  checked={type === 'curation'}
                  onChange={(e) => setType(e.target.value as any)}
                />
                Curation
              </label>
            </div>
          </div>

          {type === 'curation' && (
            <div className="form-group">
              <label>Trait Path</label>
              <input
                type="text"
                placeholder="e.g., work.focus_duration"
                value={traitPath}
                onChange={(e) => setTraitPath(e.target.value)}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Narrative Text</label>
            <textarea
              placeholder={type === 'self_observation' 
                ? "Describe your observation..." 
                : "Explain your curation..."}
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              required
            />
          </div>

          <div className="form-group">
            <label>Tags (comma-separated)</label>
            <input
              type="text"
              placeholder="productivity, morning, focus"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="button secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="button primary" disabled={isLoading}>
              {isLoading ? 'Adding...' : 'Add Narrative'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}