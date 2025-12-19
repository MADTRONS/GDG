# Epic 3: Voice Calling Integration

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Planned

---

## Epic Goal

Implement full voice calling functionality using PipeCat framework integrated with Daily.co WebRTC transport.

---

## Expanded Goal

Students click the Voice Call button on a counselor card and are immediately connected to an AI voice counselor specialized in that category. The system provides real-time speech-to-text transcription, natural text-to-speech responses, and in-session controls (mute, volume, end call). This epic delivers the core value proposition of instant-access voice counseling with human-like interaction quality. The GitHub reference repo (https://github.com/mksinha01/agent-starter-embed) guides the PipeCat integration approach.

---

## User Stories

### Story 3.1: Backend PipeCat Room Creation

**As a** backend developer,  
**I want** an API endpoint that creates Daily.co rooms and spawns PipeCat bot instances,  
**so that** voice calling sessions can be initiated for students.

**Acceptance Criteria:**

1. POST /api/voice/create-room endpoint created accepting JSON payload with counselor_category field.
2. Endpoint uses Daily.co API (via DAILY_API_KEY) to create temporary room with properties: enable_chat=true, enable_screenshare=false, max_participants=2.
3. Endpoint generates Daily.co user token for the student and bot token for PipeCat agent.
4. Endpoint spawns PipeCat bot process using subprocess or background task queue (Celery/RQ) with room URL, bot token, and counselor category context.
5. Bot configuration includes: Deepgram STT service, Cartesia TTS service, Google Gemini LLM with counselor category-specific system prompt.
6. Endpoint returns JSON response: { room_url, user_token, room_name, session_id }.
7. Endpoint requires authentication and logs session creation with student ID and category.
8. Error handling: returns 500 if Daily.co API fails, includes detailed error message for debugging.
9. Unit tests mock Daily.co API calls and verify correct room creation logic.

---

### Story 3.2: PipeCat Bot Configuration and System Prompts

**As a** backend developer,  
**I want** PipeCat bots configured with category-specific counseling personas,  
**so that** conversations feel specialized and relevant to student needs.

**Acceptance Criteria:**

1. System prompts defined for each counselor category (Health, Career, Academic, etc.) stored in configuration files or database.
2. Each system prompt includes: counselor role description, tone guidelines (supportive, professional), key topics/focus areas, boundaries (what counselor cannot help with).
3. Example Health counselor prompt: "You are a supportive health counselor specializing in student wellness. Focus on mental health, stress management, sleep hygiene, and healthy habits. Be empathetic and non-judgmental. If student expresses suicidal ideation, immediately provide crisis hotline information."
4. PipeCat bot initialization loads appropriate system prompt based on counselor_category parameter.
5. LLM context aggregator configured with system message before bot joins Daily.co room.
6. Bot logs confirm correct prompt loaded for each session.

---

### Story 3.3: Frontend Voice Call Initiation

**As a** student,  
**I want** to click Voice Call button and immediately connect to a voice counselor,  
**so that** I can start my counseling session without delay.

**Acceptance Criteria:**

1. Voice Call button on counselor card triggers voice call initiation flow when clicked.
2. Frontend calls POST /api/voice/create-room with selected counselor category.
3. On success, frontend receives room credentials (room_url, user_token, session_id) from backend.
4. Loading state displayed during room creation: button shows spinner and text "Connecting..."
5. Error handling: if API call fails, display error toast with message and retry button.
6. On room creation success, frontend transitions to voice session view (new page or modal).
7. Session ID stored in frontend state for use in transcript display and session history.

---

### Story 3.4: PipeCat Client Connection and Audio Setup

**As a** student,  
**I want** my browser to connect to the voice session using WebRTC,  
**so that** I can speak and hear the AI counselor in real-time.

**Acceptance Criteria:**

1. Frontend initializes PipeCat RTVIClient with DailyTransport using room_url and user_token from backend.
2. Client configured with: enableMic=true, enableCam=false, audio constraints (echo cancellation, noise suppression).
3. Client connection established and "connected" event listener triggers UI update showing "Connected" status.
4. Browser requests microphone permissions from user; if denied, display error message with instructions.
5. Audio output automatically plays to speakers when bot sends audio frames (no manual audio element creation required).
6. If connection fails (network error, bot not joined), display error message with retry and cancel options.
7. "disconnected" event listener handles cleanup and returns user to dashboard with session summary.
8. Client handles "on_track_started" event for bot audio track and ensures audio plays through device speakers.

---

### Story 3.5: Live Transcript Display

**As a** student,  
**I want** to see a live transcript of my conversation,  
**so that** I can follow along visually and refer back to what was said.

**Acceptance Criteria:**

1. Voice session view displays a transcript panel showing conversation history in chronological order.
2. PipeCat client "userTranscript" event listener captures student's speech as text and appends to transcript with "User:" label.
3. PipeCat client "botTranscript" event listener captures counselor's responses as text and appends to transcript with "Counselor:" label.
4. Transcript auto-scrolls to bottom as new messages arrive (with option to pause auto-scroll if user scrolls up).
5. Each transcript entry includes timestamp (e.g., "2:34 PM").
6. Transcript text is readable with sufficient font size (16px+) and contrast (4.5:1 minimum).
7. Transcript panel is responsive: side panel on desktop (768px+), bottom panel on mobile (<768px).

---

### Story 3.6: In-Session Controls

**As a** student,  
**I want** to control my audio settings during the session,  
**so that** I can mute myself, adjust volume, or end the call when ready.

**Acceptance Criteria:**

1. Voice session view displays control panel with buttons: Mute Microphone, Adjust Volume, End Session.
2. Mute button toggles microphone mute state using PipeCat client API; button shows muted status visually (icon change, color change).
3. Volume slider adjusts output volume for counselor's voice (0-100%).
4. End Session button prompts confirmation dialog: "Are you sure you want to end this session?"
5. On confirm end session, client disconnects from Daily.co room, session data saved to backend, user redirected to dashboard with session summary.
6. All controls keyboard accessible and screen reader friendly.
7. Connection quality indicator displayed (green=excellent, yellow=fair, red=poor) based on network stats from Daily.co.

---

### Story 3.7: Session Logging and Metadata

**As a** backend developer,  
**I want** voice sessions logged with metadata and transcripts,  
**so that** students can review past conversations and administrators can track usage.

**Acceptance Criteria:**

1. Database table created for sessions with fields: session_id (UUID), user_id (FK), counselor_category, mode (voice/video), started_at, ended_at, duration_seconds, transcript (TEXT), quality_rating.
2. POST /api/sessions/save endpoint accepts session data: session_id, transcript, duration, quality rating (optional).
3. Endpoint requires authentication and validates user owns the session.
4. Frontend calls save endpoint when session ends (on disconnect or explicit end).
5. Transcript saved as JSON array of messages: [{ timestamp, speaker: "user"|"counselor", text }].
6. Session metadata queryable via GET /api/sessions endpoint for session history page (implemented in Epic 5).

---

### Story 3.8: Crisis Detection and Safety Features

**As a** system,  
**I want** to detect crisis keywords in conversations,  
**so that** students in distress receive immediate access to emergency resources.

**Acceptance Criteria:**

1. PipeCat bot system prompt includes instruction: "If user expresses suicidal thoughts, self-harm ideation, or immediate danger, respond with empathy and provide crisis hotline: National Suicide Prevention Lifeline 988."
2. Frontend transcript panel monitors for crisis keywords (suicide, kill myself, self-harm, etc.) in user messages.
3. If crisis keyword detected, frontend displays prominent alert banner with emergency hotline numbers and "Connect to Crisis Line" button.
4. Alert banner remains visible until user dismisses or session ends.
5. Session flagged in backend database with crisis_detected=true for administrative review.
6. Crisis detection logic tested with variety of keyword phrases and edge cases.

---

## Definition of Done

- [x] All 8 stories completed with acceptance criteria met
- [x] Voice calling fully functional from counselor selection to session end
- [x] PipeCat integration working with Daily.co WebRTC
- [x] Real-time transcription displaying correctly
- [x] Crisis detection system operational
- [x] Session data logged to database
- [x] In-session controls functional (mute, volume, end)
- [x] Unit and integration tests passing
- [x] Performance testing shows <30 second connection time

---

**Document Status:** Planned - Awaiting Epic 2 Completion