import { useEffect, useRef, useState } from 'react'
import ChatBubble from '../components/ChatBubble'
import ChatInput from '../components/ChatInput'
import ModelSelector from '../components/ModelSelector'

interface Msg { role: string; content: string }

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([])
  const [model, setModel] = useState('gpt-3.5-turbo')
  const sessionIdRef = useRef<string>('')
  useEffect(() => {
    let id = localStorage.getItem('session_id')
    if (!id) { id = Math.random().toString(36).slice(2); localStorage.setItem('session_id', id) }
    sessionIdRef.current = id
  }, [])

  const sendMessage = (msg: string) => {
    setMessages(m => [...m, { role: 'user', content: msg }])
    const es = new EventSource(`/api/stream?message=${encodeURIComponent(msg)}&session_id=${sessionIdRef.current}`)
    const assistant: Msg = { role: 'assistant', content: '' }
    setMessages(m => [...m, assistant])
    es.onmessage = e => {
      if (e.data === '[DONE]') { es.close(); return }
      assistant.content += e.data
      setMessages(m => [...m.slice(0, -1), assistant])
    }
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="p-2 border-b"><ModelSelector model={model} setModel={setModel} /></header>
      <div className="flex-1 overflow-y-auto p-2 flex flex-col">
        {messages.map((m, i) => <ChatBubble key={i} role={m.role} content={m.content} />)}
      </div>
      <ChatInput onSend={sendMessage} />
    </div>
  )
}
