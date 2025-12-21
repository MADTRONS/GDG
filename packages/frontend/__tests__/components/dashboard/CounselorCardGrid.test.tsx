import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { CounselorCardGrid } from '@/components/dashboard/CounselorCardGrid';
import { Toaster } from '@/components/ui/toaster';
import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';

vi.mock('@/components/auth/AuthProvider');
vi.mock('next/navigation');

const mockCategories = [
  {
    id: 1,
    name: 'Health & Wellness',
    description: 'Mental health, stress management, and self-care support',
    icon_name: 'heart-pulse',
  },
  {
    id: 2,
    name: 'Career Development',
    description: 'Career planning, job search, and professional growth',
    icon_name: 'briefcase',
  },
  {
    id: 3,
    name: 'Academic Support',
    description: 'Study skills, time management, and academic success',
    icon_name: 'graduation-cap',
  },
];

const server = setupServer(
  http.get('http://localhost:8000/api/v1/counselors/categories', () => {
    return HttpResponse.json({
      categories: mockCategories,
      total: mockCategories.length,
    });
  })
);

const mockPush = vi.fn();
const mockUser = { id: 'user-123', username: 'testuser', is_blocked: false };

beforeEach(() => {
  server.listen({ onUnhandledRequest: 'error' });
  
  // Mock useAuth to return authenticated user
  vi.mocked(useAuth).mockReturnValue({
    user: mockUser,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn()
  } as any);
  
  // Mock useRouter
  vi.mocked(useRouter).mockReturnValue({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn()
  } as any);
});
afterEach(() => {
  server.resetHandlers();
});
afterEach(() => {
  server.close();
});

// Helper to render with toaster
const renderWithToaster = (component: React.ReactElement) => {
  return render(
    <>
      {component}
      <Toaster />
    </>
  );
};

describe('CounselorCardGrid', () => {
  it('should show loading skeleton cards initially', () => {
    render(<CounselorCardGrid />);
    
    const skeletons = screen.getAllByTestId('skeleton-card');
    expect(skeletons).toHaveLength(6);
  });

  it('should fetch and display counselor categories', async () => {
    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
      expect(screen.getByText('Career Development')).toBeInTheDocument();
      expect(screen.getByText('Academic Support')).toBeInTheDocument();
    });

    // Should render correct number of cards
    const cards = screen.getAllByRole('button', { name: /voice call/i });
    expect(cards).toHaveLength(mockCategories.length);
  });

  it('should display error message when fetch fails', async () => {
    server.use(
      http.get('http://localhost:8000/api/v1/counselors/categories', () => {
        return HttpResponse.json(
          { detail: 'Internal server error' },
          { status: 500 }
        );
      })
    );

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Error Loading Categories')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });
  });

  it('should retry fetching when Try Again button is clicked', async () => {
    const user = userEvent.setup();
    let callCount = 0;

    server.use(
      http.get('http://localhost:8000/api/v1/counselors/categories', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
          );
        }
        return HttpResponse.json({
          categories: mockCategories,
          total: mockCategories.length,
        });
      })
    );

    render(<CounselorCardGrid />);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText('Error Loading Categories')).toBeInTheDocument();
    });

    // Click retry button
    await user.click(screen.getByRole('button', { name: /try again/i }));

    // Should eventually show categories
    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    expect(callCount).toBe(2);
  });

  it('should log console messages when Voice/Video call buttons are clicked', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

    render(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    // Click voice call button
    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    await user.click(voiceButtons[0]);
    expect(consoleSpy).toHaveBeenCalledWith('Voice call requested for category:', 'Health & Wellness');
    expect(consoleSpy).toHaveBeenCalledWith('Category ID:', 1);

    // Click video call button
    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    await user.click(videoButtons[0]);
    expect(consoleSpy).toHaveBeenCalledWith('Video call requested for category:', 'Health & Wellness');
    expect(consoleSpy).toHaveBeenCalledWith('Category ID:', 1);

    consoleSpy.mockRestore();
  });

  it('should show toast notification when voice call button clicked', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    await user.click(voiceButtons[0]);

    // Check for toast notification
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
      expect(screen.getByText('Voice calling will be available in the next update. Stay tuned!')).toBeInTheDocument();
    });
  });

  it('should disable voice button during loading state', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const firstVoiceButton = voiceButtons[0];

    // Button should not be disabled initially
    expect(firstVoiceButton).not.toBeDisabled();

    // Click button
    await user.click(firstVoiceButton);

    // Button should be disabled
    await waitFor(() => {
      expect(firstVoiceButton).toBeDisabled();
    });

    // Button should show loading spinner
    const loader = firstVoiceButton.querySelector('.animate-spin');
    expect(loader).toBeInTheDocument();

    // Button should re-enable after timeout
    await waitFor(() => {
      expect(firstVoiceButton).not.toBeDisabled();
    }, { timeout: 5000 });
  });

  it('should prevent double-clicks on voice button', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const firstVoiceButton = voiceButtons[0];

    // Click twice rapidly
    await user.click(firstVoiceButton);
    
    // Try to click again while disabled
    await user.click(firstVoiceButton);

    // Should only log once (second click should be ignored because button is disabled)
    const voiceCallLogs = consoleSpy.mock.calls.filter(
      call => call[0] === 'Voice call requested for category:'
    );
    expect(voiceCallLogs).toHaveLength(1);

    consoleSpy.mockRestore();
  });

  it('should have independent loading states for each category card', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
      expect(screen.getByText('Career Development')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });

    // Click first button
    await user.click(voiceButtons[0]);

    // First button should be disabled
    await waitFor(() => {
      expect(voiceButtons[0]).toBeDisabled();
    });

    // Other buttons should still be enabled
    expect(voiceButtons[1]).not.toBeDisabled();
    expect(voiceButtons[2]).not.toBeDisabled();
  });

  it('should make voice button accessible via keyboard', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const firstVoiceButton = voiceButtons[0];

    // Focus button
    firstVoiceButton.focus();
    expect(firstVoiceButton).toHaveFocus();

    // Press Enter key
    await user.keyboard('{Enter}');

    // Toast should appear
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    });
  });

  it('should trigger voice button on Space key', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const firstVoiceButton = voiceButtons[0];

    // Focus button
    firstVoiceButton.focus();

    // Press Space key
    await user.keyboard(' ');

    // Toast should appear
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    });
  });

  // Video Call Tests
  it('should show toast notification when video call button clicked', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    await user.click(videoButtons[0]);

    // Check for toast notification
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
      expect(screen.getByText('Video calling will be available in the next update. Stay tuned!')).toBeInTheDocument();
    });
  });

  it('should disable video button during loading state', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    const firstVideoButton = videoButtons[0];

    // Button should not be disabled initially
    expect(firstVideoButton).not.toBeDisabled();

    // Click button
    await user.click(firstVideoButton);

    // Button should be disabled
    await waitFor(() => {
      expect(firstVideoButton).toBeDisabled();
    });

    // Button should show loading spinner
    const loader = firstVideoButton.querySelector('.animate-spin');
    expect(loader).toBeInTheDocument();

    // Button should re-enable after timeout
    await waitFor(() => {
      expect(firstVideoButton).not.toBeDisabled();
    }, { timeout: 5000 });
  });

  it('should prevent double-clicks on video button', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    const firstVideoButton = videoButtons[0];

    // Click twice rapidly
    await user.click(firstVideoButton);
    
    // Try to click again while disabled
    await user.click(firstVideoButton);

    // Should only log once (second click should be ignored because button is disabled)
    const videoCallLogs = consoleSpy.mock.calls.filter(
      call => call[0] === 'Video call requested for category:'
    );
    expect(videoCallLogs).toHaveLength(1);

    consoleSpy.mockRestore();
  });

  it('should make video button accessible via keyboard', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    const firstVideoButton = videoButtons[0];

    // Focus button
    firstVideoButton.focus();
    expect(firstVideoButton).toHaveFocus();

    // Press Enter key
    await user.keyboard('{Enter}');

    // Toast should appear
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    });
  });

  it('should trigger video button on Space key', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    const firstVideoButton = videoButtons[0];

    // Focus button
    firstVideoButton.focus();

    // Press Space key
    await user.keyboard(' ');

    // Toast should appear
    await waitFor(() => {
      expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    });
  });

  it('should have independent loading states for voice and video buttons', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const videoButtons = screen.getAllByRole('button', { name: /video call/i });

    // Click voice button
    await user.click(voiceButtons[0]);

    // Voice should be disabled, video should still be enabled
    await waitFor(() => {
      expect(voiceButtons[0]).toBeDisabled();
    });
    expect(videoButtons[0]).not.toBeDisabled();
  });

  it('should allow clicking video on different cards independently', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
      expect(screen.getByText('Career Development')).toBeInTheDocument();
    });

    const videoButtons = screen.getAllByRole('button', { name: /video call/i });

    // Click first card's video button
    await user.click(videoButtons[0]);

    // First button should be disabled
    await waitFor(() => {
      expect(videoButtons[0]).toBeDisabled();
    });

    // Other buttons should still be enabled
    expect(videoButtons[1]).not.toBeDisabled();
    expect(videoButtons[2]).not.toBeDisabled();
  });

  it('should allow both voice and video on same card sequentially', async () => {
    const user = userEvent.setup();

    renderWithToaster(<CounselorCardGrid />);

    await waitFor(() => {
      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    const voiceButtons = screen.getAllByRole('button', { name: /voice call/i });
    const videoButtons = screen.getAllByRole('button', { name: /video call/i });

    // Click voice
    await user.click(voiceButtons[0]);
    await waitFor(() => {
      expect(screen.getByText('Voice calling will be available in the next update. Stay tuned!')).toBeInTheDocument();
    });

    // Wait for voice loading to clear
    await waitFor(() => {
      expect(voiceButtons[0]).not.toBeDisabled();
    }, { timeout: 5000 });

    // Click video
    await user.click(videoButtons[0]);
    await waitFor(() => {
      expect(screen.getByText('Video calling will be available in the next update. Stay tuned!')).toBeInTheDocument();
    });
  });
});
