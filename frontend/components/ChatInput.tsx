import { useState } from 'react';

export default function ChatInput({ onSend }: { onSend(msg: string): void }) {
  const [value, setValue] = useState('');
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!value.trim()) return;
        onSend(value);
        setValue('');
      }}
      className="sticky bottom-0 bg-zinc-800 border-t border-zinc-700 p-4 flex space-x-2"
    >
      <textarea
        className="flex-1 resize-none rounded-md bg-zinc-900 text-white p-2 focus:outline-none"
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type a message"
      />
      <button type="submit" className="px-3 py-2 rounded-md bg-blue-600 text-white">
        Send
      </button>
    </form>
  );
}
