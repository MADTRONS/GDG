import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/components/auth/AuthProvider';
import SessionDetailPage from '../page';

// Mock modules
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  useParams: vi.fn(),
}));

vi.mock('@/components/auth/AuthProvider', () => ({
  useAuth: vi.fn(),
}));

vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

const mockSession = {
  session_id: '123e4567-e89b-12d3-a456-426614174000',
  counselor_category: 'Health',
  counselor_icon: '🏥',
  mode: 'voice' as const,
  started_at: '2025-12-20T10:00:00Z',
  ended_at: '2025-12-20T10:15:00Z',
  duration_seconds: 900,
  transcript: [
    {
      timestamp: '2025-12-20T10:00:00Z',
      speaker: 'user' as const,
      text: 'Hello, I need help with managing stress.',
    },
    {
      timestamp: '2025-12-20T10:00:15Z',
      speaker: 'counselor' as const,
      text: 'I understand. Let\'s talk about what\'s been stressing you out.',
    },
    {
      timestamp: '2025-12-20T10:01:00Z',
      speaker: 'user' as const,
      text: 'I have so many deadlines coming up.',
    },
  ],
  crisis_detected: false,
};

describe('SessionDetailPage', () => {
  const mockPush = vi.fn();
  const mockRouterValue = { push: mockPush };
  
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useRouter).mockReturnValue(mockRouterValue as any);
    delete (global as any).fetch; // Clear any previous fetch mocks
  });

  it('redirects to login if not authenticated', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login?redirect=/sessions');
    });
  });

  it('shows loading state while fetching', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: true,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    render(<SessionDetailPage />);

    // Check for loading spinner by class name
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('fetches and displays session details', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockSession,
    });
    global.fetch = fetchMock as any;

    render(<SessionDetailPage />);

    // Wait for fetch to be called
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    }, { timeout: 5000 });

    // Wait for content to appear
    await waitFor(() => {
      expect(screen.getByText('Health')).toBeInTheDocument();
    }, { timeout: 5000 });
    
    expect(screen.getByText(/December 20/i)).toBeInTheDocument();

    // Check session metadata
    expect(screen.getByText(/Duration:/i)).toBeInTheDocument();

    // Check transcript messages
    expect(screen.getByText('Hello, I need help with managing stress.')).toBeInTheDocument();
    expect(screen.getByText('I understand. Let\'s talk about what\'s been stressing you out.')).toBeInTheDocument();
    expect(screen.getByText('I have so many deadlines coming up.')).toBeInTheDocument();

    // Check speaker labels
    expect(screen.getAllByText('You')).toHaveLength(2); // Two user messages
    expect(screen.getAllByText('Counselor')).toHaveLength(1); // One counselor message
  });

  it('shows error for unauthorized access (403)', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'Unauthorized' }),
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /permission/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Return to Session History/i })).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('shows error for session not found (404)', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: 'non-existent-id',
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Session not found.' })).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByRole('button', { name: /Return to Session History/i })).toBeInTheDocument();
  });

  it('handles fetch errors gracefully', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Unable to load session details. Please try again.')).toBeInTheDocument();
    });
  });

  it('displays video session icon for video mode', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    const videoSession = { ...mockSession, mode: 'video' as const };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => videoSession,
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByLabelText('Video session')).toBeInTheDocument();
    });
  });

  it('displays voice session icon for voice mode', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockSession,
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByLabelText('Voice session')).toBeInTheDocument();
    });
  });

  it('shows empty state when no transcript available', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    const emptySession = { ...mockSession, transcript: [] };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => emptySession,
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('No transcript available for this session.')).toBeInTheDocument();
    });
  });

  it('navigates back to sessions when back button clicked', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockSession,
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Health')).toBeInTheDocument();
      expect(screen.getByText('Back to Sessions')).toBeInTheDocument();
    }, { timeout: 5000 });

    const backButton = screen.getByText('Back to Sessions').closest('button');
    backButton?.click();

    expect(mockPush).toHaveBeenCalledWith('/sessions');
  });

  it('formats duration correctly', async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 'user-1', username: 'testuser', is_blocked: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    vi.mocked(useParams).mockReturnValue({
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
    });

    // Test with 3665 seconds (61 minutes and 5 seconds)
    const longSession = { ...mockSession, duration_seconds: 3665 };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => longSession,
    });

    render(<SessionDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Health')).toBeInTheDocument();
      expect(screen.getByText(/Duration:/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    // Check that duration is displayed (the exact format may vary)
    const durationText = screen.getByText(/Duration:/i).parentElement;
    expect(durationText?.textContent).toContain('61m');
    expect(durationText?.textContent).toContain('5s');
  });

  describe('Download Transcript', () => {
    let createObjectURLMock: any;
    let revokeObjectURLMock: any;
    let clickMock: any;
    let mockToast: any;

    beforeEach(() => {
      // Mock URL.createObjectURL and URL.revokeObjectURL
      createObjectURLMock = vi.fn(() => 'blob:mock-url');
      revokeObjectURLMock = vi.fn();
      global.URL.createObjectURL = createObjectURLMock;
      global.URL.revokeObjectURL = revokeObjectURLMock;

      // Mock anchor element click
      clickMock = vi.fn();
      const originalCreateElement = document.createElement.bind(document);
      vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
        const element = originalCreateElement(tagName);
        if (tagName === 'a') {
          element.click = clickMock;
        }
        return element;
      });

      // Mock toast
      mockToast = vi.fn();
      vi.doMock('@/components/ui/use-toast', () => ({
        useToast: () => ({ toast: mockToast }),
      }));
    });

    it('displays download button on session detail page', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      expect(downloadButton).toBeInTheDocument();
      expect(downloadButton).toHaveAccessibleName('Download transcript as text file');
    });

    it('creates blob and triggers download when button clicked', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      fireEvent.click(downloadButton);

      // Verify blob was created
      expect(createObjectURLMock).toHaveBeenCalled();
      const blobArg = createObjectURLMock.mock.calls[0][0];
      expect(blobArg).toBeInstanceOf(Blob);
      expect(blobArg.type).toBe('text/plain;charset=utf-8');

      // Verify download was triggered
      expect(clickMock).toHaveBeenCalled();

      // Verify cleanup
      expect(revokeObjectURLMock).toHaveBeenCalledWith('blob:mock-url');
    });

    it('generates correct filename format', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      fireEvent.click(downloadButton);

      // Get the created anchor element
      const anchorElements = document.querySelectorAll('a[download]');
      const downloadAnchor = Array.from(anchorElements).find(
        (el) => (el as HTMLAnchorElement).download.startsWith('Session_')
      );

      expect(downloadAnchor).toBeDefined();
      expect((downloadAnchor as HTMLAnchorElement).download).toBe('Session_Health_2025-12-20.txt');
    });

    it('formats transcript content correctly', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      fireEvent.click(downloadButton);

      // Get blob content
      const blobArg = createObjectURLMock.mock.calls[0][0];
      const reader = new FileReader();
      
      return new Promise<void>((resolve) => {
        reader.onload = () => {
          const content = reader.result as string;

          // Verify header contains metadata
          expect(content).toContain('COUNSELING SESSION TRANSCRIPT');
          expect(content).toContain('Counselor Category: Health');
          expect(content).toContain('Session Mode: Voice Call');
          expect(content).toContain('Duration: 15m 0s');
          expect(content).toContain('Session ID: 123e4567-e89b-12d3-a456-426614174000');

          // Verify transcript contains messages
          expect(content).toContain('[10:00:00 AM] YOU:');
          expect(content).toContain('Hello, I need help with managing stress.');
          expect(content).toContain('[10:00:15 AM] COUNSELOR:');
          expect(content).toContain('I understand. Let\'s talk about what\'s been stressing you out.');
          expect(content).toContain('[10:01:00 AM] YOU:');
          expect(content).toContain('I have so many deadlines coming up.');

          resolve();
        };
        reader.readAsText(blobArg);
      });
    });

    it('handles empty transcript gracefully', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      const emptySession = { ...mockSession, transcript: [] };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => emptySession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      fireEvent.click(downloadButton);

      // Get blob content
      const blobArg = createObjectURLMock.mock.calls[0][0];
      const reader = new FileReader();
      
      return new Promise<void>((resolve) => {
        reader.onload = () => {
          const content = reader.result as string;

          // Verify header is still present
          expect(content).toContain('COUNSELING SESSION TRANSCRIPT');
          expect(content).toContain('Counselor Category: Health');

          // Verify empty transcript message
          expect(content).toContain('No transcript available for this session.');

          resolve();
        };
        reader.readAsText(blobArg);
      });
    });

    it('formats filename with spaces replaced by underscores', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      const sessionWithSpaces = { 
        ...mockSession, 
        counselor_category: 'Health and Wellness Counselor' 
      };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => sessionWithSpaces,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health and Wellness Counselor')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      fireEvent.click(downloadButton);

      const anchorElements = document.querySelectorAll('a[download]');
      const downloadAnchor = Array.from(anchorElements).find(
        (el) => (el as HTMLAnchorElement).download.startsWith('Session_')
      );

      expect((downloadAnchor as HTMLAnchorElement).download).toBe(
        'Session_Health_and_Wellness_Counselor_2025-12-20.txt'
      );
    });

    it('is keyboard accessible', async () => {
      vi.mocked(useAuth).mockReturnValue({
        user: { id: 'user-1', username: 'testuser', is_blocked: false },
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      vi.mocked(useParams).mockReturnValue({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockSession,
      });

      render(<SessionDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('Health')).toBeInTheDocument();
      });

      const downloadButton = screen.getByLabelText(/download transcript/i);
      
      // Button should be focusable
      downloadButton.focus();
      expect(document.activeElement).toBe(downloadButton);

      // Keyboard trigger (Enter key)
      fireEvent.keyDown(downloadButton, { key: 'Enter', code: 'Enter' });
      
      // Note: The actual click event is handled by the button component
      // We verify the button is accessible and can receive focus
    });
  });
});