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

// Voice Session API Types
export interface CreateVoiceRoomRequest {
  counselor_category: string; // UUID
}

export interface CreateVoiceRoomResponse {
  room_url: string;
  user_token: string;
  room_name: string;
  session_id: string;
}

export async function createVoiceRoom(
  categoryId: string
): Promise<CreateVoiceRoomResponse> {
  return apiRequest<CreateVoiceRoomResponse>('/voice/create-room', {
    method: 'POST',
    body: JSON.stringify({
      counselor_category: categoryId
    })
  });
}

// Video Session API Types
export interface CreateVideoRoomRequest {
  counselor_category: string; // UUID
}

export interface CreateVideoRoomResponse {
  room_url: string;
  access_token: string;
  room_name: string;
  session_id: string;
}

export async function createVideoRoom(
  categoryId: string
): Promise<CreateVideoRoomResponse> {
  return apiRequest<CreateVideoRoomResponse>('/video/create-room', {
    method: 'POST',
    body: JSON.stringify({
      counselor_category: categoryId
    })
  });
}

// Admin Metrics API Types
export interface CurrentMetrics {
  active_sessions_count: number;
  avg_connection_quality: string;
  error_rate_last_hour: number;
  api_response_time_p95: number;
  db_pool_active: number;
  db_pool_size: number;
  system_health: string;
}

export interface SessionMetrics {
  total_sessions: number;
  sessions_by_category: Record<string, number>;
  connection_quality_distribution: Record<string, number>;
}

export interface ExternalServices {
  daily_co: string;
  livekit: string;
  beyond_presence: string;
}

export interface AdminMetricsData {
  current: CurrentMetrics;
  sessions: SessionMetrics;
  external: ExternalServices;
}

export interface SessionAnalytics {
  total_sessions: number;
  avg_duration: number;
  sessions_by_category: Record<string, number>;
  sessions_by_mode: Record<string, number>;
  peak_usage_hours: Record<number, number>;
  daily_trend: Record<string, number>;
  avg_duration_by_category: Record<string, number>;
}

export async function fetchAdminMetrics(): Promise<AdminMetricsData> {
  const [current, sessions, external] = await Promise.all([
    apiRequest<CurrentMetrics>('/admin/metrics/current'),
    apiRequest<SessionMetrics>('/admin/metrics/sessions'),
    apiRequest<ExternalServices>('/admin/metrics/external-services'),
  ]);
  return { current, sessions, external };
}

export async function fetchSessionAnalytics(
  startDate: string,
  endDate: string
): Promise<SessionAnalytics> {
  return apiRequest<SessionAnalytics>(
    `/admin/analytics/sessions?start_date=${startDate}&end_date=${endDate}`
  );
}
