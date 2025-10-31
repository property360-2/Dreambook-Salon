import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import { Login } from './Login.jsx';

const loginMock = vi.fn();

vi.mock('../hooks/useAuth.js', () => ({
  useAuth: () => ({
    login: loginMock,
  }),
}));

describe('Login', () => {
  beforeEach(() => {
    loginMock.mockReset();
    loginMock.mockResolvedValue({ name: 'Owner' });
  });

  const routerFutureFlags = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  };

  const renderLogin = () =>
    render(
      <MemoryRouter initialEntries={['/login']} future={routerFutureFlags}>
        <Login />
      </MemoryRouter>,
    );

  it('shows validation messages when submitting empty form', async () => {
    renderLogin();

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(
      await screen.findByText(/Email is required/i),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(/Password is required/i),
    ).toBeInTheDocument();
    expect(loginMock).not.toHaveBeenCalled();
  });

  it('calls login with the provided credentials', async () => {
    renderLogin();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'owner@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'secretpass' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        email: 'owner@example.com',
        password: 'secretpass',
      });
    });
  });
});
