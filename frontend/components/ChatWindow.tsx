import { useEffect, useRef } from 'react'

export interface Message {
  role: 'user' | 'assistant'
  text: string
}

export default function ChatWindow({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.map((m, i) => (
        <div key={i} className={`p-2 rounded ${m.role === 'user' ? 'bg-blue-100' : 'bg-gray-200'}`}>{m.text}</div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
