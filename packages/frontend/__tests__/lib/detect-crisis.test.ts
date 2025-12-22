import { describe, it, expect } from 'vitest';
import { detectCrisisKeywords, analyzeCrisisInTranscript, getCrisisDetectionSummary } from '@/lib/detect-crisis';
import { TranscriptEntry } from '@/types/transcript';

describe('detectCrisisKeywords', () => {
  describe('Direct crisis keywords', () => {
    it('should detect suicide keywords', () => {
      const testCases = [
        'I want to kill myself',
        'thinking about suicide',
        'I want to end my life',
        'considering ending it all',
        'I wish I were dead',
        'better off dead'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
        expect(result.matchedKeywords.length).toBeGreaterThan(0);
      });
    });

    it('should detect self-harm keywords', () => {
      const testCases = [
        'I want to hurt myself',
        'cutting myself',
        'self harm thoughts',
        'I keep harming myself'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
        expect(result.matchedKeywords.length).toBeGreaterThan(0);
      });
    });

    it('should detect method-specific keywords', () => {
      const testCases = [
        'I have a lot of pills saved up',
        'thinking about using a gun',
        'planning to overdose',
        'jumping off a bridge'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
        expect(result.matchedKeywords.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Word boundary matching', () => {
    it('should NOT detect keywords in middle of words', () => {
      const testCases = [
        'I massacred that exam', // contains 'suicide' but not as a word
        'The harming effects of stress', // 'harming' not 'harm'
        'Analyze this suicide prevention paper', // academic context
      ];

      // Note: Some of these might still trigger if they contain actual keywords
      // The point is word boundaries prevent partial matches
      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        // These specific examples shouldn't trigger
        expect(result.detected).toBe(false);
      });
    });

    it('should detect keywords with punctuation', () => {
      const testCases = [
        'I want to kill myself.',
        'Suicide, that\'s what I think about',
        '(I want to die)',
        'Kill myself!'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
      });
    });
  });

  describe('Negative context detection', () => {
    it('should NOT trigger on negative context phrases', () => {
      const testCases = [
        "I don't want to die",
        "I'm not suicidal",
        "I don't want to hurt myself",
        "I choose to live",
        "I'm seeking help"
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(false);
        expect(result.message).toContain('negative context');
      });
    });

    it('should trigger even with negative context if crisis keywords are present elsewhere', () => {
      const text = "I don't want to die but I want to kill myself";
      const result = detectCrisisKeywords(text);
      
      // This should still trigger because crisis language is present
      // even though negative context exists
      expect(result.detected).toBe(true);
    });
  });

  describe('Obfuscation handling', () => {
    it('should detect keywords with spaces (s u i c i d e)', () => {
      const testCases = [
        'I want to commit s u i c i d e',
        'thinking about k i l l i n g myself',
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
        expect(result.matchedKeywords.length).toBeGreaterThan(0);
      });
    });

    it('should detect keywords with asterisks', () => {
      const testCases = [
        'I want to s*icide',
        'thinking about k*lling myself',
        'd*e by suicide'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
      });
    });
  });

  describe('Case insensitivity', () => {
    it('should detect keywords regardless of case', () => {
      const testCases = [
        'I WANT TO KILL MYSELF',
        'Suicide is all I think about',
        'sUiCiDe',
        'SELF HARM'
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(true);
      });
    });
  });

  describe('False positives prevention', () => {
    it('should NOT trigger on general negative emotions without crisis keywords', () => {
      const testCases = [
        "I'm feeling really sad today",
        "I'm stressed about exams",
        "I feel depressed",
        "Everything is overwhelming",
        "I'm having a hard time"
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        expect(result.detected).toBe(false);
      });
    });

    it('should NOT trigger on academic or news discussions', () => {
      const testCases = [
        "We're studying suicide prevention in my psychology class",
        "Reading about mental health awareness",
        "Discussing crisis intervention methods"
      ];

      testCases.forEach(text => {
        const result = detectCrisisKeywords(text);
        // Academic discussion should not trigger (no first-person intent)
        expect(result.detected).toBe(false);
      });
    });
  });
});

describe('analyzeCrisisInTranscript', () => {
  const createTranscriptEntry = (speaker: 'user' | 'bot', text: string): TranscriptEntry => ({
    id: Math.random().toString(),
    timestamp: new Date(),
    speaker,
    text
  });

  it('should detect crisis in transcript with user messages', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('bot', 'How are you feeling today?'),
      createTranscriptEntry('user', 'Not good, I want to kill myself'),
      createTranscriptEntry('bot', 'I\'m concerned...')
    ];

    const result = analyzeCrisisInTranscript(transcript);
    expect(result.detected).toBe(true);
    expect(result.matchedKeywords.length).toBeGreaterThan(0);
  });

  it('should NOT detect crisis in empty transcript', () => {
    const result = analyzeCrisisInTranscript([]);
    expect(result.detected).toBe(false);
  });

  it('should NOT trigger on bot messages only', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('bot', 'If you\'re thinking about suicide, please call 988'),
      createTranscriptEntry('bot', 'Crisis resources are available')
    ];

    const result = analyzeCrisisInTranscript(transcript);
    expect(result.detected).toBe(false);
  });

  it('should analyze only user messages', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('user', 'I\'m feeling okay'),
      createTranscriptEntry('bot', 'What if you wanted to kill yourself?'), // Bot shouldn't trigger
      createTranscriptEntry('user', 'I wouldn\'t do that')
    ];

    const result = analyzeCrisisInTranscript(transcript);
    expect(result.detected).toBe(false);
  });

  it('should aggregate multiple crisis keywords across messages', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('user', 'I think about suicide sometimes'),
      createTranscriptEntry('bot', 'I hear you...'),
      createTranscriptEntry('user', 'And I hurt myself when I feel bad')
    ];

    const result = analyzeCrisisInTranscript(transcript);
    expect(result.detected).toBe(true);
    expect(result.matchedKeywords.length).toBeGreaterThan(1);
  });
});

describe('getCrisisDetectionSummary', () => {
  const createTranscriptEntry = (speaker: 'user' | 'bot', text: string): TranscriptEntry => ({
    id: Math.random().toString(),
    timestamp: new Date(),
    speaker,
    text
  });

  it('should return summary for detected crisis', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('user', 'I want to end my life')
    ];

    const summary = getCrisisDetectionSummary(transcript);
    expect(summary.crisisDetected).toBe(true);
    expect(summary.keywordCount).toBeGreaterThan(0);
    expect(summary.keywords.length).toBeGreaterThan(0);
    expect(summary.message).toContain('Crisis language detected');
  });

  it('should return summary for no crisis', () => {
    const transcript: TranscriptEntry[] = [
      createTranscriptEntry('user', 'I\'m feeling stressed about exams')
    ];

    const summary = getCrisisDetectionSummary(transcript);
    expect(summary.crisisDetected).toBe(false);
    expect(summary.keywordCount).toBe(0);
    expect(summary.keywords).toEqual([]);
    expect(summary.message).toContain('No crisis language detected');
  });

  it('should handle empty transcript', () => {
    const summary = getCrisisDetectionSummary([]);
    expect(summary.crisisDetected).toBe(false);
    expect(summary.keywordCount).toBe(0);
  });
});

describe('Edge cases', () => {
  it('should handle very long text', () => {
    const longText = 'I feel okay. '.repeat(100) + 'But sometimes I think about suicide.';
    const result = detectCrisisKeywords(longText);
    expect(result.detected).toBe(true);
  });

  it('should handle special characters', () => {
    const text = 'I want to k!ll myself!!!';
    const result = detectCrisisKeywords(text);
    // May or may not detect depending on obfuscation rules
    // This tests that it doesn't crash
    expect(result).toHaveProperty('detected');
  });

  it('should handle empty string', () => {
    const result = detectCrisisKeywords('');
    expect(result.detected).toBe(false);
  });

  it('should handle undefined/null gracefully', () => {
    // @ts-expect-error Testing runtime safety
    const result1 = detectCrisisKeywords(null);
    expect(result1.detected).toBe(false);

    // @ts-expect-error Testing runtime safety
    const result2 = detectCrisisKeywords(undefined);
    expect(result2.detected).toBe(false);
  });
});
