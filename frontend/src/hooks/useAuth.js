import { useAuthContext } from '../context/AuthProvider.jsx';

export function useAuth() {
  return useAuthContext();
}
