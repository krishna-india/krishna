import { useState } from 'react';

export default function ChatInput({ onSend }: { onSend(msg: string): void }) {
  const [value, setValue] = useState('');
  return (
    <form

        e.preventDefault();
        if (!value.trim()) return;
        onSend(value);
        setValue('');
      }}

        Send
      </button>
    </form>
  );
}
