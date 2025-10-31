import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { api } from '../lib/api.js';

const STORAGE_KEY = 'dreambook_salon_session';

const AuthContext = createContext(undefined);

function readSession() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (error) {
    console.warn('Failed to parse stored session', error);
    return null;
  }
}

function writeSession(session) {
  if (!session) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [status, setStatus] = useState('idle');

  useEffect(() => {
    const stored = readSession();
    if (!stored?.token) {
      setStatus('ready');
      return;
    }

    setStatus('loading');

    api
      .currentUser(stored.token)
      .then((response) => {
        setUser(response.user);
        setToken(stored.token);
        setStatus('ready');
      })
      .catch(() => {
        writeSession(null);
        setStatus('ready');
      });
  }, []);

  const handleAuthSuccess = useCallback((data) => {
    setUser(data.user);
    setToken(data.token);
    writeSession({ token: data.token });
  }, []);

  const login = useCallback(async (credentials) => {
    const data = await api.login(credentials);
    handleAuthSuccess(data);
    return data.user;
  }, [handleAuthSuccess]);

  const register = useCallback(async (payload) => {
    const data = await api.register(payload);
    handleAuthSuccess(data);
    return data.user;
  }, [handleAuthSuccess]);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    writeSession(null);
  }, []);

  const value = useMemo(
    () => ({
      status,
      user,
      token,
      isAuthenticated: Boolean(user && token),
      login,
      register,
      logout,
    }),
    [status, user, token, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return value;
}
