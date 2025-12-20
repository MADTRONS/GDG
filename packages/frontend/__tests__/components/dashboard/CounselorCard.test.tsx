import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CounselorCard } from '@/components/dashboard/CounselorCard';
import type { CounselorCategory } from '@/lib/api';

const mockCategory: CounselorCategory = {
  id: 1,
  name: 'Health & Wellness',
  description: 'Mental health, stress management, and self-care support',
  icon_name: 'heart-pulse',
};

describe('CounselorCard', () => {
  it('should render category name and description', () => {
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    expect(screen.getByText('Mental health, stress management, and self-care support')).toBeInTheDocument();
  });

  it('should render Voice Call and Video Call buttons', () => {
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    expect(screen.getByRole('button', { name: /voice call/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /video call/i })).toBeInTheDocument();
  });

  it('should call onVoiceCall when Voice Call button is clicked', async () => {
    const user = userEvent.setup();
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    await user.click(screen.getByRole('button', { name: /voice call/i }));
    expect(onVoiceCall).toHaveBeenCalledTimes(1);
  });

  it('should call onVideoCall when Video Call button is clicked', async () => {
    const user = userEvent.setup();
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    await user.click(screen.getByRole('button', { name: /video call/i }));
    expect(onVideoCall).toHaveBeenCalledTimes(1);
  });

  it('should render icon with proper styling', () => {
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    const { container } = render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    // Icon should be rendered (lucide-react icons are SVG elements)
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThan(0);
    
    // Check that the category icon has proper classes
    const categoryIcon = container.querySelector('.lucide-heart-pulse');
    expect(categoryIcon).toBeTruthy();
  });

  it('should have proper accessibility attributes', () => {
    const onVoiceCall = vi.fn();
    const onVideoCall = vi.fn();

    render(
      <CounselorCard
        category={mockCategory}
        onVoiceCall={onVoiceCall}
        onVideoCall={onVideoCall}
      />
    );

    const voiceButton = screen.getByRole('button', { name: /voice call/i });
    const videoButton = screen.getByRole('button', { name: /video call/i });

    expect(voiceButton).toHaveAttribute('aria-label');
    expect(videoButton).toHaveAttribute('aria-label');
    expect(voiceButton.getAttribute('aria-label')).toContain('Health & Wellness');
    expect(videoButton.getAttribute('aria-label')).toContain('Health & Wellness');
  });
});
