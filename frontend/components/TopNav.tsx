import Image from 'next/image';

export default function TopNav({ onClear }: { onClear(): void }) {
  return (
    <header className="flex items-center justify-between px-4 py-2 bg-zinc-800 text-white border-b border-zinc-700">
      <div className="flex items-center space-x-2">
        {/* logo */}
        <Image src="/logo.png" alt="logo" width={32} height={32} />
        <span className="font-semibold">Chatbot</span>
      </div>
      <div className="flex items-center space-x-4">
        <button onClick={onClear} className="text-sm px-3 py-1 rounded bg-zinc-700 hover:bg-zinc-600">Clear chat</button>
        <div className="w-8 h-8 rounded-full bg-zinc-600" />
      </div>
    </header>
  );
}
