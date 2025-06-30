import Sidebar from '../components/Sidebar';

export default function Multi() {
  return (
    <div className="flex h-screen text-white bg-black">
      <Sidebar />
      <main className="flex-1 p-4">Multi-source chat coming soon.</main>
    </div>
  );
}
