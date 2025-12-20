import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';
import DashboardPage from '@/app/dashboard/page';

vi.mock('@/components/auth/AuthProvider');
vi.mock('next/navigation');

describe('DashboardPage', () => {
  const mockRouter = {
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue(mockRouter);
  });

  it('renders dashboard when authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<DashboardPage />);

    const welcomeMessages = screen.getAllByText(/welcome.*jdoe/i);
    expect(welcomeMessages.length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('has proper semantic structure', () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<DashboardPage />);

    expect(screen.getByRole('banner')).toBeInTheDocument(); // header
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument(); // footer
  });

  it('applies correct grid classes to main content', () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<DashboardPage />);

    const main = screen.getByRole('main');
    const grid = within(main).getByRole('generic', { hidden: true });
    
    expect(grid).toHaveClass('grid');
    expect(grid).toHaveClass('grid-cols-1');
    expect(grid).toHaveClass('md:grid-cols-2');
    expect(grid).toHaveClass('lg:grid-cols-3');
    expect(grid).toHaveClass('xl:grid-cols-4');
  });

  it('includes skip to main content link', () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<DashboardPage />);

    const skipLink = screen.getByText(/skip to main content/i);
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('main content has proper aria-label', () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<DashboardPage />);

    const main = screen.getByRole('main');
    expect(main).toHaveAttribute('aria-label', 'Counselor categories');
  });
});
