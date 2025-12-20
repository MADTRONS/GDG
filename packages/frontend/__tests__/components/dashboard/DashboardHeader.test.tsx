import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useAuth } from '@/components/auth/AuthProvider';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';

vi.mock('@/components/auth/AuthProvider');

describe('DashboardHeader', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays welcome message with username', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    const welcomeMessages = screen.getAllByText(/welcome.*jdoe/i);
    expect(welcomeMessages.length).toBeGreaterThan(0);
  });

  it('extracts username from domain\\username format', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '456', username: '\\\\DOMAIN\\\\alice', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    const welcomeMessages = screen.getAllByText(/welcome.*alice/i);
    expect(welcomeMessages.length).toBeGreaterThan(0);
    expect(screen.queryByText(/DOMAIN/)).not.toBeInTheDocument();
  });

  it('shows default name when user is null', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    const welcomeMessages = screen.getAllByText(/welcome.*student/i);
    expect(welcomeMessages.length).toBeGreaterThan(0);
  });

  it('displays platform logo/name', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    expect(screen.getByText(/college counseling/i)).toBeInTheDocument();
  });

  it('calls logout function when logout button clicked', async () => {
    const user = userEvent.setup();
    
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    const logoutButton = screen.getByRole('button', { name: /logout/i });
    await user.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('logout button is keyboard accessible', async () => {
    const user = userEvent.setup();
    
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    const logoutButton = screen.getByRole('button', { name: /logout/i });
    
    // Tab to button and press Enter
    await user.tab();
    expect(logoutButton).toHaveFocus();
    
    await user.keyboard('{Enter}');
    expect(mockLogout).toHaveBeenCalled();
  });

  it('has proper banner role', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: '123', username: '\\\\COLLEGE\\\\jdoe', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: mockLogout,
    });

    render(<DashboardHeader />);

    expect(screen.getByRole('banner')).toBeInTheDocument();
  });
});
