import { describe, it, expect } from 'vitest';
import { getIcon } from '@/lib/icons';
import { HeartPulse, Briefcase, GraduationCap, DollarSign, Users, Star, HelpCircle } from 'lucide-react';

describe('getIcon', () => {
  it('should return correct icon component for valid icon names', () => {
    expect(getIcon('heart-pulse')).toBe(HeartPulse);
    expect(getIcon('briefcase')).toBe(Briefcase);
    expect(getIcon('graduation-cap')).toBe(GraduationCap);
    expect(getIcon('dollar-sign')).toBe(DollarSign);
    expect(getIcon('users')).toBe(Users);
    expect(getIcon('star')).toBe(Star);
  });

  it('should return HelpCircle for unknown icon names', () => {
    expect(getIcon('unknown-icon')).toBe(HelpCircle);
    expect(getIcon('random')).toBe(HelpCircle);
    expect(getIcon('')).toBe(HelpCircle);
  });
});
