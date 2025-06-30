import Link from 'next/link';
import { useRouter } from 'next/router';

const links = [
  { href: '/', label: 'Home' },
  { href: '/basic', label: 'Basic' },
  { href: '/sql', label: 'SQL' },
  { href: '/web', label: 'Web' },
  { href: '/advisory', label: 'Advisory' },
  { href: '/multi', label: 'Multi' }
];

export default function Sidebar() {
  const { pathname } = useRouter();
  return (
    <aside className="w-64 bg-zinc-950 text-white h-screen flex-shrink-0">
      <nav className="p-4 space-y-2">
        {links.map(l => (
          <Link
            key={l.href}
            href={l.href}
            className={`block px-2 py-1 rounded hover:bg-zinc-800 ${pathname === l.href ? 'bg-zinc-800' : ''}`}
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
