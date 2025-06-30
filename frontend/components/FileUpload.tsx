export default function FileUpload({ onFiles }: { onFiles(files: FileList): void }) {
  return (
    <input
      type="file"
      accept="application/pdf"
      multiple
      onChange={e => e.target.files && onFiles(e.target.files)}
      className="p-2"
    />
  );
}
