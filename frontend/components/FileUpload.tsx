export default function FileUpload({ onFile }: { onFile: (f: File) => void }) {
  return (
    <input
      type="file"
      accept="application/pdf"
      onChange={e => {
        if (e.target.files && e.target.files[0]) onFile(e.target.files[0])
      }}
      className="my-2"
    />
  )
}
