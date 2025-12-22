import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createVideoRoom } from '@/lib/api';

describe('Video API', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('createVideoRoom', () => {
    it('makes POST request to /video/create-room endpoint', async () => {
      const mockResponse = {
        room_url: 'wss://livekit.example.com',
        access_token: 'token-123',
        room_name: 'room-test',
        session_id: 'session-456',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      const result = await createVideoRoom(categoryId);

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/video/create-room`,
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            counselor_category: categoryId
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('throws error when API request fails', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Room creation failed' })
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      
      await expect(createVideoRoom(categoryId)).rejects.toThrow('Room creation failed');
    });

    it('throws default error message when no detail provided', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        json: async () => ({})
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      
      await expect(createVideoRoom(categoryId)).rejects.toThrow('Request failed');
    });

    it('returns all expected fields in response', async () => {
      const mockResponse = {
        room_url: 'wss://livekit.example.com',
        access_token: 'token-123',
        room_name: 'room-test',
        session_id: 'session-456',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      const result = await createVideoRoom(categoryId);

      expect(result).toHaveProperty('room_url');
      expect(result).toHaveProperty('access_token');
      expect(result).toHaveProperty('room_name');
      expect(result).toHaveProperty('session_id');
    });

    it('includes credentials in request', async () => {
      const mockResponse = {
        room_url: 'wss://livekit.example.com',
        access_token: 'token-123',
        room_name: 'room-test',
        session_id: 'session-456',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const categoryId = '123e4567-e89b-12d3-a456-426614174000';
      await createVideoRoom(categoryId);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include'
        })
      );
    });
  });
});
