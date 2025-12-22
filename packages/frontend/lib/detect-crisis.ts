/**
 * Crisis detection utility for monitoring conversation content.
 * 
 * This implements keyword-based detection to identify when users may be
 * in crisis or expressing thoughts of self-harm.
 */

import { CRISIS_KEYWORDS, NEGATIVE_CONTEXT_PHRASES } from './crisis-keywords';
import { TranscriptEntry } from '@/types/transcript';

export interface CrisisDetectionResult {
  detected: boolean;
  matchedKeywords: string[];
  message: string;
}

export interface CrisisDetectionSummary {
  crisisDetected: boolean;
  keywordCount: number;
  keywords: string[];
  message: string;
}

/**
 * Detect crisis keywords in a message.
 * 
 * Uses word boundary matching to avoid false positives from partial words.
 * Checks for negative context (e.g., "don't want to die") to reduce false positives.
 * 
 * @param message - The message text to analyze
 * @returns CrisisDetectionResult with detection status and matched keywords
 * 
 * @example
 * detectCrisisKeywords("I am thinking about suicide")
 * // => { detected: true, matchedKeywords: ["suicide"], message: "..." }
 * 
 * detectCrisisKeywords("I don't want to die")
 * // => { detected: false, matchedKeywords: [], message: "..." }
 */
export function detectCrisisKeywords(message: string): CrisisDetectionResult {
  // Handle null/undefined/non-string input
  if (!message || typeof message !== 'string') {
    return {
      detected: false,
      matchedKeywords: [],
      message: 'No crisis language detected (empty message)'
    };
  }

  const normalizedMessage = message.toLowerCase().trim();
  
  // First, check for negative context (phrases that indicate safety)
  const hasNegativeContext = NEGATIVE_CONTEXT_PHRASES.some(phrase => 
    normalizedMessage.includes(phrase.toLowerCase())
  );
  
  if (hasNegativeContext) {
    return {
      detected: false,
      matchedKeywords: [],
      message: 'No crisis detected - negative context present'
    };
  }
  
  // Check for crisis keywords
  const matchedKeywords: string[] = [];
  
  for (const keyword of CRISIS_KEYWORDS) {
    const normalizedKeyword = keyword.toLowerCase();
    
    // For phrases (contains space), do exact phrase matching
    if (keyword.includes(' ')) {
      if (normalizedMessage.includes(normalizedKeyword)) {
        matchedKeywords.push(keyword);
      }
    } else {
      // For single words, use word boundary matching to avoid partial matches
      // \b matches word boundaries (transition between \w and \W)
      const pattern = new RegExp(`\\b${normalizedKeyword}\\b`, 'i');
      if (pattern.test(normalizedMessage)) {
        matchedKeywords.push(keyword);
      }
    }
  }
  
  if (matchedKeywords.length > 0) {
    return {
      detected: true,
      matchedKeywords,
      message: `Crisis language detected: ${matchedKeywords.join(', ')}`
    };
  }
  
  return {
    detected: false,
    matchedKeywords: [],
    message: 'No crisis language detected'
  };
}

/**
 * Analyze transcript entries for crisis content.
 * Only analyzes user messages, not bot responses.
 * 
 * @param transcript - Array of transcript entries to analyze
 * @returns CrisisDetectionResult with aggregated results
 * 
 * @example
 * analyzeCrisisInTranscript([
 *   { speaker: 'user', text: 'I want to end it all', ... },
 *   { speaker: 'bot', text: 'I understand...', ... }
 * ])
 * // => { detected: true, matchedKeywords: ['end it all'], message: '...' }
 */
export function analyzeCrisisInTranscript(transcript: TranscriptEntry[]): CrisisDetectionResult {
  // Handle empty transcript
  if (!transcript || transcript.length === 0) {
    return {
      detected: false,
      matchedKeywords: [],
      message: 'No crisis language detected (empty transcript)'
    };
  }

  // Only analyze user messages, not bot responses
  const userMessages = transcript
    .filter(entry => entry.speaker === 'user')
    .map(entry => entry.text);
  
  // Aggregate all matched keywords across all user messages
  const allMatchedKeywords: string[] = [];
  
  for (const message of userMessages) {
    const result = detectCrisisKeywords(message);
    if (result.detected) {
      allMatchedKeywords.push(...result.matchedKeywords);
    }
  }
  
  // Remove duplicates
  const uniqueKeywords = [...new Set(allMatchedKeywords)];
  
  if (uniqueKeywords.length > 0) {
    return {
      detected: true,
      matchedKeywords: uniqueKeywords,
      message: `Crisis language detected in ${allMatchedKeywords.length} instance(s): ${uniqueKeywords.join(', ')}`
    };
  }
  
  return {
    detected: false,
    matchedKeywords: [],
    message: 'No crisis language detected in transcript'
  };
}

/**
 * Get a summary of crisis detection results for a transcript.
 * Includes keyword count and detailed message.
 * 
 * @param transcript - Array of transcript entries to analyze
 * @returns CrisisDetectionSummary with detailed metrics
 */
export function getCrisisDetectionSummary(transcript: TranscriptEntry[]): CrisisDetectionSummary {
  const analysis = analyzeCrisisInTranscript(transcript);
  
  return {
    crisisDetected: analysis.detected,
    keywordCount: analysis.matchedKeywords.length,
    keywords: analysis.matchedKeywords,
    message: analysis.message
  };
}

