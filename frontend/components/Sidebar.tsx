import Link from 'next/link'
import { useRouter } from 'next/router'

const links = [
  { href: '/', label: 'Home' },
  { href: '/basic', label: 'Basic' },
  { href: '/sql', label: 'SQL' },
  { href: '/web', label: 'Web' },
  { href: '/advisory', label: 'Advisory' },
  { href: '/multi', label: 'Multi' },
]

export default function Sidebar() {
  const router = useRouter()
  return (
    <div className="w-56 min-h-screen bg-gray-900 text-white p-4">
      <nav className="space-y-2">
        {links.map(link => (
          <Link
            key={link.href}
            href={link.href}
            className={`block px-3 py-2 rounded hover:bg-gray-700 ${
              router.pathname === link.href ? 'bg-gray-700' : ''
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
