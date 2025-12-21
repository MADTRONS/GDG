import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import VoiceSessionPage from '@/app/voice-session/page';
import { useSearchParams, useRouter } from 'next/navigation';
import DailyIframe from '@daily-co/daily-js';
import { useToast } from '@/components/ui/use-toast';

// Mock dependencies
vi.mock('next/navigation', () => ({
  useSearchParams: vi.fn(),
  useRouter: vi.fn()
}));

vi.mock('@daily-co/daily-js', () => ({
  default: {
    createCallObject: vi.fn()
  }
}));

vi.mock('@/components/ui/use-toast', () => ({
  useToast: vi.fn()
}));

describe('VoiceSessionPage - Daily.co Connection', () => {
  const mockToast = vi.fn();
  const mockPush = vi.fn();
  const mockSearchParams = {
    get: vi.fn((key: string) => {
      const params: Record<string, string> = {
        room_url: 'https://test.daily.co/room',
        user_token: 'token-123',
        session_id: 'session-456',
        category: 'Health Counselor'
      };
      return params[key];
    })
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any);
    vi.mocked(useToast).mockReturnValue({ toast: mockToast } as any);
    
    // Mock getUserMedia
    Object.defineProperty(global.navigator, 'mediaDevices', {
      writable: true,
      value: {
        getUserMedia: vi.fn().mockResolvedValue({})
      }
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Parameter Validation', () => {
    it('redirects to dashboard when room_url is missing', async () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        const params: Record<string, string | null> = {
          user_token: 'token-123',
          session_id: 'session-456',
          category: 'Health Counselor'
        };
        return params[key] ?? null;
      });

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: "Invalid Session",
          description: "Missing required session parameters. Returning to dashboard.",
          variant: "destructive"
        });
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('redirects to dashboard when user_token is missing', async () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        const params: Record<string, string | null> = {
          room_url: 'https://test.daily.co/room',
          session_id: 'session-456',
          category: 'Health Counselor'
        };
        return params[key] ?? null;
      });

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('redirects to dashboard when session_id is missing', async () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        const params: Record<string, string | null> = {
          room_url: 'https://test.daily.co/room',
          user_token: 'token-123',
          category: 'Health Counselor'
        };
        return params[key] ?? null;
      });

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });
  });

  describe('Client Initialization', () => {
    it('initializes Daily call object with correct params', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(DailyIframe.createCallObject).toHaveBeenCalledWith({
          audioSource: true,
          videoSource: false
        });
      });

      expect(mockCallObject.join).toHaveBeenCalledWith({
        url: 'https://test.daily.co/room',
        token: 'token-123'
      });
    });

    it('shows connecting state initially', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/connecting to health counselor/i)).toBeInTheDocument();
      });
    });

    it('transitions to connected state on successful connection', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      expect(mockToast).toHaveBeenCalledWith({
        title: "Connected",
        description: "You're now connected to Health Counselor. Start speaking!"
      });
    });
  });

  describe('Microphone Permissions', () => {
    it('requests microphone permission on mount', async () => {
      const getUserMediaMock = vi.fn().mockResolvedValue({});
      global.navigator.mediaDevices.getUserMedia = getUserMediaMock;

      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(getUserMediaMock).toHaveBeenCalledWith({ audio: true });
      });
    });

    it('shows permission denied UI when microphone access is denied', async () => {
      global.navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(
        new Error('Permission denied')
      );

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/microphone access required/i)).toBeInTheDocument();
      });

      expect(mockToast).toHaveBeenCalledWith({
        title: "Microphone Required",
        description: "Please allow microphone access to join the voice session.",
        variant: "destructive"
      });
    });

    it('allows retry after permission denied', async () => {
      global.navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(
        new Error('Permission denied')
      );

      const reloadMock = vi.fn();
      Object.defineProperty(window, 'location', {
        writable: true,
        value: { reload: reloadMock }
      });

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/try again/i)).toBeInTheDocument();
      });

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);

      expect(reloadMock).toHaveBeenCalled();
    });
  });

  describe('Mute Functionality', () => {
    it('mutes microphone when mute button clicked', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      const muteButton = screen.getByRole('button', { name: /^mute$/i });
      fireEvent.click(muteButton);

      await waitFor(() => {
        expect(mockCallObject.setLocalAudio).toHaveBeenCalledWith(false);
      });
    });

    it('unmutes microphone when unmute button clicked', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      // Mute first
      const muteButton = screen.getByRole('button', { name: /^mute$/i });
      fireEvent.click(muteButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /unmute/i })).toBeInTheDocument();
      });

      // Then unmute
      const unmuteButton = screen.getByRole('button', { name: /unmute/i });
      fireEvent.click(unmuteButton);

      await waitFor(() => {
        expect(mockCallObject.setLocalAudio).toHaveBeenCalledWith(true);
      });
    });

    it('disables mute button when not connected', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        const muteButton = screen.getByRole('button', { name: /mute/i });
        expect(muteButton).toBeDisabled();
      });
    });
  });

  describe('Session End', () => {
    it('shows confirmation dialog when end session clicked', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);

      await waitFor(() => {
        expect(screen.getByText(/end voice session\?/i)).toBeInTheDocument();
      });
    });

    it('disconnects client and navigates to dashboard when confirmed', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      // Click end session
      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);

      await waitFor(() => {
        expect(screen.getByText(/end voice session\?/i)).toBeInTheDocument();
      });

      // Confirm in dialog
      const confirmButtons = screen.getAllByRole('button', { name: /end session/i });
      const confirmButton = confirmButtons[confirmButtons.length - 1]; // Get the dialog button
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(mockCallObject.leave).toHaveBeenCalled();
        expect(mockCallObject.destroy).toHaveBeenCalled();
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('cancels end session when cancel clicked', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'joined-meeting') {
            setTimeout(() => handler(), 0);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn(),
        setLocalAudio: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/^connected$/i)).toBeInTheDocument();
      });

      // Click end session
      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);

      await waitFor(() => {
        expect(screen.getByText(/end voice session\?/i)).toBeInTheDocument();
      });

      // Cancel
      const cancelButton = screen.getByRole('button', { name: /stay in session/i });
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText(/end voice session\?/i)).not.toBeInTheDocument();
      });

      expect(mockCallObject.leave).not.toHaveBeenCalled();
      expect(mockPush).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('shows error state when connection fails', async () => {
      const mockCallObject = {
        join: vi.fn().mockRejectedValue(new Error('Connection failed')),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/connection error/i)).toBeInTheDocument();
      });

      expect(mockToast).toHaveBeenCalledWith({
        title: "Connection Failed",
        description: "Connection failed",
        variant: "destructive"
      });
    });

    it('shows retry button on connection error', async () => {
      const mockCallObject = {
        join: vi.fn().mockRejectedValue(new Error('Connection failed')),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/retry connection/i)).toBeInTheDocument();
      });
    });

    it('reloads page when retry button clicked', async () => {
      const mockCallObject = {
        join: vi.fn().mockRejectedValue(new Error('Connection failed')),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      const reloadMock = vi.fn();
      Object.defineProperty(window, 'location', {
        writable: true,
        value: { reload: reloadMock }
      });

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/retry connection/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /retry connection/i });
      fireEvent.click(retryButton);

      expect(reloadMock).toHaveBeenCalled();
    });

    it('handles disconnection event', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn((event, handler) => {
          if (event === 'left-meeting') {
            setTimeout(() => handler(), 100);
          }
        }),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/disconnected/i)).toBeInTheDocument();
      }, { timeout: 2000 });
    });
  });

  describe('UI Elements', () => {
    it('displays session ID', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/session id: session-456/i)).toBeInTheDocument();
      });
    });

    it('displays crisis hotline information', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/988/i)).toBeInTheDocument();
      });
    });

    it('displays category name in title', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/voice session: health counselor/i)).toBeInTheDocument();
      });
    });

    it('defaults category to "Counselor" when not provided', async () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        const params: Record<string, string | null> = {
          room_url: 'https://test.daily.co/room',
          user_token: 'token-123',
          session_id: 'session-456'
        };
        return params[key] ?? null;
      });

      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(screen.getByText(/voice session: counselor/i)).toBeInTheDocument();
      });
    });
  });

  describe('Cleanup', () => {
    it('disconnects client on unmount', async () => {
      const mockCallObject = {
        join: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
        leave: vi.fn(),
        destroy: vi.fn()
      };

      vi.mocked(DailyIframe.createCallObject).mockReturnValue(mockCallObject as any);

      const { unmount } = render(<VoiceSessionPage />);

      await waitFor(() => {
        expect(mockCallObject.join).toHaveBeenCalled();
      });

      unmount();

      expect(mockCallObject.leave).toHaveBeenCalled();
      expect(mockCallObject.destroy).toHaveBeenCalled();
    });
  });
});
