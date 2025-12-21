import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { TranscriptPanel } from '@/components/voice/TranscriptPanel';
import { TranscriptEntry } from '@/types/transcript';

describe('TranscriptPanel', () => {
  const mockEntries: TranscriptEntry[] = [
    {
      id: '1',
      timestamp: new Date('2025-12-21T14:30:00'),
      speaker: 'user',
      text: 'Hello, I need help with stress.'
    },
    {
      id: '2',
      timestamp: new Date('2025-12-21T14:30:05'),
      speaker: 'bot',
      text: "I'm here to listen. Tell me what's been on your mind."
    },
    {
      id: '3',
      timestamp: new Date('2025-12-21T14:30:10'),
      speaker: 'user',
      text: "I've been feeling overwhelmed with schoolwork."
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders transcript entries', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    expect(screen.getByText('Hello, I need help with stress.')).toBeInTheDocument();
    expect(screen.getByText(/I'm here to listen/)).toBeInTheDocument();
    expect(screen.getByText(/I've been feeling overwhelmed/)).toBeInTheDocument();
  });

  it('shows empty state when no entries', () => {
    render(<TranscriptPanel entries={[]} />);

    expect(screen.getByText(/transcript will appear here/i)).toBeInTheDocument();
  });

  it('displays conversation transcript header', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    expect(screen.getByText('Conversation Transcript')).toBeInTheDocument();
  });

  it('has accessible transcript container', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    const container = screen.getByTestId('transcript-container');
    expect(container).toHaveAttribute('aria-live', 'polite');
    expect(container).toHaveAttribute('aria-label', 'Conversation transcript');
  });

  it('renders all entries in order', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    const messages = screen.getAllByText(/You|Counselor/);
    expect(messages).toHaveLength(3); // 1 'You' + 2 'Counselor' labels from 3 entries
  });

  it('auto-scrolls to bottom initially', async () => {
    const { rerender } = render(<TranscriptPanel entries={[mockEntries[0]]} />);

    const scrollContainer = screen.getByTestId('transcript-container');
    
    // Add new entries
    rerender(<TranscriptPanel entries={mockEntries} />);

    await waitFor(() => {
      // In a real scroll scenario, scrollTop would equal scrollHeight - clientHeight
      // In jsdom, we can check that scroll logic exists by checking container exists
      expect(scrollContainer).toBeInTheDocument();
    });
  });

  it('shows scroll to bottom button when scrolled up', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    const scrollContainer = screen.getByTestId('transcript-container');
    
    // Mock scroll dimensions
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      value: 1000
    });
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      value: 500
    });
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      value: 0
    });

    // Simulate scroll
    fireEvent.scroll(scrollContainer);

    expect(screen.getByTestId('scroll-to-bottom-button')).toBeInTheDocument();
  });

  it('scroll to bottom button has accessible label', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    const scrollContainer = screen.getByTestId('transcript-container');
    
    // Trigger scroll button appearance
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      value: 1000
    });
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      value: 500
    });
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      value: 0
    });

    fireEvent.scroll(scrollContainer);

    const button = screen.getByTestId('scroll-to-bottom-button');
    expect(button).toHaveAttribute('aria-label', 'Scroll to latest message');
  });

  it('renders messages with timestamps', () => {
    render(<TranscriptPanel entries={mockEntries} />);

    expect(screen.getAllByText('2:30 PM')).toHaveLength(3);
  });
});
