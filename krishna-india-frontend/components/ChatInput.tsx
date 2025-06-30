import { useState } from 'react'

export default function ChatInput({ onSend }: { onSend: (msg: string) => void }) {
  const [value, setValue] = useState('')
  return (
    <form
      onSubmit={e => { e.preventDefault(); onSend(value); setValue('') }}
      className="p-2 flex"
    >
      <input className="flex-1 border px-2 text-black" value={value} onChange={e => setValue(e.target.value)} />
      <button className="ml-2 bg-blue-600 text-white px-3 rounded" type="submit">Send</button>
    </form>
  )
}
