import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';

describe('AuthProvider', () => {
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

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const TestComponent = () => {
    const { user, isAuthenticated, isLoading } = useAuth();
    
    if (isLoading) return <div>Loading...</div>;
    if (isAuthenticated) return <div>Authenticated: {user?.username}</div>;
    return <div>Not authenticated</div>;
  };

  it('initializes with loading state', () => {
    (global.fetch as any).mockImplementation(() => new Promise(() => {}));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('sets user data on successful auth check', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false }),
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/authenticated: .*jdoe/i)).toBeInTheDocument();
    });
  });

  it('sets unauthenticated on failed auth check', async () => {
    (global.fetch as any).mockResolvedValueOnce({ ok: false });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/not authenticated/i)).toBeInTheDocument();
    });
  });

  it('handles network errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/not authenticated/i)).toBeInTheDocument();
    });
  });

  it('login updates user state', async () => {
    (global.fetch as any).mockResolvedValueOnce({ ok: false });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.login({
        id: '123',
        username: '\\\\COLLEGE\\\\jdoe',
        is_blocked: false,
      });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.username).toBe('\\\\COLLEGE\\\\jdoe');
  });

  it('logout clears user state and calls API', async () => {
    (global.fetch as any).mockResolvedValueOnce({ ok: false });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Set initial user
    act(() => {
      result.current.login({ id: '123', username: 'user', is_blocked: false });
    });

    expect(result.current.isAuthenticated).toBe(true);

    // Mock logout API
    (global.fetch as any).mockResolvedValueOnce({ ok: true });

    // Logout
    await act(async () => {
      await result.current.logout();
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/logout'),
      expect.objectContaining({ method: 'POST', credentials: 'include' })
    );
    expect(result.current.isAuthenticated).toBe(false);
    expect(mockRouter.push).toHaveBeenCalledWith('/');
  });

  it('logout redirects even if API fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({ ok: false });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.login({ id: '123', username: 'user', is_blocked: false });
    });

    // Mock logout API failure
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(mockRouter.push).toHaveBeenCalledWith('/');
  });

  it('throws error when useAuth used outside provider', () => {
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');
  });
});
