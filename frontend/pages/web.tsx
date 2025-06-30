import Sidebar from '../components/Sidebar';

export default function Web() {
  return (
    <div className="flex h-screen text-white bg-black">
      <Sidebar />
      <main className="flex-1 p-4">Web chat coming soon.</main>
    </div>
  );
}
