import { useEffect, useRef } from 'react';

export type Message = { role: 'user' | 'assistant'; text: string };

export default function ChatWindow({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages]);
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((m, i) => (
        <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : ''}`}>
          <div
            className={`max-w-xl whitespace-pre-wrap rounded-2xl px-4 py-2 ${
              m.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-black shadow'
            }`}
          >
            {m.text}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
