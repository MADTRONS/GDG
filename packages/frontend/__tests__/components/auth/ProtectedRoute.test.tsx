import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';

describe('ProtectedRoute', () => {
  const mockRouter = {
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
    (useRouter as any).mockReturnValue(mockRouter);
  });

  it('shows loading state initially', () => {
    (global.fetch as any).mockImplementation(() => new Promise(() => {}));

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', async () => {
    (global.fetch as any).mockResolvedValueOnce({ ok: false });

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/');
    });

    expect(screen.queryByText(/protected content/i)).not.toBeInTheDocument();
  });

  it('renders children when authenticated', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '123', username: 'user', is_blocked: false }),
    });

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/protected content/i)).toBeInTheDocument();
    });

    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('does not redirect if authentication check succeeds', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '456', username: '\\\\COLLEGE\\\\testuser', is_blocked: false }),
    });

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Dashboard</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    });

    expect(mockRouter.push).not.toHaveBeenCalled();
  });
});
