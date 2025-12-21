export type SpeakerType = 'user' | 'bot';

export interface TranscriptEntry {
  id: string;
  timestamp: Date;
  speaker: SpeakerType;
  text: string;
}

