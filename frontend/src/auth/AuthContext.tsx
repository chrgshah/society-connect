import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { getCurrentUser, initializeCsrf, login as loginApi, logout as logoutApi } from '../api/authApi';
import { useToast } from '../components/ToastProvider';
import type { AuthUser } from '../types/auth';

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const toast = useToast();
  const [user, setUser] = useState<AuthUser | null>(null);
  const authenticatedUserRef = useRef<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleAuthExpired = () => {
      if (authenticatedUserRef.current) {
        toast.warning('Your session is no longer valid. Please sign in again.', 'Session expired');
      }
      authenticatedUserRef.current = null;
      setUser(null);
      setLoading(false);
    };
    window.addEventListener('auth:expired', handleAuthExpired);

    const bootstrap = async () => {
      try {
        await initializeCsrf();
        const profile = await getCurrentUser();
        authenticatedUserRef.current = profile;
        setUser(profile);
      } catch {
        authenticatedUserRef.current = null;
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    void bootstrap();

    return () => {
      window.removeEventListener('auth:expired', handleAuthExpired);
    };
  }, [toast]);

  const login = async (username: string, password: string) => {
    await loginApi(username, password);
    const data = await getCurrentUser();
    authenticatedUserRef.current = data;
    setUser(data);
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch {
      // ignore
    }
    authenticatedUserRef.current = null;
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
