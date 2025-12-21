import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CounselorCardGrid } from '@/components/dashboard/CounselorCardGrid';
import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ui/use-toast';
import * as api from '@/lib/api';

vi.mock('@/components/auth/AuthProvider');
vi.mock('next/navigation');
vi.mock('@/components/ui/use-toast');
vi.mock('@/lib/api');

describe('CounselorCardGrid Voice Call Initiation', () => {
  const mockCategories = [
    {
      id: '123e4567-e89b-12d3-a456-426614174000',
      name: 'Health Counselor',
      description: 'Mental health support',
      icon_name: 'heart'
    },
    {
      id: '223e4567-e89b-12d3-a456-426614174001',
      name: 'Academic Counselor',
      description: 'Academic guidance',
      icon_name: 'book'
    }
  ];

  const mockPush = vi.fn();
  const mockToast = vi.fn();
  const mockUser = { id: 'user-123', username: 'testuser', is_blocked: false };

  beforeEach(() => {
    vi.clearAllMocks();
    
    vi.mocked(useRouter).mockReturnValue({ 
      push: mockPush,
      replace: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      refresh: vi.fn(),
      prefetch: vi.fn()
    } as any);

    vi.mocked(useToast).mockReturnValue({
      toast: mockToast,
      dismiss: vi.fn(),
      toasts: []
    } as any);

    vi.mocked(useAuth).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn()
    } as any);

    vi.mocked(api.getCategories).mockResolvedValue(mockCategories);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls API and navigates on successful voice call', async () => {
    const mockResponse = {
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      room_name: 'room-test',
      session_id: 'session-456',
    };

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/voice/create-room'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ counselor_category: mockCategories[0].id })
        })
      );
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining('/voice-session')
      );
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining('room_url=')
      );
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining('user_token=')
      );
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining('session_id=')
      );
    });
  });

  it('shows loading state during API call', async () => {
    global.fetch = vi.fn().mockImplementation(() => new Promise(() => {}));

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(voiceButtons[0]).toBeDisabled();
    });
  });

  it('shows error toast on API failure', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Room creation failed' })
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Connection Failed',
          variant: 'destructive'
        })
      );
    });
  });

  it('redirects to login if not authenticated', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn()
    } as any);

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Authentication Required'
        })
      );
      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });

  it('prevents duplicate simultaneous calls', async () => {
    global.fetch = vi.fn().mockImplementation(() => new Promise(() => {}));

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    
    fireEvent.click(voiceButtons[0]);
    fireEvent.click(voiceButtons[0]);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  it('includes retry button in error toast', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Server error' })
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          action: expect.anything()
        })
      );
    });
  });

  it('logs error details to console', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Test error' })
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Voice call initiation error:',
        expect.any(Error)
      );
    });

    consoleErrorSpy.mockRestore();
  });

  it('passes correct counselor category in request', async () => {
    const mockResponse = {
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      room_name: 'room-test',
      session_id: 'session-456',
    };

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Academic Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[1]); // Click second counselor

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          body: JSON.stringify({ counselor_category: mockCategories[1].id })
        })
      );
    });
  });

  it('includes category name in navigation URL', async () => {
    const mockResponse = {
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      room_name: 'room-test',
      session_id: 'session-456',
    };

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health Counselor')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByLabelText(/start voice call/i);
    fireEvent.click(voiceButtons[0]);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining('category=Health%20Counselor')
      );
    });
  });
});
