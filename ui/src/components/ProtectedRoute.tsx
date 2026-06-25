import { Navigate } from 'react-router-dom';
import { getCurrentUser } from '../types';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  const user = getCurrentUser();

  if (!token || !user) {
    // Clear any stale partial state
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
