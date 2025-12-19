# College Student Counseling Platform - Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Draft for Review

---

## Goals and Background Context

### Goals

- Provide college students with instant, 24/7 access to specialized AI counselors across multiple categories (Health, Career, Academic, etc.)
- Deliver seamless voice and video counseling experiences with natural, human-like interaction quality
- Create a trustworthy, professional interface that feels authentic and supportive, not generic or AI-like
- Enable students to connect with counselors in <30 seconds with zero wait times or appointment scheduling
- Support unlimited concurrent counseling sessions with consistent quality across all interactions
- Achieve 85%+ user satisfaction and 60%+ return usage rates within first semester pilot
- Demonstrate measurable reduction in traditional campus counseling waitlists through scalable AI solution

### Background Context

The mental health crisis among college students has intensified post-pandemic, with 70% reporting anxiety or depression yet only 40% seeking help due to access barriers. Traditional campus counseling centers face 2-4 week wait times and operate with student-to-counselor ratios exceeding 1:1500. Existing solutionswhether campus-based, app-based, or telehealthsuffer from limited capacity, availability constraints, high costs, or lack of specialization.

This platform addresses these gaps by combining proven AI frameworks (PipeCat for voice, Beyond Presence for video avatars) with modern web architecture to deliver specialized, instant-access counseling. Students choose their preferred interaction mode (voice or video) and counselor category, connecting immediately to AI counselors trained for specific domains. The technology stack leverages Daily.co WebRTC, LiveKit, Deepgram STT, Cartesia TTS, and advanced LLMs to create natural conversations with authentic visual representation.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-19 | 1.0 | Initial PRD draft based on project brief | Mary (Business Analyst) |

---

## Requirements

### Functional Requirements

**FR1:** The system SHALL provide a student login page accepting credentials in the format \\\domain\\username\ and password, validating against stored user records.

**FR2:** The system SHALL check blocked user status on login attempt and display a specific error message directing blocked students to contact support if their account is restricted.

**FR3:** The system SHALL maintain user session state after successful authentication, keeping students logged in across page navigation until explicit logout.

**FR4:** The system SHALL display a dashboard with counselor category cards (minimum: Health, Career, Academic, Financial, Social, Personal Development) after successful login.

**FR5:** Each counselor category card SHALL display: category icon, specialty description, available interaction modes (voice/video icons), and connection availability indicator.

**FR6:** The system SHALL initiate a voice calling session when student clicks the voice call option on any counselor card, connecting to PipeCat-powered AI counselor within 30 seconds.

**FR7:** The system SHALL initiate a video calling session when student clicks the video call option on any counselor card, connecting to Beyond Presence avatar counselor within 30 seconds.

**FR8:** Voice calling sessions SHALL include real-time speech-to-text transcription displayed to the student during the conversation.

**FR9:** Voice calling sessions SHALL provide natural text-to-speech responses with appropriate counseling tone and pacing.

**FR10:** Video calling sessions SHALL display a realistic AI avatar counselor with lip-sync matching the voice responses within 100ms accuracy.

**FR11:** Video calling sessions SHALL include avatar emotional expressions (concerned, supportive, thoughtful) matching conversation context.

**FR12:** The system SHALL provide in-session controls for both voice and video modes: mute microphone, adjust volume, end session, and (video only) toggle camera.

**FR13:** The system SHALL gracefully degrade video sessions to voice-only mode if connection bandwidth drops below quality threshold.

**FR14:** The system SHALL log all counseling sessions with metadata: student ID, counselor category, session duration, interaction mode, timestamp.

**FR15:** The system SHALL provide a session history view showing past conversations with date, category, duration, and mode.

**FR16:** Students SHALL be able to view transcript of past voice/video sessions from the session history page.

**FR17:** The system SHALL display real-time connection quality indicators during active sessions (excellent/good/fair/poor).

**FR18:** The system SHALL provide a logout function accessible from all authenticated pages, clearing session and returning to login page.

**FR19:** The system SHALL handle concurrent sessions, allowing multiple students to connect to different counselor categories simultaneously without interference.

**FR20:** The system SHALL implement crisis detection keywords and immediately display emergency hotline numbers and resources when detected in conversation.

### Non-Functional Requirements

**NFR1:** The system SHALL achieve 99.5% uptime during business hours (8 AM - 11 PM student local time) measured monthly.

**NFR2:** Voice call audio quality SHALL maintain 4.0/5.0 or higher rating based on user feedback surveys.

**NFR3:** Video call avatar rendering SHALL maintain minimum 24 FPS on devices with baseline specifications (2019+ smartphones, modern browsers).

**NFR4:** Initial page load time SHALL be under 3 seconds on broadband connections (10 Mbps+).

**NFR5:** Voice/video connection establishment SHALL complete within 30 seconds of user initiating call 95% of the time.

**NFR6:** The system SHALL support a minimum of 50 concurrent counseling sessions without degradation in audio/video quality.

**NFR7:** All user data and session transcripts SHALL be encrypted at rest using AES-256 and in transit using TLS 1.3.

**NFR8:** The system SHALL comply with FERPA (Family Educational Rights and Privacy Act) requirements for student data protection.

**NFR9:** Session transcripts SHALL be stored for maximum 90 days and then automatically purged unless student explicitly saves for longer retention.

**NFR10:** The platform SHALL be accessible according to WCAG 2.1 AA standards including keyboard navigation and screen reader compatibility.

**NFR11:** The frontend SHALL be responsive and functional on devices ranging from mobile phones (320px width) to desktop monitors (1920px+).

**NFR12:** API response times for authentication and session creation SHALL be under 500ms at p95.

**NFR13:** The system SHALL support graceful degradation when external services (Daily.co, LiveKit, Beyond Presence) experience outages, falling back to cached content or voice-only mode.

**NFR14:** Error messages SHALL be user-friendly, avoid technical jargon, and provide clear next steps for students to resolve issues.

**NFR15:** The system SHALL maintain detailed logs for debugging and auditing purposes with minimum 30-day retention.

---

## User Interface Design Goals

### Overall UX Vision

Create a **calming, trustworthy, and professional** counseling environment that feels like a modern mental health clinic rather than a tech chatbot interface. The aesthetic should blend **soft healthcare blues and greens** with **warm, welcoming neutrals**. Interactions should feel **human-centered and supportive**, prioritizing student comfort and ease of access. The design must avoid generic AI chatbot patterns (no floating bubbles, overly playful animations, or sterile corporate aesthetics). Instead, think **premium telehealth platform meets thoughtfully designed student support center**.

### Key Interaction Paradigms

- **Card-based navigation** for counselor selection with clear visual hierarchy
- **One-click access** to counseling sessionsminimize steps between login and conversation
- **Real-time feedback** during sessions (connection quality, transcript updates, visual/audio cues)
- **Calm, non-intrusive notifications** for system status (connected, reconnecting, etc.)
- **Progressive disclosure** of advanced features (settings, history) to avoid overwhelming first-time users
- **Touch-friendly targets** (minimum 44x44px) for mobile accessibility

### Core Screens and Views

From a product perspective, the critical screens necessary to deliver PRD goals:

1. **Login Screen** - Clean, centered form with clear error messaging for blocked accounts or invalid credentials
2. **Main Dashboard** - Grid of counselor category cards with icons, descriptions, and voice/video options
3. **Voice Session View** - Full-screen minimalist interface with live transcript, waveform visualization, in-session controls
4. **Video Session View** - Avatar video player with transcript sidebar, connection quality indicator, controls
5. **Session History** - Chronological list of past sessions with filters by category and date
6. **Session Detail/Transcript** - Full transcript view with metadata and option to download or delete
7. **Settings/Profile** - Student preferences, notification settings, account management
8. **Error/Help States** - Connection troubleshooting, FAQ, emergency resources

### Accessibility

**Target Level:** WCAG 2.1 AA Compliance

- Full keyboard navigation support for all interactions
- Screen reader compatible with ARIA labels and semantic HTML
- Sufficient color contrast (minimum 4.5:1 for text, 3:1 for UI components)
- Captions/transcripts available for all audio content (already planned as feature)
- Focus indicators clearly visible on all interactive elements
- Form fields with proper labels and error validation

### Branding

- **Color Palette:** Primary: Soft blue (#4A90E2), Secondary: Calming green (#6FCF97), Neutral: Warm grays (#F5F5F5, #333333)
- **Typography:** Clean sans-serif for headability (Inter or similar), readable line heights (1.6+)
- **Iconography:** Rounded, friendly icons for counselor categories (avoid clinical/sterile medical symbols)
- **Tone:** Supportive and professional without being overly casual or stiffthink "understanding advisor"
- **Photography/Illustration:** If used, show diverse students in natural, positive environments (avoid stock photo clichés)

### Target Device and Platforms

**Primary:** Web Responsive (Desktop and Mobile browsers)

- **Desktop:** Optimized for Chrome, Firefox, Safari, Edge on Windows/Mac (1280px+ viewports)
- **Mobile:** Optimized for iOS Safari and Android Chrome (320px-768px viewports)
- **Tablet:** Responsive layout adapts to iPad/Android tablets (768px-1024px)

**Future Consideration:** Native mobile apps (iOS/Android) for push notifications and offline access to past transcriptsnot included in MVP scope.

---

## Technical Assumptions

### Repository Structure

**Monorepo** using pnpm workspaces or Turborepo

**Rationale:** Keeps frontend and backend tightly coupled during rapid MVP development, simplifies shared TypeScript types and configurations, enables atomic commits across full-stack features. All code lives in single repository with separate packages for frontend, backend, and shared utilities.

### Service Architecture

**Hybrid Monolith with Modular Services**

- **Frontend:** Next.js 14 app served as single application
- **Backend:** FastAPI Python monolith with modular routers for authentication, sessions, counselor management
- **External Services:** PipeCat voice agent, Beyond Presence avatar API, Daily.co/LiveKit infrastructure treated as managed external dependencies
- **Database:** Single PostgreSQL instance for user data and session logs

**Rationale:** Monolithic architecture simplifies MVP development, deployment, and debugging. Modular internal structure (routers, services, repositories) allows future extraction to microservices if scale demands. Serverless functions avoided due to complexity of real-time WebRTC connections requiring persistent sessions.

### Testing Requirements

**Unit + Integration Testing with Manual QA**

**Frontend:**
- Unit tests for utility functions and hooks (Vitest)
- Component integration tests (React Testing Library)
- Manual testing for real-time WebRTC interactions (challenging to automate in CI)

**Backend:**
- Unit tests for business logic and utilities (pytest)
- Integration tests for API endpoints (pytest with TestClient)
- Manual testing for external API integrations (PipeCat, Beyond Presence)

**E2E Testing:** Limited scope for MVPmanual testing of critical user paths (login  select counselor  complete session). Playwright E2E tests considered for post-MVP if budget allows.

**Rationale:** Balance test coverage with MVP speed. Real-time audio/video testing is notoriously difficult to automate reliably. Focus automated tests on business logic and API contracts; rely on manual QA for UX and integration flows.

### Additional Technical Assumptions and Requests

- **Language - Frontend:** TypeScript (strict mode enabled)
- **Language - Backend:** Python 3.11+
- **Frontend Framework:** Next.js 14 (App Router) with React 18
- **UI Component Library:** shadcn/ui (Radix UI primitives + Tailwind CSS)
- **Styling:** Tailwind CSS with custom theme configuration
- **State Management:** React Context for global state (auth, session), Zustand if more complexity needed
- **Backend Framework:** FastAPI with Pydantic for validation
- **Database ORM:** SQLAlchemy (async) for PostgreSQL interactions
- **Authentication:** JWT tokens stored in httpOnly cookies
- **Real-time Transport:** Daily.co SDK for voice (PipeCat integration), LiveKit client for video (Beyond Presence)
- **API Integration SDKs:**
  - @pipecat-ai/client-js for voice calling
  - @daily-co/daily-js for WebRTC transport
  - livekit-client for video sessions
- **LLM Providers:** Google Gemini 2.0 Flash (primary), OpenAI GPT-4 (fallback)
- **STT Provider:** Deepgram Nova-2 model
- **TTS Provider:** Cartesia Sonic-English
- **Avatar Provider:** Beyond Presence API with pre-configured avatar IDs for each counselor category
- **Deployment Target:** Docker containers on cloud platform (AWS ECS, Google Cloud Run, or Railway for MVP simplicity)
- **CI/CD:** GitHub Actions for automated testing and deployment
- **Environment Management:** .env files for local development, cloud provider secrets management for production
- **Logging:** Structured logging with context IDs (Python: loguru, Frontend: custom logger)
- **Monitoring:** Basic uptime monitoring and error tracking (Sentry or similar)
- **Version Control:** Git with feature branch workflow, pull requests required before merging to main

---

## Epic List

**Epic 1: Foundation & Authentication**  
*Goal:* Establish project infrastructure, repository structure, CI/CD pipeline, and student authentication system with login/logout functionality.

**Epic 2: Counselor Dashboard & Category Management**  
*Goal:* Create the main dashboard displaying counselor categories as interactive cards, enabling students to browse available counselor types and understand their options before initiating sessions.

**Epic 3: Voice Calling Integration**  
*Goal:* Implement end-to-end voice calling functionality using PipeCat framework, allowing students to connect with AI voice counselors and have natural spoken conversations with real-time transcription.

**Epic 4: Video Calling Integration**  
*Goal:* Integrate Beyond Presence avatar system for visual counseling sessions, providing students with face-to-face counseling experience via AI avatar with lip-sync and emotional expressions.

**Epic 5: Session Management & History**  
*Goal:* Enable students to review past counseling sessions, view transcripts, and manage their counseling history with filtering, search, and transcript download capabilities.

---

## Epic 1: Foundation & Authentication

**Expanded Goal:**  
Establish the foundational project setup including repository initialization, development environment configuration, CI/CD pipeline, and core authentication system. This epic delivers a working login page where students can authenticate using institutional credentials (\\\domain\\username\ format), maintains secure sessions, and handles blocked user scenarios. By the end of this epic, the basic project structure is deployment-ready with automated testing and a functional (though minimal) authentication flow that serves as the foundation for all subsequent features.

### Story 1.1: Project Initialization and Repository Setup

**As a** developer,  
**I want** the project repository initialized with monorepo structure, frontend and backend packages, and essential configuration files,  
**so that** the team has a consistent development environment and can begin feature development immediately.

**Acceptance Criteria:**

1. Repository created with pnpm workspace configuration for monorepo structure containing packages/frontend and packages/backend directories.
2. Frontend package initialized with Next.js 14 (App Router), TypeScript, Tailwind CSS, and shadcn/ui configured.
3. Backend package initialized with FastAPI, Python 3.11+, Poetry/pip for dependency management.
4. Root-level configuration files present: .gitignore, README.md, .env.example, docker-compose.yml for local development.
5. ESLint and Prettier configured for frontend with consistent code style enforced.
6. Python linting (Black, Flake8) configured for backend.
7. README includes quick start instructions for running frontend and backend locally.

### Story 1.2: CI/CD Pipeline Setup

**As a** developer,  
**I want** automated testing and deployment pipelines configured,  
**so that** code quality is maintained and deployments are reliable and repeatable.

**Acceptance Criteria:**

1. GitHub Actions workflow created for frontend: runs linting, type checking, and unit tests on pull requests.
2. GitHub Actions workflow created for backend: runs linting, type checking, and pytest on pull requests.
3. Docker images build successfully for both frontend and backend services.
4. Deployment workflow configured to push Docker images to container registry on merge to main branch.
5. Environment variables and secrets properly managed in GitHub repository settings.
6. CI pipeline fails if tests fail or linting errors exist, preventing merge of broken code.

### Story 1.3: Database Setup and User Model

**As a** backend developer,  
**I want** PostgreSQL database configured with user authentication schema,  
**so that** student credentials and session data can be securely stored and retrieved.

**Acceptance Criteria:**

1. PostgreSQL database running locally via Docker Compose with initialization scripts.
2. SQLAlchemy models defined for User table with fields: id (UUID primary key), username (unique), password_hash, is_blocked (boolean), created_at, updated_at.
3. Database migrations setup using Alembic with initial migration creating users table.
4. Database connection pool configured in FastAPI application with async SQLAlchemy session management.
5. Environment variables for database connection string properly loaded from .env file.
6. Basic health check endpoint (GET /health) returns database connection status.

### Story 1.4: Student Login API Endpoint

**As a** backend developer,  
**I want** a login API endpoint that validates student credentials and returns authentication tokens,  
**so that** the frontend can authenticate students and maintain secure sessions.

**Acceptance Criteria:**

1. POST /api/auth/login endpoint accepts JSON payload with username and password fields.
2. Endpoint validates username format matches \\domain\\username pattern and returns 400 error if format invalid.
3. Endpoint queries database for user record matching username and verifies password using bcrypt.
4. If credentials valid and user not blocked, endpoint generates JWT token and returns it in httpOnly cookie plus response body.
5. If user account is blocked (is_blocked=true), endpoint returns 403 error with message: "Your account has been blocked. Please reach out to support for help."
6. If credentials invalid, endpoint returns 401 error with generic message: "Invalid username or password."
7. JWT token includes user ID and username claims, expires in 24 hours.
8. Unit tests cover all authentication scenarios: valid login, invalid credentials, blocked user, malformed username.

### Story 1.5: Student Logout API Endpoint

**As a** student,  
**I want** to securely log out of my session,  
**so that** my account is protected when I'm finished using the platform.

**Acceptance Criteria:**

1. POST /api/auth/logout endpoint created requiring valid JWT authentication.
2. Endpoint clears the httpOnly authentication cookie and returns 200 success response.
3. After logout, subsequent requests to authenticated endpoints return 401 unauthorized.
4. Unit tests verify logout clears session and prevents further authenticated access.

### Story 1.6: Login Page UI

**As a** student,  
**I want** a clean, professional login page,  
**so that** I can easily sign in to access counseling services.

**Acceptance Criteria:**

1. Login page created at / route in Next.js app using shadcn/ui form components.
2. Form includes two input fields: Username (with placeholder showing format \\domain\\username) and Password (masked input).
3. Form includes "Login" submit button styled according to branding guidelines (primary blue color).
4. Login form validates username format client-side before submission and displays inline error if format incorrect.
5. On form submission, frontend calls POST /api/auth/login and handles response: success redirects to /dashboard, error displays message below form.
6. Blocked user error message matches backend message: "Your account has been blocked. Please reach out to support for help."
7. Invalid credentials error message: "Invalid username or password. Please try again."
8. Loading state shown on submit button while request in flight (button disabled, loading spinner).
9. Page is fully responsive and functional on mobile devices (320px+ width).
10. Page passes WCAG 2.1 AA accessibility checks (keyboard navigation, screen reader labels).

### Story 1.7: Session State Management

**As a** student,  
**I want** to remain logged in while navigating the platform,  
**so that** I don't have to re-enter credentials for every action.

**Acceptance Criteria:**

1. React Context provider created for authentication state management containing: user data (id, username), authentication status, login/logout functions.
2. Frontend checks authentication status on initial app load by validating JWT token or calling auth status endpoint.
3. Protected routes (dashboard, session history, etc.) redirect to login page if user not authenticated.
4. Authenticated user data available throughout application via useAuth() hook.
5. Logout function clears authentication state and calls POST /api/auth/logout endpoint.
6. JWT token automatically sent with all API requests via httpOnly cookie.

### Story 1.8: Deployment and Environment Configuration

**As a** developer,  
**I want** the MVP authentication system deployable to a production environment,  
**so that** we can begin user testing and iterate based on real feedback.

**Acceptance Criteria:**

1. Docker Compose configuration builds and runs both frontend and backend services locally with database.
2. Environment-specific configuration documented in README for local, staging, and production environments.
3. Production deployment guide created covering: database migration, environment variable setup, SSL/TLS configuration, logging setup.
4. Health check endpoints responding successfully in deployed environment.
5. HTTPS enabled with valid SSL certificate for production domain.
6. Basic monitoring configured to alert on service downtime or error rate spikes.

---

## Epic 2: Counselor Dashboard & Category Management

**Expanded Goal:**  
Create the central hub of the applicationa visually engaging dashboard displaying counselor category cards that students interact with to begin counseling sessions. This epic focuses on the UI/UX of counselor browsing, implementing the card-based navigation paradigm, and preparing the infrastructure for connecting to voice and video services (without implementing full calling logicthat's saved for Epics 3 and 4). By the end, students can log in, see available counselor categories with descriptions, and understand their options, setting the stage for functional calling integration.

### Story 2.1: Dashboard Page Layout and Routing

**As a** student,  
**I want** to land on a clear dashboard after logging in,  
**so that** I can immediately see my counseling options.

**Acceptance Criteria:**

1. Dashboard page created at /dashboard route in Next.js app.
2. Dashboard only accessible to authenticated users; unauthenticated access redirects to login page.
3. Page displays header with platform logo/name, welcome message showing student's username, and logout button.
4. Main content area prepared with container for counselor category cards (grid layout, responsive).
5. Footer includes links to Help/FAQ and Emergency Resources (placeholders for now).
6. Page passes WCAG 2.1 AA accessibility checks.

### Story 2.2: Counselor Category Data Model

**As a** backend developer,  
**I want** counselor categories defined in the system,  
**so that** the frontend can display accurate, consistent counselor information.

**Acceptance Criteria:**

1. Counselor category configuration defined in backend (YAML, JSON, or database table) with fields: id, name, description, icon_name, enabled.
2. Minimum six categories configured: Health, Career, Academic, Financial, Social, Personal Development.
3. Each category includes a 1-2 sentence description of the counselor's specialty.
4. GET /api/counselors/categories endpoint returns list of enabled categories as JSON.
5. Endpoint accessible only to authenticated users (requires valid JWT).
6. Unit tests verify endpoint returns expected category data structure.

### Story 2.3: Counselor Category Cards UI

**As a** student,  
**I want** to see counselor categories as visually distinct cards,  
**so that** I can easily identify which type of counseling I need.

**Acceptance Criteria:**

1. Dashboard fetches counselor categories from GET /api/counselors/categories on page load.
2. Each category rendered as a card using shadcn/ui Card component with: category icon, category name as heading, description text, two action buttons (Voice Call, Video Call).
3. Cards arranged in responsive grid: 1 column on mobile (<640px), 2 columns on tablet (640-1024px), 3-4 columns on desktop (1024px+).
4. Card styling follows branding guidelines: soft blue primary color, rounded corners, subtle shadow on hover.
5. Icons for each category are visually appropriate and sourced from icon library (Lucide React or similar).
6. Cards have hover state showing slight elevation increase and border color change.
7. Voice Call and Video Call buttons styled distinctly (icons: microphone for voice, video camera for video).
8. Loading state shown while categories fetch (skeleton cards or spinner).
9. Error state displayed if categories fail to load with retry button.

### Story 2.4: Voice Call Button (Placeholder Action)

**As a** student,  
**I want** clicking Voice Call button to provide feedback (even if calling not yet implemented),  
**so that** I understand the platform recognizes my action and will connect me once the feature is complete.

**Acceptance Criteria:**

1. Voice Call button on each counselor card is interactive and styled as primary action.
2. Clicking Voice Call button displays a toast notification: "Voice calling will be available in the next update. Stay tuned!"
3. Console logs the selected counselor category for debugging purposes.
4. Button includes loading state (disabled while notification shows) to prevent double-clicks.
5. All voice call button interactions keyboard accessible (Enter key triggers action).

### Story 2.5: Video Call Button (Placeholder Action)

**As a** student,  
**I want** clicking Video Call button to provide feedback (even if calling not yet implemented),  
**so that** I understand the platform recognizes my action and will connect me once the feature is complete.

**Acceptance Criteria:**

1. Video Call button on each counselor card is interactive and styled as secondary action (distinct from Voice Call).
2. Clicking Video Call button displays a toast notification: "Video calling will be available in the next update. Stay tuned!"
3. Console logs the selected counselor category for debugging purposes.
4. Button includes loading state (disabled while notification shows) to prevent double-clicks.
5. All video call button interactions keyboard accessible (Enter key triggers action).

### Story 2.6: Dashboard Navigation and Logout

**As a** student,  
**I want** to log out from the dashboard,  
**so that** I can end my session securely when finished.

**Acceptance Criteria:**

1. Logout button in dashboard header calls logout function from authentication context.
2. Logout function invokes POST /api/auth/logout API endpoint and clears local authentication state.
3. After logout completes, user redirected to login page with confirmation message: "You have been logged out."
4. All authenticated API requests fail after logout with 401 responses.
5. Logout button accessible via keyboard (Tab focus, Enter key).

---

## Epic 3: Voice Calling Integration

**Expanded Goal:**  
Implement full voice calling functionality using PipeCat framework integrated with Daily.co WebRTC transport. Students click the Voice Call button on a counselor card and are immediately connected to an AI voice counselor specialized in that category. The system provides real-time speech-to-text transcription, natural text-to-speech responses, and in-session controls (mute, volume, end call). This epic delivers the core value proposition of instant-access voice counseling with human-like interaction quality. The GitHub reference repo (https://github.com/mksinha01/agent-starter-embed) guides the PipeCat integration approach.

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

## Epic 4: Video Calling Integration

**Expanded Goal:**  
Integrate Beyond Presence avatar system to provide visual counseling sessions where students interact with realistic AI avatar counselors. This epic builds on the voice calling infrastructure established in Epic 3 but adds the visual componentavatars with lip-sync, emotional expressions, and high-quality video rendering. Students can choose video calls for a more personal, face-to-face counseling experience. The GitHub reference repo (https://github.com/ruxakK/ai_avatar_it_support_agent.git) guides the Beyond Presence integration approach using LiveKit infrastructure.

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

## Epic 5: Session Management & History

**Expanded Goal:**  
Enable students to review their counseling history by providing a session history page where they can browse past conversations, filter by counselor category or date, view full transcripts, and manage their session data (download or delete). This epic completes the core user experience loop: students can have counseling sessions (voice/video) and then reflect on or refer back to those conversations over time. By the end, the platform feels complete and empowers students to take ownership of their counseling journey.

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
6. 	ranscript_preview includes first 100 characters of transcript for list display.
7. Endpoint returns 401 if user not authenticated, 400 if invalid filter parameters provided.
8. Unit tests cover filtering, pagination, and authorization logic.

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

## Checklist Results Report

*This section will be populated after running the PM checklist tool.*

---

## Next Steps

### UX Expert Prompt

"Hi! I need your help creating a high-fidelity design for the College Student Counseling Platform. I've completed the PRD (attached/linked). Please review the UI Design Goals section and create detailed mockups for the core screens: Login Page, Counselor Dashboard, Voice Session View, Video Session View, and Session History Page. Focus on the calming, trustworthy aesthetic using soft blues/greens, ensure WCAG 2.1 AA compliance, and design for mobile-first responsiveness. Provide Figma files or detailed component specifications for the dev team."

### Architect Prompt

"Hi! I need a comprehensive technical architecture document for the College Student Counseling Platform. I've completed the PRD (attached/linked). Please review the Technical Assumptions and Requirements sections, then design the system architecture covering: frontend structure (Next.js components, routing, state management), backend API design (FastAPI endpoints, database schema), PipeCat voice integration, Beyond Presence video integration, deployment infrastructure, and security considerations. Include sequence diagrams for voice/video call flows and database schema diagrams. Focus on MVP scope while considering scalability for future growth."

---

**END OF PRD**

