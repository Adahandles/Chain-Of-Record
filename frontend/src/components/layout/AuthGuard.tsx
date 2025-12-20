// Auth Guard component to protect routes
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { LoadingPage } from '@/components/shared/LoadingSpinner';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function AuthGuard({ children, requireAdmin = false }: AuthGuardProps) {
  const { user, loading, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/auth/login');
      } else if (requireAdmin && !isAdmin) {
        router.push('/dashboard');
      }
    }
  }, [user, loading, isAdmin, requireAdmin, router]);

  if (loading) {
    return <LoadingPage />;
  }

  if (!user || (requireAdmin && !isAdmin)) {
    return null;
  }

  return <>{children}</>;
}
