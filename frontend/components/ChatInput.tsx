import { useState } from 'react';

export default function ChatInput({ onSend }: { onSend(msg: string): void }) {
  const [value, setValue] = useState('');
  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        if (!value.trim()) return;
        onSend(value);
        setValue('');
      }}
      className="p-4 flex space-x-2"
    >
      <input
        className="flex-1 rounded border bg-zinc-900 text-white px-2"
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder="Type a message"
      />
      <button type="submit" className="px-3 rounded bg-blue-600 text-white">
        Send
      </button>
    </form>
  );
}
