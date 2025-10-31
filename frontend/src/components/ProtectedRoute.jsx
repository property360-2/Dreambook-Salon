import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth.js';

export function ProtectedRoute({ redirectTo = '/login' }) {
  const { isAuthenticated, status } = useAuth();
  const location = useLocation();

  if (status !== 'ready') {
    return (
      <div className="screen-centered">
        <p className="muted">Loading session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  return <Outlet />;
}
