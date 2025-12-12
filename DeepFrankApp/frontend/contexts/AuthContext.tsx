'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/types/api';
import { getCurrentUser, logout as apiLogout } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = (userData: User, token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('session_token', token);
    }
    setUser(userData);
    setLoading(false);
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      // Logout error - continue with clearing local state
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('session_token');
      }
      setUser(null);
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    setLoading(true);
    
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const token = localStorage.getItem('session_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const session = await getCurrentUser();
      setUser(session.user);
    } catch (error) {
      localStorage.removeItem('session_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

