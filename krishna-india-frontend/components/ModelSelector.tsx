export default function ModelSelector({ model, setModel }: { model: string; setModel: (m: string) => void }) {
  return (
    <select className="p-2 border" value={model} onChange={e => setModel(e.target.value)}>
      <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
      <option value="gpt-4-turbo">gpt-4-turbo</option>
    </select>
  )
}
