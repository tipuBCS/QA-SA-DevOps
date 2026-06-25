export const API_BASE_URL = import.meta.env.VITE_API_URL;

export function getToken(): string | null {
  return localStorage.getItem('token');
}

export async function apiRequest(path: string, options?: RequestInit) {
  const token = getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  // If we get a 401 on an authenticated route, token is expired/invalid — clear auth state
  if (response.status === 401 && !path.startsWith('/users/login') && !path.startsWith('/users/signup')) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  return response;
}
