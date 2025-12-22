export interface Session {
  session_id: string;
  counselor_category: string;
  counselor_icon: string;
  mode: 'voice' | 'video';
  started_at: string;
  ended_at: string;
  duration_seconds: number;
  transcript_preview: string;
  transcript?: TranscriptMessage[];
}

export interface TranscriptMessage {
  timestamp: string;
  speaker: 'user' | 'counselor';
  text: string;
}

export interface SessionsResponse {
  sessions: Session[];
  total_count: number;
  page: number;
  limit: number;
}
