// Sidebar component
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';

interface SidebarLink {
  href: string;
  label: string;
  icon?: string;
}

const mainLinks: SidebarLink[] = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/entities', label: 'Entities' },
  { href: '/properties', label: 'Properties' },
];

const adminLinks: SidebarLink[] = [
  { href: '/admin/cases', label: 'Case Review' },
  { href: '/admin/alerts', label: 'Alerts' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 border-r bg-white lg:block">
      <div className="flex h-full flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-1">
            <p className="mb-2 px-3 text-xs font-semibold uppercase text-gray-500">Main</p>
            {mainLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  pathname === link.href
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="mt-6 space-y-1">
            <p className="mb-2 px-3 text-xs font-semibold uppercase text-gray-500">Admin</p>
            {adminLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  pathname === link.href
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
