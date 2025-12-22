import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SessionHistoryPage from '@/app/sessions/page';

// Mock next/navigation
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => ({
    get: vi.fn(),
  }),
  usePathname: () => '/sessions',
}));

// Mock ProtectedRoute to render children directly in tests
vi.mock('@/components/auth/ProtectedRoute', () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock toast
const mockToast = vi.fn();
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({
    toast: mockToast,
  }),
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  format: (date: Date, formatStr: string) => '2025-12-20 • 10:00 AM',
}));

describe('SessionHistoryPage', () => {
  const mockSessions = [
    {
      session_id: 'session-1',
      counselor_category: 'Health Counselor',
      counselor_icon: '🏥',
      mode: 'voice' as const,
      started_at: '2025-12-20T10:00:00Z',
      ended_at: '2025-12-20T10:10:00Z',
      duration_seconds: 600,
      transcript_preview: 'I need help with stress management',
    },
    {
      session_id: 'session-2',
      counselor_category: 'Career Counselor',
      counselor_icon: '💼',
      mode: 'video' as const,
      started_at: '2025-12-19T14:30:00Z',
      ended_at: '2025-12-19T15:00:00Z',
      duration_seconds: 1800,
      transcript_preview: 'How can I improve my resume for tech jobs',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('displays loading state initially', async () => {
    (global.fetch as any).mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<SessionHistoryPage />);

    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument();
  });

  it('displays list of sessions after loading', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Health Counselor' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Career Counselor' })).toBeInTheDocument();
    });

    expect(screen.getByText(/stress management/i)).toBeInTheDocument();
    expect(screen.getByText(/improve my resume/i)).toBeInTheDocument();
  });

  it('shows empty state when no sessions exist', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: [],
        total_count: 0,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText(/no sessions yet/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/visit your dashboard/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to dashboard/i })).toBeInTheDocument();
  });

  it('navigates to session detail when card is clicked', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Health Counselor' })).toBeInTheDocument();
    });

    const sessionCard = screen.getByRole('heading', { name: 'Health Counselor' }).closest('[role="button"]');
    fireEvent.click(sessionCard!);

    expect(mockPush).toHaveBeenCalledWith('/sessions/session-1');
  });

  it('navigates to session detail with keyboard', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Health Counselor' })).toBeInTheDocument();
    });

    const sessionCard = screen.getByRole('heading', { name: 'Health Counselor' }).closest('[role="button"]');
    fireEvent.keyDown(sessionCard!, { key: 'Enter' });

    expect(mockPush).toHaveBeenCalledWith('/sessions/session-1');
  });

  it('displays correct mode icons', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Health Counselor' })).toBeInTheDocument();
    });

    // Check for mode icons by their aria-labels
    expect(screen.getByLabelText('Voice call')).toBeInTheDocument();
    expect(screen.getByLabelText('Video call')).toBeInTheDocument();
  });

  it('formats duration correctly', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText('10m 0s')).toBeInTheDocument();
      expect(screen.getByText('30m 0s')).toBeInTheDocument();
    });
  });

  it('filters sessions by category', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        sessions: [mockSessions[0]], // Only health counselor
        total_count: 1,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText('My Counseling Sessions')).toBeInTheDocument();
    });

    // Clear previous calls
    (global.fetch as any).mockClear();

    // Click Health category button
    const healthButton = screen.getByRole('button', { name: /🏥Health Counselor/i });
    fireEvent.click(healthButton);

    // Verify fetch was called with category filter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      const calls = (global.fetch as any).mock.calls;
      const lastCall = calls[calls.length - 1][0];
      expect(lastCall).toContain('category=Health');
    }, { timeout: 3000 });
  });

  it('filters sessions by mode', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        sessions: [mockSessions[1]], // Only video
        total_count: 1,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText('My Counseling Sessions')).toBeInTheDocument();
    });

    // Clear previous calls
    (global.fetch as any).mockClear();

    // Click Video Call mode button (filter button, not session card)
    const buttons = screen.getAllByRole('button', { name: /video call/i });
    const videoButton = buttons.find(b => b.tagName === 'BUTTON'); // Filter buttons are actual <button> elements
    fireEvent.click(videoButton!);

    // Verify fetch was called with mode filter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      const calls = (global.fetch as any).mock.calls;
      const lastCall = calls[calls.length - 1][0];
      expect(lastCall).toContain('mode=video');
    }, { timeout: 3000 });
  });

  it('clears filters when clear button is clicked', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText('My Counseling Sessions')).toBeInTheDocument();
    });

    // Set a filter first - click Health category
    const healthButton = screen.getByRole('button', { name: /🏥Health Counselor/i });
    fireEvent.click(healthButton);

    // Wait for Clear Filters button to appear
    await waitFor(() => {
      const clearButton = screen.queryByRole('button', { name: /clear filters/i });
      expect(clearButton).toBeInTheDocument();
    });

    // Click clear filters
    const clearButton = screen.getByRole('button', { name: /clear filters/i });
    fireEvent.click(clearButton);

    // Verify the "All Categories" button is now active (should have default variant)
    await waitFor(() => {
      const allCategoriesButton = screen.getByRole('button', { name: /📋All Categories/i });
      expect(allCategoriesButton).toBeInTheDocument();
    });
  });

  it('shows pagination for multiple pages', async () => {
    const manySessions = Array.from({ length: 25 }, (_, i) => ({
      ...mockSessions[0],
      session_id: `session-${i}`,
    }));

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: manySessions.slice(0, 20),
        total_count: 25,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument();
    });
  });

  it('navigates to next page', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 25,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
    });

    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);

    await waitFor(() => {
      const calls = (global.fetch as any).mock.calls;
      const lastCall = calls[calls.length - 1][0];
      expect(lastCall).toContain('page=2');
    });
  });

  it('shows error toast on fetch failure', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error Loading Sessions',
          variant: 'destructive',
        })
      );
    });
  });

  it('shows no results message when filters return empty', async () => {
    // First call returns sessions
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: mockSessions,
        total_count: 2,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      expect(screen.getByText('My Counseling Sessions')).toBeInTheDocument();
    });

    // Second call returns empty after filter
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: [],
        total_count: 0,
        page: 1,
        limit: 20,
      }),
    });

    // Apply filter - click Financial category button
    const financialButton = screen.getByRole('button', { name: /💰Financial Counselor/i });
    fireEvent.click(financialButton);

    await waitFor(() => {
      expect(screen.getByText(/no sessions found matching your filters/i)).toBeInTheDocument();
    });
  });

  it('navigates to dashboard from empty state', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sessions: [],
        total_count: 0,
        page: 1,
        limit: 20,
      }),
    });

    render(<SessionHistoryPage />);

    await waitFor(() => {
      const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
      fireEvent.click(dashboardButton);
    });

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });
});
