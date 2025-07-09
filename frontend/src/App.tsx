import { useState } from 'react';
import AskComponent from './AskComponent';
import ChatComponent from './ChatComponent';

export default function App() {
  const [mode, setMode] = useState<'ask' | 'chat'>('ask');

  return (
    <div className="min-h-screen flex flex-col items-center bg-gradient-to-br from-blue-50 to-white p-6">
      <h1 className="text-4xl font-bold mb-6 text-blue-600">LLM RAG Chat Demo</h1>

      <div className="flex gap-4 mb-6">
        <button
          className={`px-4 py-2 rounded-lg shadow ${mode === 'ask' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setMode('ask')}
        >
          Q&A Mode
        </button>
        <button
          className={`px-4 py-2 rounded-lg shadow ${mode === 'chat' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setMode('chat')}
        >
          Chat Mode
        </button>
      </div>

      {mode === 'ask' && <AskComponent />}
      {mode === 'chat' && <ChatComponent />}
    </div>
  );
}
