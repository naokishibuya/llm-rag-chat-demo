import { useState } from 'react';
import axios from 'axios';
import type { ModelId } from './modelOptions';

type ModerationInfo = {
  verdict: string;
  severity: string;
  categories: string[];
  rationale?: string | null;
};

type AskResponse = {
  answer: string;
  intent: string;
  routing_rationale?: string | null;
  moderation: ModerationInfo;
};

type ResponseMeta = Omit<AskResponse, 'answer'>;

type AskProps = {
  model: ModelId;
};

export default function AskComponent({ model }: AskProps) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [meta, setMeta] = useState<ResponseMeta | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer('');
    setMeta(null);

    try {
      const res = await axios.post<AskResponse>('http://localhost:8000/ask', { question, model });
      const { answer: backendAnswer, ...rest } = res.data;
      setAnswer(backendAnswer);
      setMeta(rest);
    } catch {
      setAnswer('⚠️ Error contacting backend.');
      setMeta(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border w-full max-w-xl">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          className="flex-grow border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          disabled={loading || !question.trim()}
        >
          {loading ? '...' : 'Ask'}
        </button>
      </form>
      {answer && (
        <div className="mt-4 p-3 bg-gray-50 border rounded-lg">
          <p className="text-gray-800">{answer}</p>
          {meta && (
            <div className="mt-3 pt-3 border-t text-xs text-gray-600 space-y-1">
              <div>
                <span className="font-semibold">Classification:</span> {meta.intent},{' '}
                <span className="font-semibold">Permission:</span> {meta.moderation.verdict}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
