import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TranscriptMessage } from '@/components/voice/TranscriptMessage';
import { TranscriptEntry } from '@/types/transcript';

describe('TranscriptMessage', () => {
  const mockUserEntry: TranscriptEntry = {
    id: '1',
    timestamp: new Date('2025-12-21T14:30:00'),
    speaker: 'user',
    text: 'Hello, I need help with stress management.'
  };

  const mockBotEntry: TranscriptEntry = {
    id: '2',
    timestamp: new Date('2025-12-21T14:30:05'),
    speaker: 'bot',
    text: "I'm here to listen. Tell me what's been on your mind."
  };

  it('renders user message with correct label', () => {
    render(<TranscriptMessage entry={mockUserEntry} />);
    
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText('Hello, I need help with stress management.')).toBeInTheDocument();
  });

  it('renders bot message with correct label', () => {
    render(<TranscriptMessage entry={mockBotEntry} />);
    
    expect(screen.getByText('Counselor')).toBeInTheDocument();
    expect(screen.getByText(/I'm here to listen/)).toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    render(<TranscriptMessage entry={mockUserEntry} />);
    
    // Timestamp should be formatted as "h:mm a" (e.g., "2:30 PM")
    expect(screen.getByText('2:30 PM')).toBeInTheDocument();
  });

  it('applies different styling for user vs bot messages', () => {
    const { container: userContainer } = render(<TranscriptMessage entry={mockUserEntry} />);
    const { container: botContainer } = render(<TranscriptMessage entry={mockBotEntry} />);
    
    // User messages should have different class than bot messages
    const userMessage = userContainer.querySelector('[data-testid="transcript-message-user"]');
    const botMessage = botContainer.querySelector('[data-testid="transcript-message-bot"]');
    
    expect(userMessage).toBeInTheDocument();
    expect(botMessage).toBeInTheDocument();
    expect(userMessage?.className).not.toBe(botMessage?.className);
  });

  it('has readable text size', () => {
    const { container } = render(<TranscriptMessage entry={mockUserEntry} />);
    
    const textElement = screen.getByText('Hello, I need help with stress management.');
    const computedStyle = window.getComputedStyle(textElement);
    
    // Should have base text size class (16px+)
    expect(textElement.className).toContain('text-base');
  });
});
