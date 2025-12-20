import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiRequest } from '@/lib/api';

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
    delete (window as any).location;
    window.location = { href: '' } as any;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('includes credentials in requests', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'test' }),
    });
    global.fetch = mockFetch;

    await apiRequest('/test');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/test'),
      expect.objectContaining({ credentials: 'include' })
    );
  });

  it('includes content-type header', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'test' }),
    });
    global.fetch = mockFetch;

    await apiRequest('/test');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('redirects to login on 401 response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    });
    global.fetch = mockFetch;

    await expect(apiRequest('/test')).rejects.toThrow();
    expect(window.location.href).toBe('/');
  });

  it('throws error on failed request', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Bad request' }),
    });
    global.fetch = mockFetch;

    await expect(apiRequest('/test')).rejects.toThrow('Bad request');
  });

  it('handles network errors', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));
    global.fetch = mockFetch;

    await expect(apiRequest('/test')).rejects.toThrow('Network error');
  });

  it('merges custom headers with defaults', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'test' }),
    });
    global.fetch = mockFetch;

    await apiRequest('/test', {
      headers: {
        'X-Custom-Header': 'value',
      },
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'X-Custom-Header': 'value',
        }),
      })
    );
  });

  it('uses correct API base URL', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'test' }),
    });
    global.fetch = mockFetch;

    await apiRequest('/auth/me');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/auth/me'),
      expect.any(Object)
    );
  });
});
