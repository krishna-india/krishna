import Sidebar from '../components/Sidebar';
import FileUpload from '../components/FileUpload';

export default function Advisory() {
  return (
    <div className="flex h-screen text-white bg-black">
      <Sidebar />
      <main className="flex-1 p-4">
        <FileUpload onFiles={() => {}} />
        Advisory chat coming soon.
      </main>
    </div>
  );
}
