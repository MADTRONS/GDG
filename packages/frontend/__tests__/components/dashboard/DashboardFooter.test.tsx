import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardFooter } from '@/components/dashboard/DashboardFooter';

describe('DashboardFooter', () => {
  it('renders help and emergency links', () => {
    render(<DashboardFooter />);

    expect(screen.getByText(/help.*faq/i)).toBeInTheDocument();
    expect(screen.getByText(/emergency resources/i)).toBeInTheDocument();
    expect(screen.getByText(/988/)).toBeInTheDocument();
  });

  it('help link navigates to /help', () => {
    render(<DashboardFooter />);

    const helpLink = screen.getByText(/help.*faq/i);
    expect(helpLink).toHaveAttribute('href', '/help');
  });

  it('emergency link navigates to /emergency', () => {
    render(<DashboardFooter />);

    const emergencyLink = screen.getByText(/emergency resources/i);
    expect(emergencyLink).toHaveAttribute('href', '/emergency');
  });

  it('displays suicide prevention lifeline number', () => {
    render(<DashboardFooter />);

    expect(screen.getByText(/national suicide prevention lifeline.*988/i)).toBeInTheDocument();
  });

  it('has proper contentinfo role', () => {
    render(<DashboardFooter />);

    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });

  it('help link has descriptive aria-label', () => {
    render(<DashboardFooter />);

    const helpLink = screen.getByLabelText(/get help and frequently asked questions/i);
    expect(helpLink).toHaveAttribute('href', '/help');
  });

  it('emergency link has descriptive aria-label', () => {
    render(<DashboardFooter />);

    const emergencyLink = screen.getByLabelText(/access emergency resources/i);
    expect(emergencyLink).toHaveAttribute('href', '/emergency');
  });
});
