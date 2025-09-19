import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function Chat() {
  const [message, setMessage] = useState('');
  const [reply, setReply] = useState('');
  const [providers, setProviders] = useState([]);

  async function sendChat(e) {
    e.preventDefault();
    setReply('');
    setProviders([]);
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    setReply(data.reply);
    setProviders(data.providers);
  }

  return (
    <div className="chat-box">
      <form onSubmit={sendChat}>
        <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Type a message..." />
        <button type="submit">Send</button>
      </form>
      {reply && <div className="reply">{reply}</div>}
      {providers.length > 0 && <div className="providers">Providers: {providers.join(', ')}</div>}
    </div>
  );
}
