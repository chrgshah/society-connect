import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getCurrentUser, initializeCsrf, login as loginApi, logout as logoutApi } from '../api/authApi';
import type { AuthUser } from '../types/auth';

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleAuthExpired = () => {
      setUser(null);
      setLoading(false);
    };
    window.addEventListener('auth:expired', handleAuthExpired);

    const bootstrap = async () => {
      try {
        await initializeCsrf();
        const profile = await getCurrentUser();
        setUser(profile);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    void bootstrap();

    return () => {
      window.removeEventListener('auth:expired', handleAuthExpired);
    };
  }, []);

  const login = async (username: string, password: string) => {
    await loginApi(username, password);
    const data = await getCurrentUser();
    setUser(data);
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch {
      // ignore
    }
    setUser(null);
  };

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
