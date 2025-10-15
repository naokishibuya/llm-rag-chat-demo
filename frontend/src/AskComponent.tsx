import { useState } from 'react';
import axios from 'axios';
import type { ModelId } from './modelOptions';

type AskProps = {
  model: ModelId;
};

export default function AskComponent({ model }: AskProps) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer('');

    try {
      const res = await axios.post('http://localhost:8000/ask', { question, model });
      setAnswer(res.data.answer);
    } catch {
      setAnswer('⚠️ Error contacting backend.');
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
        <div className="mt-4 p-3 bg-gray-50 border rounded-lg">{answer}</div>
      )}
    </div>
  );
}
