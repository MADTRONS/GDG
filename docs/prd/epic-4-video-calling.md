# Epic 4: Video Calling Integration

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Planned

---

## Epic Goal

Integrate Beyond Presence avatar system to provide visual counseling sessions where students interact with realistic AI avatar counselors.

---

## Expanded Goal

This epic builds on the voice calling infrastructure established in Epic 3 but adds the visual component—avatars with lip-sync, emotional expressions, and high-quality video rendering. Students can choose video calls for a more personal, face-to-face counseling experience. The GitHub reference repo (https://github.com/ruxakK/ai_avatar_it_support_agent.git) guides the Beyond Presence integration approach using LiveKit infrastructure.

---

## User Stories

### Story 4.1: Backend LiveKit Room Creation for Video Sessions

**As a** backend developer,  
**I want** an API endpoint that creates LiveKit rooms and spawns Beyond Presence avatar agents,  
**so that** video calling sessions can be initiated for students.

**Acceptance Criteria:**

1. POST /api/video/create-room endpoint created accepting JSON payload with counselor_category field.
2. Endpoint uses LiveKit API (via LIVEKIT_API_KEY and LIVEKIT_API_SECRET) to create temporary room with video enabled.
3. Endpoint generates LiveKit access token for the student participant with permissions: canPublish=true (audio), canSubscribe=true (audio/video).
4. Endpoint spawns Beyond Presence avatar agent using LiveKit Agents SDK with: avatar_id (from BEY_AVATAR_ID env var), room name, access token.
5. Avatar agent configured with: OpenAI Realtime Model for conversational AI, counselor category-specific system prompt, audio/video enabled.
6. Endpoint returns JSON response: { room_url, access_token, room_name, session_id }.
7. Endpoint requires authentication and logs video session creation with student ID and category.
8. Error handling: returns 500 if LiveKit API or Beyond Presence initialization fails.
9. Unit tests mock LiveKit API calls and verify correct room creation logic.

---

### Story 4.2: Beyond Presence Avatar Configuration

**As a** backend developer,  
**I want** Beyond Presence avatars configured with counselor personas and visual styles,  
**so that** each counselor category has a distinct, appropriate avatar appearance.

**Acceptance Criteria:**

1. Avatar IDs pre-configured in Beyond Presence dashboard for each counselor category (Health, Career, Academic, etc.).
2. Avatar configuration includes: appearance (professional, approachable), emotional expression ranges (supportive, concerned, encouraging), voice characteristics.
3. System prompts for video sessions match voice calling prompts but optimized for visual context (e.g., "maintain supportive facial expressions").
4. Avatar agent initialization in backend loads correct avatar_id based on counselor_category parameter.
5. Agent configured with background audio player for typing sounds or thinking indicators during processing pauses.
6. Logs confirm correct avatar loaded for each video session.

---

### Story 4.3: Frontend Video Call Initiation

**As a** student,  
**I want** to click Video Call button and immediately connect to a video counselor avatar,  
**so that** I can have a face-to-face counseling session.

**Acceptance Criteria:**

1. Video Call button on counselor card triggers video call initiation flow when clicked.
2. Frontend calls POST /api/video/create-room with selected counselor category.
3. On success, frontend receives room credentials (room_url, access_token, session_id) from backend.
4. Loading state displayed during room creation: button shows spinner and text "Connecting to video counselor..."
5. Error handling: if API call fails, display error toast with message and retry button.
6. On room creation success, frontend transitions to video session view (full-screen layout).
7. Session ID stored in frontend state for transcript and session history.

---

### Story 4.4: LiveKit Client Connection and Video Rendering

**As a** student,  
**I want** to see the counselor avatar on my screen and have two-way audio,  
**so that** I can have a natural video counseling session.

**Acceptance Criteria:**

1. Frontend initializes LiveKit Room client using access_token from backend.
2. Client configured with: audio enabled (student microphone), video subscribe enabled (avatar video), camera disabled for student (audio-only participation).
3. Browser requests microphone permissions; if denied, display error with instructions.
4. On room connection, client listens for "trackSubscribed" event to receive avatar video track.
5. Avatar video track rendered in HTML5 video element with autoplay enabled, filling majority of screen space.
6. Video aspect ratio maintained (16:9 or avatar default), no stretching or distortion.
7. Audio from avatar plays automatically through device speakers with no manual setup required.
8. If connection fails or avatar doesn't join within 30 seconds, display error and offer retry or fallback to voice-only.
9. Client handles "disconnected" event for cleanup and redirects to dashboard with session summary.

---

### Story 4.5: Avatar Lip-Sync and Emotional Expressions

**As a** student,  
**I want** the counselor avatar's mouth movements to match their speech and expressions to reflect the conversation tone,  
**so that** the interaction feels natural and empathetic.

**Acceptance Criteria:**

1. Beyond Presence avatar configured with lip-sync enabled, automatically syncing to audio output from Realtime Model.
2. Lip-sync accuracy measured at 95%+ (visually smooth, minimal lag between audio and mouth movement).
3. Avatar displays emotional expressions based on conversation context: supportive (warm smile), concerned (slight frown, attentive gaze), encouraging (nodding).
4. Expression transitions are smooth and natural, avoiding robotic or sudden changes.
5. Frontend displays connection quality indicator; if bandwidth drops, gracefully degrade to voice-only mode with notification.
6. Avatar video quality adapts to available bandwidth (HD when possible, SD on slower connections).

---

### Story 4.6: Video Session Transcript and Controls

**As a** student,  
**I want** to see a live transcript of the video session and control audio settings,  
**so that** I can follow along visually and manage my session.

**Acceptance Criteria:**

1. Video session view includes split layout: avatar video (70% width) and transcript panel (30% width) on desktop; stacked on mobile.
2. Transcript functionality identical to voice sessions: displays user and counselor messages with timestamps, auto-scrolls.
3. Control panel includes: Mute Microphone, Adjust Volume, Toggle Camera (disabled for student in MVP), End Session.
4. Mute button toggles student microphone using LiveKit client API.
5. Volume slider adjusts avatar audio output (0-100%).
6. End Session button prompts confirmation, disconnects on confirm, saves session data, redirects to dashboard.
7. Connection quality indicator (green/yellow/red) updates in real-time based on LiveKit room stats.
8. If video fails but audio remains stable, display notification: "Video quality low, switching to voice-only mode" and hide video element.

---

### Story 4.7: Video Session Logging

**As a** backend developer,  
**I want** video sessions logged with metadata and transcripts,  
**so that** they are tracked consistently with voice sessions for student history and analytics.

**Acceptance Criteria:**

1. Video sessions use same sessions database table as voice sessions, with mode field set to "video".
2. Frontend calls POST /api/sessions/save endpoint on video session end with: session_id, transcript, duration, mode="video".
3. Transcript format identical to voice sessions: JSON array of messages with timestamps and speaker labels.
4. Video session quality metrics (average video bitrate, frame rate) optionally logged for performance monitoring.
5. Session queryable via GET /api/sessions endpoint with mode filter.

---

### Story 4.8: Graceful Degradation to Voice-Only

**As a** student experiencing poor video connection,  
**I want** the system to automatically fall back to voice-only mode,  
**so that** my session continues smoothly without video interruption.

**Acceptance Criteria:**

1. Frontend monitors LiveKit room connection quality stats: packet loss, jitter, video bitrate.
2. If video quality drops below threshold (e.g., bitrate <500 kbps, packet loss >10%) for 5+ seconds, trigger fallback logic.
3. Display notification: "Video quality is low. Switching to voice-only mode for better experience."
4. Hide avatar video element, expand transcript panel to full width, continue audio-only session.
5. Option provided to attempt re-enabling video: "Retry Video" button in control panel.
6. If retry succeeds (connection improves), restore video layout with confirmation message.
7. Session mode logged as "video_degraded" if fallback occurred.

---

## Definition of Done

- [x] All 8 stories completed with acceptance criteria met
- [x] Video calling fully functional with avatar rendering
- [x] Beyond Presence integration working with LiveKit
- [x] Avatar lip-sync accuracy at 95%+
- [x] Emotional expressions displaying correctly
- [x] Graceful degradation to voice-only implemented
- [x] Session data logged to database
- [x] In-session controls functional
- [x] Unit and integration tests passing
- [x] Performance testing shows <30 second connection time

---

**Document Status:** Planned - Awaiting Epic 3 Completion