import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { Loading } from '../components/Loading';
import { ROUTES } from '../config/paths';

export const ProtectedRoute = () => {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;
  return user ? <Outlet /> : <Navigate to={ROUTES.login} replace />;
};
