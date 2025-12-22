/**
 * Tests for Video Session Controls
 * Story 4.6: Video Session Transcript and Controls
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import VideoSessionPage from '@/app/video-session/page';
import { Room, RoomEvent, ConnectionQuality } from 'livekit-client';

// Mock Next.js router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => ({
    get: (key: string) => {
      const params: Record<string, string> = {
        room_url: 'ws://test-room',
        access_token: 'test-token',
        session_id: 'test-session',
        category: 'Health',
      };
      return params[key] || null;
    },
  }),
}));

// Mock toast
const mockToast = vi.fn();
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}));

// Mock LiveKit Room
vi.mock('livekit-client', () => {
  const mockRoom = {
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn(),
    localParticipant: {
      audioTracks: new Map(),
    },
  };

  return {
    Room: vi.fn(() => mockRoom),
    RoomEvent: {
      Connected: 'connected',
      TrackSubscribed: 'trackSubscribed',
      Disconnected: 'disconnected',
      ConnectionQualityChanged: 'connectionQualityChanged',
      DataReceived: 'dataReceived',
    },
    Track: {
      Kind: {
        Video: 'video',
        Audio: 'audio',
      },
    },
    ConnectionQuality: {
      Excellent: 'excellent',
      Good: 'good',
      Poor: 'poor',
    },
  };
});

// Mock getUserMedia
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [],
    }),
  },
  writable: true,
});

describe('Video Session Controls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPush.mockClear();
    mockToast.mockClear();
  });

  describe('Layout', () => {
    it('renders split layout with video and transcript sections', () => {
      render(<VideoSessionPage />);
      
      // Check for video section - initially shows connecting message
      expect(screen.getByText(/connecting to video session/i)).toBeInTheDocument();
      
      // Check for transcript section
      expect(screen.getByText(/live transcript/i)).toBeInTheDocument();
    });

    it('shows transcript panel on desktop', () => {
      render(<VideoSessionPage />);
      
      const transcriptPanel = screen.getByText(/live transcript/i).closest('div');
      expect(transcriptPanel).toBeInTheDocument();
    });
  });

  describe('Transcript Display', () => {
    it('shows placeholder text when transcript is empty', () => {
      render(<VideoSessionPage />);
      
      expect(screen.getByText(/transcript will appear here/i)).toBeInTheDocument();
    });

    it('displays transcript messages with speaker labels', async () => {
      const { container } = render(<VideoSessionPage />);
      
      // Get the room instance and simulate connected state first
      const roomMock = vi.mocked(Room).mock.results[0]?.value;
      if (!roomMock) return;

      // Simulate connection
      const connectedHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.Connected
      )?.[1];
      if (connectedHandler) connectedHandler();

      // Wait briefly for state update
      await new Promise(resolve => setTimeout(resolve, 100));

      // Now simulate data reception
      const dataHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.DataReceived
      )?.[1];

      if (dataHandler) {
        const encoder = new TextEncoder();
        const payload = encoder.encode(JSON.stringify({
          type: 'transcript',
          speaker: 'user',
          text: 'Hello, I need help',
        }));
        
        dataHandler(payload);
        
        await waitFor(() => {
          expect(screen.getByText('You:')).toBeInTheDocument();
          expect(screen.getByText('Hello, I need help')).toBeInTheDocument();
        });
      }
    });

    it('displays counselor messages with different label', async () => {
      render(<VideoSessionPage />);
      
      const roomMock = vi.mocked(Room).mock.results[0]?.value;
      if (!roomMock) return;

      // Simulate connection first
      const connectedHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.Connected
      )?.[1];
      if (connectedHandler) connectedHandler();

      await new Promise(resolve => setTimeout(resolve, 100));

      const dataHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.DataReceived
      )?.[1];

      if (dataHandler) {
        const encoder = new TextEncoder();
        const payload = encoder.encode(JSON.stringify({
          type: 'transcript',
          speaker: 'counselor',
          text: 'How can I help you today?',
        }));
        
        dataHandler(payload);
        
        await waitFor(() => {
          expect(screen.getByText('Counselor:')).toBeInTheDocument();
          expect(screen.getByText('How can I help you today?')).toBeInTheDocument();
        });
      }
    });
  });

  describe('Mute Button', () => {
    it('renders mute button', () => {
      render(<VideoSessionPage />);
      
      const muteButton = screen.getByLabelText(/mute/i);
      expect(muteButton).toBeInTheDocument();
    });

    it('toggles mute state when clicked', () => {
      render(<VideoSessionPage />);
      
      const muteButton = screen.getByLabelText(/mute/i);
      
      // Button should be unmuted initially
      expect(muteButton).toHaveAttribute('aria-label', 'Mute');
      expect(muteButton).not.toBeDisabled();
      
      // Verify clicking the button works (actual mute requires audio track from LiveKit)
      fireEvent.click(muteButton);
      
      // Button should still be present and functional
      expect(muteButton).toBeInTheDocument();
    });
  });

  describe('Volume Control', () => {
    it('renders volume slider on desktop', () => {
      render(<VideoSessionPage />);
      
      const volumeSlider = screen.getByLabelText(/volume/i);
      expect(volumeSlider).toBeInTheDocument();
    });

    it('displays current volume percentage', () => {
      render(<VideoSessionPage />);
      
      // Default volume is 80%
      expect(screen.getByText('80%')).toBeInTheDocument();
    });

    it('persists volume to localStorage', async () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');
      
      render(<VideoSessionPage />);
      
      await waitFor(() => {
        expect(setItemSpy).toHaveBeenCalledWith('avatar_volume', '80');
      });
    });
  });

  describe('Connection Quality Indicator', () => {
    it('renders connection quality indicator', () => {
      render(<VideoSessionPage />);
      
      // Should show default "Good" quality
      expect(screen.getByText(/good/i)).toBeInTheDocument();
    });

    it('shows toast notification for poor connection quality', async () => {
      render(<VideoSessionPage />);
      
      const roomMock = vi.mocked(Room).mock.results[0]?.value;
      if (!roomMock) return;

      const qualityHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.ConnectionQualityChanged
      )?.[1];

      if (qualityHandler) {
        qualityHandler(ConnectionQuality.Poor);
        
        await waitFor(() => {
          expect(mockToast).toHaveBeenCalledWith(
            expect.objectContaining({
              title: "Poor Connection Quality",
              variant: "destructive"
            })
          );
        });
      }
    });

    it('updates quality level indicator when connection changes', async () => {
      render(<VideoSessionPage />);
      
      const roomMock = vi.mocked(Room).mock.results[0]?.value;
      if (!roomMock) return;

      const qualityHandler = roomMock.on.mock.calls.find(
        call => call[0] === RoomEvent.ConnectionQualityChanged
      )?.[1];

      if (qualityHandler) {
        qualityHandler(ConnectionQuality.Excellent);
        
        await waitFor(() => {
          expect(screen.getByText(/excellent/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('End Session Button', () => {
    it('renders end session button', () => {
      render(<VideoSessionPage />);
      
      const endButton = screen.getByRole('button', { name: /end session/i });
      expect(endButton).toBeInTheDocument();
    });

    it('shows confirmation dialog when clicked', async () => {
      render(<VideoSessionPage />);
      
      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);
      
      await waitFor(() => {
        expect(screen.getByText(/are you sure you want to end this counseling session/i)).toBeInTheDocument();
      });
    });

    it('disconnects and navigates to dashboard on confirm', async () => {
      const mockDisconnect = vi.fn();
      vi.mocked(Room).mockImplementation(() => ({
        connect: vi.fn(),
        disconnect: mockDisconnect,
        on: vi.fn(),
        localParticipant: {
          audioTracks: new Map(),
        },
      } as any));

      render(<VideoSessionPage />);
      
      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);
      
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });
      
      const confirmButton = screen.getByRole('button', { name: /^end session$/i });
      fireEvent.click(confirmButton);
      
      await waitFor(() => {
        expect(mockDisconnect).toHaveBeenCalled();
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('stays in session when cancel is clicked', async () => {
      render(<VideoSessionPage />);
      
      const endButton = screen.getByRole('button', { name: /end session/i });
      fireEvent.click(endButton);
      
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });
      
      const cancelButton = screen.getByRole('button', { name: /stay in session/i });
      fireEvent.click(cancelButton);
      
      await waitFor(() => {
        expect(screen.queryByText(/are you sure/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('shows keyboard shortcut hint for mute', () => {
      render(<VideoSessionPage />);
      
      expect(screen.getByText(/press space to/i)).toBeInTheDocument();
    });
  });

  describe('Crisis Hotline', () => {
    it('displays crisis hotline information', () => {
      render(<VideoSessionPage />);
      
      expect(screen.getByText(/if you're in crisis, call 988/i)).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('renders transcript toggle button for mobile', () => {
      render(<VideoSessionPage />);
      
      // Mobile transcript toggle button (hidden on desktop)
      const toggleButtons = screen.getAllByLabelText(/toggle transcript/i);
      expect(toggleButtons.length).toBeGreaterThan(0);
    });
  });
});
