import { useState } from 'react';
import axios from 'axios';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function ChatComponent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/chat', { messages: newMessages });
      setMessages([...newMessages, { role: 'assistant', content: res.data.answer }]);
    } catch {
      setMessages([...newMessages, { role: 'assistant', content: '⚠️ Error contacting backend.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border w-full max-w-xl flex flex-col">
      <div className="flex-grow overflow-y-auto h-[400px] p-4 bg-gray-50 rounded-lg border mb-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-center">Start the conversation!</p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex mb-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] p-3 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-grow border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          disabled={loading || !input.trim()}
        >
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
