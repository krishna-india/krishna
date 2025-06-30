export default function ChatBubble({ role, content }: { role: string; content: string }) {
  const align = role === 'user' ? 'self-end bg-blue-200' : 'self-start bg-gray-200'
  return <div className={`p-2 m-1 rounded ${align}`}>{content}</div>
}
