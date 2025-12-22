import { render, screen, waitFor } from '@testing-library/react';
import { StatsWidget } from '@/components/StatsWidget';
import { useRouter } from 'next/navigation';
import { vi } from 'vitest';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('StatsWidget', () => {
  const mockPush = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.clear();
    mockLocalStorage.setItem('token', 'test-token');
    (useRouter as unknown as ReturnType<typeof vi.fn>).mockReturnValue({ push: mockPush });
    global.fetch = vi.fn() as typeof global.fetch;
  });

  it('renders loading state initially', () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockImplementation(() => 
      new Promise(() => {}) // Never resolves
    );

    render(<StatsWidget />);
    
    expect(screen.getByText('Your Session Summary')).toBeInTheDocument();
    // Check for spinner animation class
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('renders empty state when no sessions exist', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 0,
        total_hours: 0.0,
        top_category: null,
        top_category_icon: null,
        last_session_date: null,
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText(/You haven't started any sessions yet/i)).toBeInTheDocument();
    });
    
    const button = screen.getByRole('button', { name: /View All Sessions/i });
    expect(button).toBeDisabled();
  });

  it('renders stats when sessions exist', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 5,
        total_hours: 3.5,
        top_category: 'Anxiety Support',
        top_category_icon: '😰',
        last_session_date: '2024-12-20T10:00:00Z',
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('3.5')).toBeInTheDocument();
      expect(screen.getByText('Anxiety Support')).toBeInTheDocument();
      expect(screen.getByText('😰')).toBeInTheDocument();
    });

    expect(screen.getByText('Total Sessions')).toBeInTheDocument();
    expect(screen.getByText('Total Hours')).toBeInTheDocument();
    expect(screen.getByText('Top Category')).toBeInTheDocument();
    expect(screen.getByText('Last Session')).toBeInTheDocument();
  });

  it('formats last session date correctly for today', async () => {
    const today = new Date();
    
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 1,
        total_hours: 0.5,
        top_category: 'Career Guidance',
        top_category_icon: '💼',
        last_session_date: today.toISOString(),
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('Today')).toBeInTheDocument();
    });
  });

  it('formats last session date correctly for yesterday', async () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 1,
        total_hours: 0.5,
        top_category: 'Career Guidance',
        top_category_icon: '💼',
        last_session_date: yesterday.toISOString(),
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('Yesterday')).toBeInTheDocument();
    });
  });

  it('formats last session date correctly for days ago', async () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 1,
        total_hours: 0.5,
        top_category: 'Career Guidance',
        top_category_icon: '💼',
        last_session_date: threeDaysAgo.toISOString(),
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('3 days ago')).toBeInTheDocument();
    });
  });

  it('navigates to session history when button is clicked', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 3,
        total_hours: 2.0,
        top_category: 'Anxiety Support',
        top_category_icon: '😰',
        last_session_date: '2024-12-20T10:00:00Z',
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    const button = screen.getByRole('button', { name: /View All Sessions/i });
    button.click();

    expect(mockPush).toHaveBeenCalledWith('/session-history');
  });

  it('renders error state when fetch fails', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText(/Error loading stats/i)).toBeInTheDocument();
    });
  });

  it('sends authorization header with token', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 0,
        total_hours: 0.0,
        top_category: null,
        top_category_icon: null,
        last_session_date: null,
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/sessions/stats',
        expect.objectContaining({
          headers: {
            'Authorization': 'Bearer test-token',
          },
        })
      );
    });
  });

  it('handles missing top category icon gracefully', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 2,
        total_hours: 1.5,
        top_category: 'Custom Category',
        top_category_icon: null,
        last_session_date: '2024-12-20T10:00:00Z',
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('Custom Category')).toBeInTheDocument();
      expect(screen.getByText('Top Category')).toBeInTheDocument();
    });
  });

  it('displays N/A when top category is null', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 1,
        total_hours: 0.5,
        top_category: null,
        top_category_icon: null,
        last_session_date: '2024-12-20T10:00:00Z',
      }),
    });

    render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });
  });

  it('uses responsive grid layout', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_sessions: 5,
        total_hours: 3.5,
        top_category: 'Anxiety Support',
        top_category_icon: '😰',
        last_session_date: '2024-12-20T10:00:00Z',
      }),
    });

    const { container } = render(<StatsWidget />);

    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument();
    });

    const grid = container.querySelector('.grid');
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-4');
  });
});