// Dashboard Layout wrapper
'use client';

import { AuthGuard } from './AuthGuard';
import { Navbar } from '@/components/shared/Navbar';
import { Sidebar } from '@/components/shared/Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function DashboardLayout({ children, requireAdmin = false }: DashboardLayoutProps) {
  return (
    <AuthGuard requireAdmin={requireAdmin}>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-8">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
