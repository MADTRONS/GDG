# Crisis Detection and Emergency Response Protocol

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Complete  
**Priority:** CRITICAL - Safety Feature  
**Related Requirements:** PRD FR20, NFR8 (FERPA)

---

## Overview

This protocol defines the crisis detection system for identifying students in distress during counseling sessions and immediately connecting them with appropriate emergency resources. The system is designed to balance **rapid response** for genuine emergencies with **minimal false positives** to avoid unnecessary disruption of helpful counseling conversations.

**Key Principles:**
1. **Safety First:** When in doubt, trigger the alert
2. **Privacy Preserved:** Crisis detection is logged separately and flagged for human review
3. **Non-Disruptive:** Continue the session while displaying resources
4. **Clear Action Path:** Provide specific next steps, not just hotline numbers

---

## Crisis Detection Methodology

### Two-Tier Detection System

**Tier 1: Keyword-Based (Immediate Trigger)**
- High-risk keywords/phrases trigger instant alert
- Processed in real-time during transcription
- No AI interpretation - direct string matching with context awareness

**Tier 2: LLM-Based Semantic Analysis (Secondary Check)**
- LLM evaluates conversation context for non-explicit crisis indicators
- Triggered every 5 conversation turns
- Catches subtle patterns (e.g., prolonged hopelessness, isolation)

---

## Crisis Keyword Dictionary

### Critical Keywords (Immediate Alert)

**Self-Harm & Suicide:**
```
- suicide
- kill myself
- end my life
- want to die
- not worth living
- better off dead
- suicide plan
- end it all
- self-harm
- cut myself
- hurt myself
- overdose
- hanging
- jump off
```

**Abuse & Violence:**
```
- being abused
- sexually assaulted
- raped
- domestic violence
- hitting me
- threatening me
- scared for my safety
- stalking me
```

**Substance Abuse (Immediate Danger):**
```
- overdosed
- too many pills
- mixed alcohol and
- can't stop drinking
- using every day
```

### Context-Sensitive Keywords (Require Phrase Analysis)

These keywords trigger alerts ONLY when combined with distress indicators:

**Depression Indicators (when combined with intensity words):**
```
- depression (+ "can't cope", "unbearable", "no point")
- hopeless (+ "always", "never", "forever")
- empty (+ "completely", "totally", "nothing left")
```

**Isolation Indicators (when combined with duration):**
```
- alone (+ "weeks", "months", "nobody")
- no friends (+ "never", "anywhere", "completely")
```

### False Positive Prevention

**Excluded Contexts:**
- Academic discussions: "studying suicide prevention", "reading about"
- Past tense without current distress: "used to feel", "had thought about"
- Hypothetical: "what if someone", "if a friend"
- Media references: "watched a movie about", "read an article"

**Implementation:**
Use 5-word context window before and after keyword. Apply exclusion rules before triggering alert.

---

## LLM Semantic Analysis Prompt

**Trigger Frequency:** Every 5 conversation turns (approximately every 2-3 minutes)

**System Prompt for Crisis Detection:**
```
You are a crisis detection system analyzing a counseling conversation for signs of immediate danger.

ANALYZE THE LAST 5 EXCHANGES for these indicators:

CRITICAL INDICATORS (Report Immediately):
1. Explicit suicidal ideation or plans
2. Self-harm behaviors or intentions
3. Disclosure of abuse or assault
4. Immediate danger to self or others
5. Substance abuse emergency

CONCERNING PATTERNS (Report if multiple present):
- Persistent hopelessness spanning multiple turns
- Escalating emotional distress without relief
- Withdrawal and severe isolation
- Rejection of all coping strategies
- Fixation on single catastrophic problem

RESPOND IN JSON FORMAT ONLY:
{
  "crisis_detected": true/false,
  "severity": "critical" | "concerning" | "none",
  "indicators": ["list of detected patterns"],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}

CRITICAL: Only flag "crisis_detected": true if there is immediate danger or explicit distress signals. Do not over-flag normal counseling conversations about challenges.
```

---

## Emergency Resources Configuration

### National Resources (Always Display)

```json
[
  {
    "id": "nspl",
    "name": "988 Suicide & Crisis Lifeline",
    "phone": "988",
    "text": "Text 988",
    "url": "https://988lifeline.org",
    "available": "24/7",
    "description": "Free, confidential support for people in distress",
    "priority": 1
  },
  {
    "id": "crisis_text",
    "name": "Crisis Text Line",
    "phone": null,
    "text": "Text HOME to 741741",
    "url": "https://www.crisistextline.org",
    "available": "24/7",
    "description": "Text-based crisis support",
    "priority": 2
  },
  {
    "id": "trevor",
    "name": "The Trevor Project (LGBTQ+)",
    "phone": "1-866-488-7386",
    "text": "Text START to 678678",
    "url": "https://www.thetrevorproject.org",
    "available": "24/7",
    "description": "LGBTQ+ youth crisis support",
    "priority": 3
  },
  {
    "id": "rainn",
    "name": "RAINN Sexual Assault Hotline",
    "phone": "1-800-656-4673",
    "text": null,
    "url": "https://www.rainn.org",
    "available": "24/7",
    "description": "Support for sexual assault survivors",
    "priority": 4
  },
  {
    "id": "samhsa",
    "name": "SAMHSA Substance Abuse Hotline",
    "phone": "1-800-662-4357",
    "text": null,
    "url": "https://www.samhsa.gov",
    "available": "24/7",
    "description": "Treatment referral and information",
    "priority": 5
  }
]
```

### Campus-Specific Resources (Customize per Institution)

**Configuration File:** `config/campus-resources.json`

```json
{
  "institution_name": "Example University",
  "resources": [
    {
      "id": "campus_security",
      "name": "Campus Security",
      "phone": "(555) 123-4567",
      "text": null,
      "url": "https://university.edu/security",
      "available": "24/7",
      "description": "Immediate on-campus emergency response",
      "priority": 1
    },
    {
      "id": "counseling_center",
      "name": "University Counseling Center",
      "phone": "(555) 123-4568",
      "text": null,
      "url": "https://university.edu/counseling",
      "available": "8 AM - 6 PM Mon-Fri",
      "after_hours": "Call (555) 123-4567 for after-hours crisis support",
      "description": "Professional mental health services",
      "priority": 2
    },
    {
      "id": "student_health",
      "name": "Student Health Services",
      "phone": "(555) 123-4569",
      "text": null,
      "url": "https://university.edu/health",
      "available": "8 AM - 5 PM Mon-Fri",
      "description": "Medical and psychiatric care",
      "priority": 3
    },
    {
      "id": "dean_students",
      "name": "Dean of Students Office",
      "phone": "(555) 123-4570",
      "text": null,
      "url": "https://university.edu/dean-students",
      "available": "8 AM - 5 PM Mon-Fri",
      "description": "Student support and advocacy",
      "priority": 4
    }
  ]
}
```

---

## Crisis Alert UI Implementation

### Frontend Component Specifications

**Component:** `EmergencyResourcesBanner`

**Trigger Conditions:**
- WebSocket message `type: "crisis_alert"` received
- Keyword detection triggered during session
- User manually clicks "I need emergency help" button (always available)

**Visual Design:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🆘 IMMEDIATE HELP AVAILABLE                                 │
│                                                              │
│ If you're in crisis or considering harming yourself,        │
│ please reach out to one of these resources right now:       │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 📞 988 Suicide & Crisis Lifeline (24/7)              │  │
│ │    Call: 988  |  Text: 988  |  Chat: 988lifeline.org│  │
│ │    → Call Now  → Text Now  → Chat Now                │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🏫 Campus Security (24/7)                             │  │
│ │    Call: (555) 123-4567                               │  │
│ │    → Call Now                                         │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                              │
│ [Show More Resources ▼]  [I'm Safe - Continue Session]     │
└─────────────────────────────────────────────────────────────┘
```

**Behavior:**
- Appears as **non-modal overlay** at top of screen (does not block counseling)
- Remains visible until user clicks "I'm Safe - Continue Session"
- Does **not** automatically end the session
- Logs user action (called resource, dismissed, continued session)

**Accessibility:**
- Announce with screen reader: "Emergency resources alert"
- Keyboard focus moves to banner when displayed
- High contrast colors (red #E74C3C background, white text)
- Minimum 18px font size for phone numbers

---

## Crisis Event Logging

### Database Schema

**Table:** `crisis_events`

```sql
CREATE TABLE crisis_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Detection Details
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    detection_method VARCHAR(50) NOT NULL, -- 'keyword', 'llm_analysis', 'user_triggered'
    
    -- Keyword Detection (if applicable)
    keywords_matched TEXT[], -- Array of matched keywords
    context_text TEXT, -- Surrounding conversation context
    
    -- LLM Analysis (if applicable)
    llm_severity VARCHAR(20), -- 'critical', 'concerning', null
    llm_indicators TEXT[], -- Patterns detected by LLM
    llm_confidence DECIMAL(3,2), -- 0.00-1.00
    llm_reasoning TEXT,
    
    -- User Response
    resources_displayed JSONB, -- Which resources were shown
    user_action VARCHAR(50), -- 'called_resource', 'dismissed', 'continued', 'ended_session'
    resource_clicked VARCHAR(100), -- ID of resource clicked (if any)
    dismissed_at TIMESTAMP WITH TIME ZONE,
    
    -- Follow-up
    flagged_for_review BOOLEAN DEFAULT true,
    reviewed_by UUID REFERENCES admin_users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_crisis_events_session ON crisis_events(session_id);
CREATE INDEX idx_crisis_events_user ON crisis_events(user_id);
CREATE INDEX idx_crisis_events_review ON crisis_events(flagged_for_review, reviewed_at);
```

---

## LLM System Prompt Integration

### Crisis-Aware Counselor Prompts

All counselor system prompts MUST include this crisis response section:

```
CRISIS RESPONSE PROTOCOL:

If the student expresses suicidal thoughts, self-harm intentions, or discloses abuse:

1. ACKNOWLEDGE with empathy: "I hear that you're going through an incredibly difficult time."

2. VALIDATE feelings: "What you're feeling is real, and it's important that you're talking about it."

3. GENTLE REDIRECT to human support: "I want to make sure you get the immediate support you need. Would you be comfortable speaking with a crisis counselor who can provide more specialized help? I can connect you with resources right now."

4. STAY PRESENT: Continue the conversation supportively. Do not abruptly end or dismiss the session.

5. REINFORCE SAFETY: "Your safety matters. The resources appearing on your screen are available 24/7 and can provide immediate support."

DO NOT:
- Minimize or dismiss crisis expressions
- Provide medical advice or diagnoses
- Promise confidentiality (legally required to report imminent danger)
- End the session immediately
- Use phrases like "just calm down" or "it's not that bad"

REMEMBER: The crisis detection system will automatically display emergency resources. Your role is to remain supportive, empathetic, and present while professional crisis support becomes available.
```

---

## Testing & Validation

### Test Scenarios

**Scenario 1: Explicit Suicide Ideation**
- Input: "I've been thinking about suicide. I have a plan."
- Expected: Immediate keyword trigger, emergency banner displays, LLM analysis confirms critical
- Validation: Crisis event logged, user action tracked

**Scenario 2: Subtle Distress (LLM Detection)**
- Input: Multiple exchanges expressing hopelessness, isolation, rejection of help
- Expected: LLM analysis detects concerning pattern after 5 turns, banner displays
- Validation: LLM reasoning logged, lower priority resources shown

**Scenario 3: False Positive Prevention**
- Input: "I'm taking a psychology class about suicide prevention."
- Expected: No alert (academic context exclusion)
- Validation: No crisis event created

**Scenario 4: User-Triggered Help**
- Input: User clicks "I need emergency help" button
- Expected: Banner displays immediately regardless of conversation content
- Validation: Detection method logged as 'user_triggered'

**Scenario 5: Past Tense Discussion**
- Input: "I used to have dark thoughts last year, but I'm better now."
- Expected: LLM analysis evaluates current state, no alert if context is clearly past
- Validation: No false alarm

---

## Compliance & Legal Considerations

### FERPA Compliance

- Crisis event logs are considered **educational records** under FERPA
- Disclosure to emergency personnel is permitted under **health/safety emergency exception** (34 CFR § 99.36)
- Students must be notified in Terms of Service that crisis situations may require intervention

### Liability Protections

**Disclaimer in Session Start:**
```
"This AI counseling service is not a substitute for professional mental health care 
or emergency services. If you are in crisis or considering harming yourself, please 
call 988 (Suicide & Crisis Lifeline) or your local emergency services immediately. 

By continuing, you understand that this service will detect and respond to crisis 
indicators by providing emergency resource information."
```

### Mandatory Reporting

**Scope:** This platform does NOT replace mandatory reporting obligations for:
- Child abuse (if student is minor)
- Imminent threat to others
- Court-ordered disclosures

**Implementation:** Crisis events flagged for human review enable compliance officers to fulfill reporting duties.

---

## Performance & Monitoring

### Metrics to Track

1. **Detection Metrics:**
   - Keyword trigger rate per 1000 sessions
   - LLM analysis trigger rate
   - False positive rate (based on human review)
   - True positive confirmation rate

2. **User Response Metrics:**
   - % of users who call/text emergency resources
   - % of users who dismiss alert
   - % of users who continue vs. end session
   - Average time alert displayed before action

3. **System Performance:**
   - Keyword detection latency (<100ms target)
   - LLM analysis latency (<2s target)
   - WebSocket message delivery time (<500ms target)

### Alerting Thresholds

- **Critical:** Keyword detection system failure (no detections in 24h with active sessions)
- **Warning:** LLM analysis latency >5s
- **Info:** Crisis event rate >10% of sessions (may indicate tuning needed)

---

## Continuous Improvement

### Human Review Process

1. **Daily Review:** Compliance officer reviews all flagged crisis events
2. **Weekly Analysis:** Evaluate false positive rate and adjust keyword exclusions
3. **Monthly Tuning:** Update LLM prompt based on missed detections or over-flagging
4. **Quarterly Audit:** Full crisis detection system audit with student health center

### Keyword Dictionary Updates

- **Source:** National Suicide Prevention Lifeline guidance, CDC terminology
- **Frequency:** Quarterly review, ad-hoc for emerging slang/terms
- **Approval:** Requires sign-off from student health director and legal counsel

---

## Version History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0 | 2025-12-19 | Initial crisis detection protocol | Product Team |

---

## Emergency Contacts for Platform Team

**Crisis Escalation (24/7):**
- On-Call Engineer: See PagerDuty rotation
- Student Health Director: Dr. Sarah Johnson, (555) 123-9999
- Legal Counsel: law@university.edu, (555) 123-9998

**System Failure Escalation:**
If crisis detection system fails, immediately activate manual monitoring protocol (documented in `ops/incident-response.md`).
