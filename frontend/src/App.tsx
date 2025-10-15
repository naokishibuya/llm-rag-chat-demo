import { useState } from 'react';
import { DEFAULT_MODEL, MODEL_OPTIONS, type ModelId } from './modelOptions';
import AskComponent from './AskComponent';
import ChatComponent from './ChatComponent';

export default function App() {
  const [mode, setMode] = useState<'ask' | 'chat'>('ask');
  const [model, setModel] = useState<ModelId>(DEFAULT_MODEL);

  return (
    <div className="min-h-screen flex flex-col items-center bg-gradient-to-br from-blue-50 to-white p-6">
      <h1 className="text-4xl font-bold mb-6 text-blue-600">LLM RAG Chat Demo</h1>

      <div className="flex gap-4 mb-6">
        <label className="flex items-center gap-2 bg-white border rounded-lg shadow px-4 py-2">
          <span className="text-sm font-semibold text-gray-600">Model</span>
          <select
            className="border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            value={model}
            onChange={(event) => setModel(event.target.value as ModelId)}
          >
            {MODEL_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </div>

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

      {mode === 'ask' && <AskComponent model={model} />}
      {mode === 'chat' && <ChatComponent model={model} />}
    </div>
  );
}
