import { Outlet, Route, Routes, Navigate, Link, useNavigate } from 'react-router-dom';

import { ProtectedRoute } from './components/ProtectedRoute.jsx';
import { useAuth } from './hooks/useAuth.js';
import { Dashboard } from './pages/Dashboard.jsx';
import { Login } from './pages/Login.jsx';
import { NotFound } from './pages/NotFound.jsx';
import { Register } from './pages/Register.jsx';
import { Book } from './pages/Book.jsx';
import { BookConfirm } from './pages/BookConfirm.jsx';
import { BookComplete } from './pages/BookComplete.jsx';
import { PaymentDemo } from './pages/PaymentDemo.jsx';

function AppLayout() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-left">
          <h1>Dreambook Salon</h1>
          <p className="muted">Salon appointment & inventory system</p>
        </div>
        <nav className="app-nav">
          <Link to="/book">Book</Link>
          {isAuthenticated ? <Link to="/">Dashboard</Link> : null}
        </nav>
        <div>
          {isAuthenticated ? (
            <div
              className="flow"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-end',
              }}
            >
              <div>
                <span className="badge">{user.role ?? 'MEMBER'}</span>{' '}
                <strong>{user.name}</strong>
              </div>
              <button className="button" onClick={handleLogout}>
                Sign out
              </button>
            </div>
          ) : (
            <div
              className="flow"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-end',
              }}
            >
              <Link to="/login" className="button" style={{ display: 'inline-block' }}>
                Sign in
              </Link>
              <Link to="/register" className="muted">
                Create account
              </Link>
            </div>
          )}
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}

function GuestOnly({ children }) {
  const { isAuthenticated, status } = useAuth();

  if (status !== 'ready') {
    return (
      <div className="screen-centered">
        <p className="muted">Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route element={<ProtectedRoute />}>
          <Route index element={<Dashboard />} />
        </Route>
        <Route path="book" element={<Book />} />
        <Route path="book/confirm" element={<BookConfirm />} />
        <Route path="book/complete" element={<BookComplete />} />
        <Route path="payment/demo/:paymentId" element={<PaymentDemo />} />
        <Route
          path="login"
          element={
            <GuestOnly>
              <Login />
            </GuestOnly>
          }
        />
        <Route
          path="register"
          element={
            <GuestOnly>
              <Register />
            </GuestOnly>
          }
        />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
