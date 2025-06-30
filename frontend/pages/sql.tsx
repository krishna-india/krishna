import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import ChatWindow, { Message } from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'

export default function SqlPage() {
  const [messages, setMessages] = useState<Message[]>([])

  const sendMessage = async (msg: string) => {
    setMessages(m => [...m, { role: 'user', text: msg }])
    const res = await fetch('http://localhost:8000/chat/sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    })
    const data = await res.json()
    if (data.messages && data.messages[0]) {
      setMessages(m => [...m, { role: 'assistant', text: data.messages[0].text }])
    }
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <ChatWindow messages={messages} />
        <ChatInput onSend={sendMessage} />
      </div>
    </div>
  )
}
