import Chat from './components/Chat';
import StreamChat from './components/StreamChat';

export default function App() {
  return (
    <div className="container">
      <h1>LLM Meta Chatbot</h1>
      <Chat />
      <StreamChat />
    </div>
  );
}
