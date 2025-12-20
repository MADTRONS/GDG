import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { CounselorCardGrid } from '@/components/dashboard/CounselorCardGrid';

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

beforeEach(() => {
  server.listen({ onUnhandledRequest: 'error' });
});
afterEach(() => {
  server.resetHandlers();
});
afterEach(() => {
  server.close();
});

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
    expect(consoleSpy).toHaveBeenCalledWith('Voice call initiated for:', 'Health & Wellness');

    // Click video call button
    const videoButtons = screen.getAllByRole('button', { name: /video call/i });
    await user.click(videoButtons[0]);
    expect(consoleSpy).toHaveBeenCalledWith('Video call initiated for:', 'Health & Wellness');

    consoleSpy.mockRestore();
  });
});
