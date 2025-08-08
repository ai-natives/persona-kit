import React, { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

export const Chat: React.FC = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, isLoading, error, sendMessage, currentProfile } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      await sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="border-b p-4">
        <h2 className="text-lg font-semibold">
          Chat with Senior Mentor
          {currentProfile && (
            <span className="text-sm font-normal text-gray-600 ml-2">
              (Adapting for {currentProfile.name})
            </span>
          )}
        </h2>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="mb-2">👋 Welcome! I'm your senior developer mentor.</p>
            <p className="text-sm">
              {currentProfile 
                ? `I've loaded ${currentProfile.name}'s profile and will adapt my teaching style.`
                : 'Select a learner profile or just start asking questions!'}
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <div className="text-sm font-semibold mb-1">
                {message.role === 'user' ? 'You' : 'Mentor'}
              </div>
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {message.adaptations && message.adaptations.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <div className="text-xs opacity-75">
                    🧠 Adaptations: {message.adaptations.join(', ')}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="animate-pulse">Mentor is thinking...</div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            Error: {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};