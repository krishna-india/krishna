import { useEffect, useRef } from 'react';

export type Message = { role: 'user' | 'assistant'; text: string };

export default function ChatWindow({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages]);
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.map((m, i) => (
        <div
          key={i}
          className={`max-w-xl rounded px-3 py-2 ${m.role === 'user' ? 'bg-blue-600 text-white self-end ml-auto' : 'bg-zinc-800 text-white'}`}
        >
          {m.text}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
