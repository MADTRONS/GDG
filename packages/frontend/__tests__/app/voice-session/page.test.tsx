import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import VoiceSessionPage from '@/app/voice-session/page';
import { useSearchParams } from 'next/navigation';

vi.mock('next/navigation', () => ({
  useSearchParams: vi.fn()
}));

describe('VoiceSessionPage', () => {
  it('displays session parameters when all are provided', async () => {
    const mockSearchParams = new URLSearchParams({
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      session_id: 'session-456',
      category: 'Health Counselor'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    expect(screen.getByText(/Voice Session: Health Counselor/i)).toBeInTheDocument();
    expect(screen.getByText(/Room URL: https:\/\/test.daily.co\/room/i)).toBeInTheDocument();
    expect(screen.getByText(/Session ID: session-456/i)).toBeInTheDocument();
  });

  it('shows error when room_url is missing', async () => {
    const mockSearchParams = new URLSearchParams({
      user_token: 'token-123',
      session_id: 'session-456'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    expect(screen.getByText(/Invalid session parameters/i)).toBeInTheDocument();
  });

  it('shows error when user_token is missing', async () => {
    const mockSearchParams = new URLSearchParams({
      room_url: 'https://test.daily.co/room',
      session_id: 'session-456'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    expect(screen.getByText(/Invalid session parameters/i)).toBeInTheDocument();
  });

  it('shows error when session_id is missing', async () => {
    const mockSearchParams = new URLSearchParams({
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    expect(screen.getByText(/Invalid session parameters/i)).toBeInTheDocument();
  });

  it('shows placeholder message for Story 3.4', async () => {
    const mockSearchParams = new URLSearchParams({
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      session_id: 'session-456',
      category: 'Health Counselor'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    expect(screen.getByText(/Story 3.4 will implement RTVIClient connection here/i)).toBeInTheDocument();
  });

  it('handles missing category gracefully', async () => {
    const mockSearchParams = new URLSearchParams({
      room_url: 'https://test.daily.co/room',
      user_token: 'token-123',
      session_id: 'session-456'
    });

    vi.mocked(useSearchParams).mockReturnValue(mockSearchParams as any);

    render(<VoiceSessionPage />);

    // Should still render the page, just without category name
    expect(screen.getByText(/Voice Session:/i)).toBeInTheDocument();
  });
});
