import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import type { ModelId } from './modelOptions';

type ModerationInfo = {
  verdict: string;
  severity: string;
  categories: string[];
  rationale?: string | null;
};

type ChatResponse = {
  answer: string;
  intent: string;
  routing_rationale?: string | null;
  moderation: ModerationInfo;
};

type ResponseMeta = Omit<ChatResponse, 'answer'>;

type Message = {
  role: 'user' | 'assistant';
  content: string;
  meta?: ResponseMeta;
};

const createMessage = (role: 'user' | 'assistant', content: string, meta?: ResponseMeta): Message => ({
  role,
  content,
  meta
});

type ChatProps = {
  model: ModelId;
};

export default function ChatComponent({ model }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const lastMsgRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (lastMsgRef.current) {
      lastMsgRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = createMessage('user', input);
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    const payloadMessages = updatedMessages.map(({ role, content }) => ({ role, content }));

    try {
      const res = await axios.post<ChatResponse>('http://localhost:8000/chat', { messages: payloadMessages, model });
      const { answer, ...meta } = res.data;
      setMessages([...updatedMessages, createMessage('assistant', answer, meta)]);
    } catch {
      setMessages([...updatedMessages, createMessage('assistant', 'Error contacting backend.')]);
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
          <div
            key={idx}
            ref={idx === messages.length - 1 ? lastMsgRef : undefined}
            className={`flex mb-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] p-3 rounded-lg shadow-sm ${
                msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
              }`}
            >
              <div>{msg.content}</div>
              {msg.role === 'assistant' && msg.meta && (
                <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-700 space-y-1">
                  <div>
                    <span className="font-semibold">Classification:</span> {msg.meta.intent},{' '}
                    <span className="font-semibold">Permission:</span> {msg.meta.moderation.verdict}
                  </div>
                </div>
              )}
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
