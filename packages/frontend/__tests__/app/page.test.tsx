import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useSearchParams } from 'next/navigation';
import { useToast } from '@/components/ui/use-toast';
import Home from '@/app/page';

vi.mock('next/navigation', () => ({
  useSearchParams: vi.fn(),
}));

vi.mock('@/components/auth/LoginForm', () => ({
  LoginForm: () => <div data-testid="login-form">Login Form</div>,
}));

vi.mock('@/components/ui/use-toast');

describe('Login Page (Home)', () => {
  const mockToast = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window.history.replaceState
    global.window.history.replaceState = vi.fn();
    
    // Default mock for useToast
    vi.mocked(useToast).mockReturnValue({
      toast: mockToast,
      dismiss: vi.fn(),
      toasts: [],
    });
  });

  it('renders login form', () => {
    vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams('') as any);

    render(<Home />);

    expect(screen.getByTestId('login-form')).toBeInTheDocument();
  });

  it('shows logout message when logout param is true', async () => {
    vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams('logout=true') as any);

    render(<Home />);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Logged Out",
        description: "You have been logged out.",
        duration: 3000,
      });
    });

    // Should clear URL parameter
    expect(window.history.replaceState).toHaveBeenCalledWith({}, '', '/');
  });

  it('does not show logout message on normal load', () => {
    vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams('') as any);

    render(<Home />);

    expect(mockToast).not.toHaveBeenCalled();
  });

  it('does not show message when logout param is false', () => {
    vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams('logout=false') as any);

    render(<Home />);

    expect(mockToast).not.toHaveBeenCalled();
  });
});
