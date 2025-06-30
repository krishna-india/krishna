import { useEffect, useRef } from 'react';

export type Message = { role: 'user' | 'assistant'; text: string };

export default function ChatWindow({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages]);
  return (

        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
