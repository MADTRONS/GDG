import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createVoiceRoom, CreateVoiceRoomResponse } from '@/lib/api';

describe('Voice API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createVoiceRoom', () => {
    it('calls API with correct parameters', async () => {
      const mockResponse: CreateVoiceRoomResponse = {
        room_url: 'https://test.daily.co/room',
        user_token: 'token-123',
        room_name: 'room-test',
        session_id: 'session-456',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      const result = await createVoiceRoom(categoryId);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/voice/create-room'),
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({ counselor_category: categoryId })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('throws error on API failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' })
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';

      await expect(createVoiceRoom(categoryId)).rejects.toThrow('Server error');
    });

    it('throws generic error when detail not provided', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({})
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';

      await expect(createVoiceRoom(categoryId)).rejects.toThrow('Request failed');
    });

    it('handles 401 unauthorized', async () => {
      delete (global as any).window;
      (global as any).window = { location: { href: '' } };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' })
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';

      await expect(createVoiceRoom(categoryId)).rejects.toThrow();
      expect(window.location.href).toBe('/');
    });
  });
});
