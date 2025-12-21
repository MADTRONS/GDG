export type ConnectionState = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';

export interface VoiceSessionParams {
  room_url: string;
  user_token: string;
  session_id: string;
  category: string;
}

export interface RTVIClientConfig {
  transport: any;
  params: {
    baseUrl: string;
    token: string;
    enableMic: boolean;
    enableCam: boolean;
  };
  timeout: number;
}
