import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isBackendConnected: boolean;
  login: (email: string, password?: string) => Promise<void>;
  register: (data: {
    name: string;
    email: string;
    password?: string;
    phone: string;
    role: UserRole;
    is_equipment_owner?: boolean;
    location: string;
  }) => Promise<void>;
  logout: () => void;
  quickSwitchUser: (role: 'FARMER_OWNER' | 'FARMER' | 'VENDOR' | 'ADMIN') => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('krishi_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);

  // Check health and restore auth on mount
  useEffect(() => {
    const initAuth = async () => {
      // Check backend connection status
      const healthy = await api.checkBackendHealth();
      setIsBackendConnected(healthy);

      const savedToken = localStorage.getItem('krishi_token');
      const savedUser = localStorage.getItem('krishi_user');

      if (savedToken && savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser);
          setUser(parsedUser);
          setToken(savedToken);
          // If backend is live and saved token was a mock token, exchange it for a real JWT
          if (healthy && savedToken.startsWith('mock-jwt-')) {
            const response = await api.login(parsedUser.email || 'farmer@krishisetu.com', 'password123');
            setToken(response.access_token);
            setUser(response.user);
            localStorage.setItem('krishi_token', response.access_token);
            localStorage.setItem('krishi_user', JSON.stringify(response.user));
          } else {
            const me = await api.getMe();
            setUser(me);
            localStorage.setItem('krishi_user', JSON.stringify(me));
          }
        } catch {
          localStorage.removeItem('krishi_token');
          localStorage.removeItem('krishi_user');
          setUser(null);
          setToken(null);
        }
      } else {
        // Default demo account on first load
        try {
          const response = await api.login('farmer@krishisetu.com', 'password123');
          setToken(response.access_token);
          setUser(response.user);
          localStorage.setItem('krishi_token', response.access_token);
          localStorage.setItem('krishi_user', JSON.stringify(response.user));
        } catch {
          const defaultUser: User = {
            id: 1,
            name: 'Ramesh Kumar (Farmer & Owner)',
            email: 'farmer@krishisetu.com',
            phone: '9876543210',
            role: 'FARMER',
            is_equipment_owner: true,
            location: 'Nashik, Maharashtra',
            created_at: new Date().toISOString(),
          };
          const demoToken = 'mock-jwt-demo-token-farmer-1';
          localStorage.setItem('krishi_token', demoToken);
          localStorage.setItem('krishi_user', JSON.stringify(defaultUser));
          setUser(defaultUser);
          setToken(demoToken);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password?: string) => {
    setIsLoading(true);
    try {
      const response = await api.login(email, password);
      setToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('krishi_token', response.access_token);
      localStorage.setItem('krishi_user', JSON.stringify(response.user));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: {
    name: string;
    email: string;
    password?: string;
    phone: string;
    role: UserRole;
    is_equipment_owner?: boolean;
    location: string;
  }) => {
    setIsLoading(true);
    try {
      const response = await api.register(data);
      setToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('krishi_token', response.access_token);
      localStorage.setItem('krishi_user', JSON.stringify(response.user));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('krishi_token');
    localStorage.removeItem('krishi_user');
    setUser(null);
    setToken(null);
  };

  const quickSwitchUser = async (role: 'FARMER_OWNER' | 'FARMER' | 'VENDOR' | 'ADMIN') => {
    const emails: Record<string, string> = {
      FARMER_OWNER: 'farmer@krishisetu.com',
      FARMER: 'farmer2@krishisetu.com',
      VENDOR: 'vendor@krishisetu.com',
      ADMIN: 'admin@krishisetu.com',
    };
    await login(emails[role], 'password123');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        isBackendConnected,
        login,
        register,
        logout,
        quickSwitchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
