import { LoginFormData } from './schemas';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface CounselorCategory {
  id: string;
  name: string;
  description: string;
  icon_name: string;
}

export interface CounselorCategoriesResponse {
  categories: CounselorCategory[];
  total: number;
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include', // Always send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Handle unauthorized globally
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const loginUser = async (credentials: LoginFormData) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
};

export async function getCategories(): Promise<CounselorCategory[]> {
  const response = await apiRequest<CounselorCategoriesResponse>(
    '/counselors/categories'
  );
  return response.categories;
}
