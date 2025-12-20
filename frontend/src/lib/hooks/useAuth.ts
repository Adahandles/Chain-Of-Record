// Auth hook for managing authentication state
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
  id: number;
  email: string;
  name?: string;
  role: 'user' | 'admin';
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (e) {
        console.error('Error parsing user data:', e);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // For demo purposes, we'll use a simple mock auth
      // In production, this would call the backend API
      const mockUser: User = {
        id: 1,
        email,
        name: email.split('@')[0],
        role: 'user',
      };
      const mockToken = 'demo-token-' + Date.now();

      localStorage.setItem('auth_token', mockToken);
      localStorage.setItem('user', JSON.stringify(mockUser));
      setUser(mockUser);

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setUser(null);
    router.push('/auth/login');
  };

  const isAdmin = user?.role === 'admin';

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin,
  };
}
