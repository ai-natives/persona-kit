import React, { useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

export const ProfilePanel: React.FC = () => {
  const { 
    profiles, 
    currentProfile, 
    memoryState,
    loadProfiles, 
    selectProfile,
    fetchMemoryState
  } = useChatStore();

  useEffect(() => {
    loadProfiles();
    fetchMemoryState();
    
    // Poll memory state every 5 seconds
    const interval = setInterval(fetchMemoryState, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-80 bg-gray-50 p-4 border-r flex flex-col">
      <h2 className="text-lg font-semibold mb-4">Learner Profile</h2>

      {/* Profile selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Select Learner:</label>
        <select
          value={currentProfile?.id || ''}
          onChange={(e) => selectProfile(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">General (No Profile)</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </div>

      {/* Current profile details */}
      {currentProfile && (
        <div className="mb-6 p-4 bg-white rounded-lg shadow">
          <h3 className="font-semibold mb-2">{currentProfile.name}</h3>
          <p className="text-sm text-gray-600 mb-3">{currentProfile.description}</p>
          
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-medium">Tech Level:</span>{' '}
              <span className="capitalize">{currentProfile.traits.techLevel}</span>
            </div>
            <div>
              <span className="font-medium">Learning Style:</span>{' '}
              <span className="capitalize">{currentProfile.traits.learningStyle.replace(/_/g, ' ')}</span>
            </div>
            <div>
              <span className="font-medium">Preference:</span>{' '}
              <span className="capitalize">{currentProfile.traits.preference.replace(/_/g, ' ')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Memory stats */}
      <div className="mt-auto">
        <h3 className="font-semibold mb-2">Memory Stats</h3>
        
        {memoryState ? (
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-white rounded-lg">
              <h4 className="font-medium mb-1">Session Memory (Agno)</h4>
              <div className="text-gray-600">
                <div>• Turns: {memoryState.agno.sessionTurns}</div>
                <div>• Messages: {memoryState.agno.messageCount}</div>
                <div>• Adaptations: {memoryState.agno.adaptations.length}</div>
              </div>
            </div>
            
            <div className="p-3 bg-white rounded-lg">
              <h4 className="font-medium mb-1">Learner Model (PersonaKit)</h4>
              <div className="text-gray-600">
                <div>• {memoryState.personakit.usingDemoProfiles ? 'Demo Mode 🎭' : 'PersonaKit Connected ✅'}</div>
                {memoryState.personakit.currentLearner?.name && (
                  <div>• Active: {memoryState.personakit.currentLearner.name}</div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-gray-500">Loading memory state...</div>
        )}
      </div>
    </div>
  );
};