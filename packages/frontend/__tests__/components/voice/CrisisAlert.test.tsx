import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CrisisAlert } from '@/components/voice/CrisisAlert';

describe('CrisisAlert Component', () => {
  const mockOnDismiss = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window.open
    vi.stubGlobal('open', vi.fn());
    // Reset location.href
    delete (window as any).location;
    (window as any).location = { href: '' };
  });

  describe('Rendering', () => {
    it('should render crisis alert with 988 information', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      expect(screen.getByText('Crisis Support Available')).toBeInTheDocument();
      expect(screen.getByText(/If you're experiencing thoughts of suicide/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Call 988/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Chat online/i })).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
      expect(alert).toHaveAttribute('aria-atomic', 'true');
    });

    it('should display campus counseling and 911 info', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      expect(screen.getByText(/Campus Counseling Center/i)).toBeInTheDocument();
      expect(screen.getByText(/Emergency: 911/i)).toBeInTheDocument();
    });

    it('should render dismiss button', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /Dismiss alert/i });
      expect(dismissButton).toBeInTheDocument();
    });
  });

  describe('Call 988 functionality', () => {
    it('should initiate phone call on mobile devices', () => {
      // Mock mobile device
      Object.defineProperty(window, 'ontouchstart', { value: true, writable: true });

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const callButton = screen.getByRole('button', { name: /Call 988/i });
      fireEvent.click(callButton);

      expect(window.location.href).toBe('tel:988');
    });

    it('should open 988 website on desktop', () => {
      // Mock desktop device (no touch support)
      Object.defineProperty(window, 'ontouchstart', { value: undefined, writable: true });
      Object.defineProperty(navigator, 'maxTouchPoints', { value: 0, writable: true });

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const callButton = screen.getByRole('button', { name: /Call 988/i });
      fireEvent.click(callButton);

      expect(window.open).toHaveBeenCalledWith(
        'https://988lifeline.org/',
        '_blank',
        'noopener,noreferrer'
      );
    });

    it('should log analytics event when Call 988 clicked', () => {
      const consoleLogSpy = vi.spyOn(console, 'log');

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const callButton = screen.getByRole('button', { name: /Call 988/i });
      fireEvent.click(callButton);

      expect(consoleLogSpy).toHaveBeenCalledWith('[Crisis Alert] User clicked Call 988');
    });
  });

  describe('Chat Online functionality', () => {
    it('should open 988 chat in new window', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const chatButton = screen.getByRole('button', { name: /Chat online/i });
      fireEvent.click(chatButton);

      expect(window.open).toHaveBeenCalledWith(
        'https://988lifeline.org/chat/',
        '_blank',
        'noopener,noreferrer'
      );
    });

    it('should log analytics event when Chat Online clicked', () => {
      const consoleLogSpy = vi.spyOn(console, 'log');

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const chatButton = screen.getByRole('button', { name: /Chat online/i });
      fireEvent.click(chatButton);

      expect(consoleLogSpy).toHaveBeenCalledWith('[Crisis Alert] User clicked Chat Online');
    });
  });

  describe('Two-step dismissal', () => {
    it('should show confirmation message on first dismiss click', async () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /Dismiss alert/i });
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(screen.getByText(/Are you sure you want to dismiss this/i)).toBeInTheDocument();
      });

      // onDismiss should NOT be called yet
      expect(mockOnDismiss).not.toHaveBeenCalled();
    });

    it('should call onDismiss on second dismiss click', async () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /Dismiss alert/i });
      
      // First click
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(screen.getByText(/Yes, dismiss alert/i)).toBeInTheDocument();
      });

      // Second click on confirmation
      const confirmButton = screen.getByText(/Yes, dismiss alert/i);
      fireEvent.click(confirmButton);

      expect(mockOnDismiss).toHaveBeenCalledTimes(1);
    });

    it('should log dismissal event', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log');

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /Dismiss alert/i });
      
      // First click
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(screen.getByText(/Yes, dismiss alert/i)).toBeInTheDocument();
      });

      // Second click
      const confirmButton = screen.getByText(/Yes, dismiss alert/i);
      fireEvent.click(confirmButton);

      expect(consoleLogSpy).toHaveBeenCalledWith('[Crisis Alert] Alert dismissed by user');
    });
  });

  describe('Visual styling', () => {
    it('should have red background for prominence', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('bg-red-600');
    });

    it('should be fixed at top of viewport', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('fixed', 'top-0', 'left-0', 'right-0');
    });

    it('should have high z-index to appear above other content', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('z-50');
    });
  });

  describe('Icon rendering', () => {
    it('should render AlertTriangle icon', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      // AlertTriangle renders as svg with specific attributes
      const icons = document.querySelectorAll('svg');
      expect(icons.length).toBeGreaterThan(0);
    });

    it('should render Phone icon on Call button', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const callButton = screen.getByRole('button', { name: /Call 988/i });
      const icon = callButton.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should render ExternalLink icon on Chat button', () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const chatButton = screen.getByRole('button', { name: /Chat online/i });
      const icon = chatButton.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('should handle missing window object gracefully', () => {
      // Temporarily remove window
      const originalWindow = global.window;
      // @ts-expect-error Testing edge case
      delete global.window;

      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const callButton = screen.getByRole('button', { name: /Call 988/i });
      
      // Should not throw error
      expect(() => fireEvent.click(callButton)).not.toThrow();

      // Restore window
      global.window = originalWindow;
    });

    it('should handle rapid dismiss clicks', async () => {
      render(<CrisisAlert onDismiss={mockOnDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /Dismiss alert/i });
      
      // Rapid clicks
      fireEvent.click(dismissButton);
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(screen.getByText(/Yes, dismiss alert/i)).toBeInTheDocument();
      });

      // Should still only call onDismiss once
      const confirmButton = screen.getByText(/Yes, dismiss alert/i);
      fireEvent.click(confirmButton);

      expect(mockOnDismiss).toHaveBeenCalledTimes(1);
    });
  });
});
