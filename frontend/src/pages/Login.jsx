import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth.js';

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (values) => {
    try {
      setError(null);
      await login(values);
      const redirectTo = location.state?.from?.pathname ?? '/';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message ?? 'Login failed');
    }
  };

  return (
    <div className="screen-centered">
      <div className="card" style={{ width: 'min(480px, 100%)' }}>
        <h2 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Sign in</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Use the seeded admin account or create a customer account.
        </p>

        {error && <p className="error">{error}</p>}

        <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && (
              <span className="field-error" role="alert">
                {errors.email.message}
              </span>
            )}
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register('password', { required: 'Password is required' })}
            />
            {errors.password && (
              <span className="field-error" role="alert">
                {errors.password.message}
              </span>
            )}
          </div>

          <button type="submit" className="button" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="muted" style={{ marginTop: '1.25rem' }}>
          Need an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}
