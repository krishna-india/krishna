import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow, { Message } from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';

export default function SQL() {
  const [messages, setMessages] = useState<Message[]>([]);

  const send = async (text: string) => {
    const user: Message = { role: 'user', text };
    setMessages((m) => [...m, user]);
    const res = await fetch('http://localhost:8000/chat/sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    if (!res.body) return;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let answer = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      if (value) answer += decoder.decode(value);
    }
    setMessages((m) => [...m, { role: 'assistant', text: answer }]);
  };

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <ChatWindow messages={messages} />
        <ChatInput onSend={send} />
      </div>
    </div>
  );
}
