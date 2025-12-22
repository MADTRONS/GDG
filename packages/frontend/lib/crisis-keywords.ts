/**
 * Crisis detection keyword lists for safety monitoring.
 * 
 * IMPORTANT: This is a safety net, not clinical monitoring.
 * False positives are acceptable to avoid missing true crises.
 */

export const CRISIS_KEYWORDS = [
  // Direct suicidal ideation
  'suicide',
  'suicidal',
  'kill myself',
  'killing myself',
  'end my life',
  'ending my life',
  'want to die',
  'wish I was dead',
  'wish I were dead',
  'better off dead',
  'take my own life',
  'end it all',
  'no reason to live',
  "can't go on",
  'cannot go on',
  'nothing to live for',
  
  // Self-harm
  'self harm',
  'self-harm',
  'hurt myself',
  'hurting myself',
  'cut myself',
  'cutting myself',
  'harm myself',
  'harming myself',
  
  // Methods (sensitive but necessary for detection)
  'overdose',
  'jump off',
  'hang myself',
  'hanging myself',
  
  // Variations/obfuscations
  'sui cide', // common obfuscation with space
  's*icide',
  'k*ll myself',
  'unalive', // internet slang for suicide
  'unalive myself',
  
  // Crisis phrases
  'goodbye forever',
  'final goodbye',
  'this is the end',
  "can't take it anymore",
  'cannot take it anymore',
  'world is better without me',
  'everyone would be better off',
  'people would be better without me',
  'no point in living',
  'ready to die',
  'plan to die',
  'planning to die'
] as const;

/**
 * Positive context phrases that should NOT trigger detection.
 * These indicate the person is expressing resilience or declining suicidal thoughts.
 */
export const NEGATIVE_CONTEXT_PHRASES = [
  "don't want to die",
  'do not want to die',
  'not suicidal',
  "won't kill myself",
  'will not kill myself',
  'never hurt myself',
  'choose to live',
  'want to live',
  'reasons to live',
  'not thinking about suicide',
  'not planning to hurt',
  'getting help'
] as const;
