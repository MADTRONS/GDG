import { Track } from 'livekit-client';

export type ConnectionState = 'idle' | 'connecting' | 'connected' | 'waiting_avatar' | 'disconnected' | 'error';

export interface VideoSessionParams {
  room_url: string;
  access_token: string;
  session_id: string;
  category: string;
}

export interface AvatarTrack {
  video: MediaStreamTrack | null;
  audio: MediaStreamTrack | null;
}
