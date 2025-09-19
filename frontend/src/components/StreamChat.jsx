import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function StreamChat() {
  const [message, setMessage] = useState('');
  const [stream, setStream] = useState('');
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);

  function startStream(e) {
    e.preventDefault();
    setStream('');
    setProviders([]);
    setLoading(true);
    const es = new EventSource(`${API_BASE}/api/chat/stream?message=${encodeURIComponent(message)}`);
    es.onmessage = (event) => {
      if (event.type === 'message') {
        if (event.data.startsWith('{')) {
          try {
            const obj = JSON.parse(event.data);
            setProviders(obj.providers || []);
            setLoading(false);
          } catch {}
        } else {
          setStream(s => s + event.data);
        }
      }
    };
    es.addEventListener('chunk', e => setStream(s => s + e.data));
    es.addEventListener('done', e => {
      try {
        const obj = JSON.parse(e.data);
        setProviders(obj.providers || []);
      } catch {}
      setLoading(false);
      es.close();
    });
    es.onerror = () => {
      setLoading(false);
      es.close();
    };
  }

  return (
    <div className="stream-chat-box">
      <form onSubmit={startStream}>
        <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Type a message for streaming..." />
        <button type="submit" disabled={loading}>Stream</button>
      </form>
      <div className="stream-reply">{stream}</div>
      {providers.length > 0 && <div className="providers">Providers: {providers.join(', ')}</div>}
    </div>
  );
}
