import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
};

const useAuthMock = vi.fn();

vi.mock('../hooks/useAuth.js', () => ({
  useAuth: () => useAuthMock(),
}));

import { ProtectedRoute } from './ProtectedRoute.jsx';

const renderWithRoutes = () =>
  render(
    <MemoryRouter initialEntries={['/dashboard']} future={routerFutureFlags}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard Screen</div>} />
        </Route>
        <Route path="/login" element={<div>Login Screen</div>} />
      </Routes>
    </MemoryRouter>,
  );

describe('ProtectedRoute', () => {
  beforeEach(() => {
    useAuthMock.mockReset();
  });

  it('renders a loading indicator while auth status is resolving', () => {
    useAuthMock.mockReturnValue({
      status: 'loading',
      isAuthenticated: false,
    });

    renderWithRoutes();

    expect(
      screen.getByText(/Loading session\.\.\./i),
    ).toBeInTheDocument();
  });

  it('redirects unauthenticated users to the login page', async () => {
    useAuthMock.mockReturnValue({
      status: 'ready',
      isAuthenticated: false,
    });

    renderWithRoutes();

    await waitFor(() => {
      expect(screen.getByText(/Login Screen/i)).toBeInTheDocument();
    });
  });

  it('renders nested routes when the user is authenticated', async () => {
    useAuthMock.mockReturnValue({
      status: 'ready',
      isAuthenticated: true,
    });

    renderWithRoutes();

    await waitFor(() => {
      expect(
        screen.getByText(/Dashboard Screen/i),
      ).toBeInTheDocument();
    });
  });
});
