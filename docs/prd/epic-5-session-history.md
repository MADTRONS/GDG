# Epic 5: Session Management & History

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Planned

---

## Epic Goal

Enable students to review their counseling history by providing a session history page where they can browse past conversations, filter by counselor category or date, view full transcripts, and manage their session data.

---

## Expanded Goal

This epic completes the core user experience loop: students can have counseling sessions (voice/video) and then reflect on or refer back to those conversations over time. By the end, the platform feels complete and empowers students to take ownership of their counseling journey.

---

## User Stories

### Story 5.1: Session History Page Layout

**As a** student,  
**I want** a dedicated page showing my past counseling sessions,  
**so that** I can easily review my conversation history.

**Acceptance Criteria:**

1. Session history page created at /sessions route, accessible only to authenticated users.
2. Page header includes title "My Counseling Sessions" and filter/search controls (category filter, date range picker).
3. Main content area displays list of sessions in reverse chronological order (most recent first).
4. Each session list item shows: counselor category icon/name, date and time, session duration, mode (voice/video icon), truncated first line of transcript.
5. Session list items clickable, navigating to session detail page.
6. Empty state displayed if student has no sessions yet: "You haven't started any counseling sessions yet. Visit your dashboard to get started!"
7. Page responsive on mobile (vertical list, touch-friendly tap targets).
8. Pagination or infinite scroll implemented if student has 20+ sessions.

---

### Story 5.2: Backend Session History API

**As a** backend developer,  
**I want** an API endpoint that returns a student's session history with filtering,  
**so that** the frontend can display and filter past sessions efficiently.

**Acceptance Criteria:**

1. GET /api/sessions endpoint created requiring authentication (JWT token).
2. Endpoint queries sessions table for records matching authenticated user's user_id.
3. Query supports optional filters via query parameters: category (counselor category), mode (voice/video), start_date, end_date.
4. Results sorted by started_at descending (newest first) with pagination parameters: page, limit (default 20).
5. Response JSON structure: { sessions: [{ session_id, counselor_category, mode, started_at, duration_seconds, transcript_preview }], total_count, page, limit }.
6. transcript_preview includes first 100 characters of transcript for list display.
7. Endpoint returns 401 if user not authenticated, 400 if invalid filter parameters provided.
8. Unit tests cover filtering, pagination, and authorization logic.

---

### Story 5.3: Session Filtering and Search

**As a** student,  
**I want** to filter my session history by counselor category and date range,  
**so that** I can quickly find specific past conversations.

**Acceptance Criteria:**

1. Session history page includes filter controls: Category dropdown (All, Health, Career, Academic, etc.), Mode dropdown (All, Voice, Video), Date range picker.
2. Selecting filter options triggers API call to GET /api/sessions with filter parameters.
3. Session list updates to show only matching sessions, maintaining reverse chronological order.
4. Filter state persisted in URL query parameters (e.g., /sessions?category=Health&mode=voice) for shareable/bookmarkable filters.
5. "Clear Filters" button resets all filters and shows full session history.
6. Loading state shown while filtered results fetch.
7. Filter controls keyboard accessible and work with screen readers.

---

### Story 5.4: Session Detail Page with Full Transcript

**As a** student,  
**I want** to view the full transcript of a past session,  
**so that** I can review what was discussed and reflect on the counseling received.

**Acceptance Criteria:**

1. Session detail page created at /sessions/:sessionId route, accessible only to authenticated session owner.
2. Page fetches session data from GET /api/sessions/:sessionId endpoint (requires authentication, returns 403 if user doesn't own session).
3. Page displays session metadata: counselor category, date/time, duration, mode (voice/video).
4. Full transcript rendered as conversation thread: alternating user and counselor messages with timestamps and speaker labels.
5. Messages styled clearly: user messages left-aligned with distinct background color, counselor messages right-aligned, consistent with modern chat UI patterns.
6. Transcript scrollable with timestamps in margin for easy reference.
7. Back button navigates to session history page.
8. Page responsive on mobile with readable font sizes and spacing.

---

### Story 5.5: Backend Session Detail API

**As a** backend developer,  
**I want** an API endpoint that returns complete session details including full transcript,  
**so that** students can view their past conversations.

**Acceptance Criteria:**

1. GET /api/sessions/:sessionId endpoint created requiring authentication.
2. Endpoint queries sessions table for record matching session_id and authenticated user_id.
3. Response includes: session_id, counselor_category, mode, started_at, ended_at, duration_seconds, full transcript (JSON array of messages).
4. Endpoint returns 404 if session_id not found, 403 if session belongs to different user.
5. Transcript deserialized from database TEXT field into JSON array structure: [{ timestamp: ISO string, speaker: "user"|"counselor", text: string }].
6. Unit tests verify authorization logic and data structure.

---

### Story 5.6: Download Transcript Feature

**As a** student,  
**I want** to download my session transcript as a text file,  
**so that** I can keep a personal copy for reflection or share with my personal therapist.

**Acceptance Criteria:**

1. Session detail page includes "Download Transcript" button below transcript content.
2. Clicking button triggers download of plain text file formatted as: Session_[Category]_[Date].txt.
3. File content includes: session metadata header (category, date, duration) followed by formatted transcript (speaker labels, timestamps, message text).
4. Download implemented client-side using Blob API and anchor element download attribute (no backend endpoint needed).
5. Button accessible via keyboard and screen reader announces action.

---

### Story 5.7: Delete Session Feature

**As a** student,  
**I want** to delete a past session from my history,  
**so that** I can manage my privacy and remove sessions I no longer wish to keep.

**Acceptance Criteria:**

1. Session detail page includes "Delete Session" button (styled as danger/destructive action, secondary color like red).
2. Clicking button displays confirmation dialog: "Are you sure you want to delete this session? This action cannot be undone."
3. On confirm, frontend calls DELETE /api/sessions/:sessionId endpoint.
4. Endpoint requires authentication, verifies user owns session, soft-deletes session (sets deleted_at timestamp) or hard-deletes record.
5. On successful delete, frontend redirects to session history page with success message: "Session deleted."
6. If delete fails (network error, authorization), display error toast with retry option.
7. Deleted sessions no longer appear in session history list.
8. Unit tests verify authorization and deletion logic.

---

### Story 5.8: Session Stats and Dashboard Summary

**As a** student,  
**I want** to see a summary of my counseling usage on the dashboard,  
**so that** I can track my engagement and reflect on my patterns.

**Acceptance Criteria:**

1. Dashboard page includes "My Counseling Stats" widget displaying: Total Sessions, Total Hours, Most Used Category, Recent Session Date.
2. Frontend fetches stats from GET /api/sessions/stats endpoint (requires authentication).
3. Endpoint returns aggregated data: { total_sessions, total_hours, top_category, last_session_date }.
4. Stats widget styled consistently with counselor category cards (same card component).
5. "View All Sessions" link in stats widget navigates to session history page.
6. Stats update immediately after completing a new session (refresh or real-time update).
7. Widget responsive on mobile, stacked layout if needed.

---

## Definition of Done

- [x] All 8 stories completed with acceptance criteria met
- [x] Session history page functional with filtering
- [x] Full transcript viewing operational
- [x] Download transcript feature working
- [x] Delete session feature implemented
- [x] Dashboard stats widget displaying correctly
- [x] Authorization enforced (students only see own sessions)
- [x] Unit and integration tests passing
- [x] WCAG 2.1 AA accessibility compliance verified

---

**Document Status:** Planned - Awaiting Epic 4 Completion