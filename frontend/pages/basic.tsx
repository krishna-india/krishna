import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import TopNav from '../components/TopNav';
import ChatWindow, { Message } from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';

export default function Basic() {
  const [messages, setMessages] = useState<Message[]>([]);

  const send = async (text: string) => {
    const user: Message = { role: 'user', text };
    setMessages((m) => [...m, user, { role: 'assistant', text: '' }]);
    const res = await fetch('http://localhost:8000/chat/basic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    if (!res.body) return;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let answer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      chunk.split('\n').forEach((line) => {
        if (line.startsWith('data: ')) {
          answer += line.replace('data: ', '');
          setMessages((msgs) => {
            const copy = [...msgs];
            copy[copy.length - 1] = { role: 'assistant', text: answer };
            return copy;
          });
        }
      });
    }
  };

  return (
    <div className="flex h-screen bg-zinc-900 text-white">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <TopNav onClear={() => setMessages([])} />
        <ChatWindow messages={messages} />
        <ChatInput onSend={send} />
      </div>
    </div>
  );
}
