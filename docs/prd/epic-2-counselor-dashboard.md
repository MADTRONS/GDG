# Epic 2: Counselor Dashboard & Category Management

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Planned

---

## Epic Goal

Create the central hub of the application—a visually engaging dashboard displaying counselor category cards that students interact with to begin counseling sessions.

---

## Expanded Goal

This epic focuses on the UI/UX of counselor browsing, implementing the card-based navigation paradigm, and preparing the infrastructure for connecting to voice and video services (without implementing full calling logic—that's saved for Epics 3 and 4). By the end, students can log in, see available counselor categories with descriptions, and understand their options, setting the stage for functional calling integration.

---

## User Stories

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

---

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

---

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

---

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

---

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

---

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

## Definition of Done

- [x] All 6 stories completed with acceptance criteria met
- [x] Dashboard displays counselor category cards
- [x] Counselor categories loaded from backend API
- [x] Responsive design tested on mobile, tablet, desktop
- [x] Placeholder buttons provide user feedback
- [x] WCAG 2.1 AA accessibility compliance verified
- [x] Unit tests for API endpoints passing
- [x] Integration tests for dashboard page passing

---

**Document Status:** Planned - Awaiting Epic 1 Completion