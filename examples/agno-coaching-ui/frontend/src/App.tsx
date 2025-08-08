import React from 'react';
import { Chat } from './components/Chat';
import { ProfilePanel } from './components/ProfilePanel';
import { useChatStore } from './stores/chatStore';

function App() {
  const { resetSession, fetchMemoryState } = useChatStore();

  const handleShowMemory = async () => {
    await fetchMemoryState();
    // In a real app, this would open a modal or expand a panel
    console.log('Memory state updated - check the Profile Panel');
  };

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <header className="bg-gray-800 text-white p-4">
        <h1 className="text-xl font-bold">
          🎓 Senior Developer Mentor
          <span className="text-sm font-normal ml-2 opacity-75">
            Powered by Agno + PersonaKit
          </span>
        </h1>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Profile panel */}
        <ProfilePanel />

        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <Chat />
        </div>
      </div>

      {/* Footer controls */}
      <footer className="bg-gray-100 border-t p-4">
        <div className="flex space-x-4 justify-center">
          <button
            onClick={handleShowMemory}
            className="px-4 py-2 text-gray-700 hover:text-gray-900"
          >
            🧠 Show Memory
          </button>
          <button
            onClick={() => console.log('Show adaptations')}
            className="px-4 py-2 text-gray-700 hover:text-gray-900"
          >
            📊 Show Adaptations
          </button>
          <button
            onClick={resetSession}
            className="px-4 py-2 text-gray-700 hover:text-gray-900"
          >
            🔄 Reset Session
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;