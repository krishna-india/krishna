import { useState } from 'react'

export default function ChatInput({ onSend }: { onSend: (msg: string) => void }) {
  const [value, setValue] = useState('')
  return (
    <form
      onSubmit={e => {
        e.preventDefault()
        onSend(value)
        setValue('')
      }}
      className="p-4 flex space-x-2"
    >
      <input
        className="flex-1 border rounded px-2 text-black"
        value={value}
        onChange={e => setValue(e.target.value)}
      />
      <button className="bg-blue-600 text-white px-3 py-1 rounded" type="submit">
        Send
      </button>
    </form>
  )
}
