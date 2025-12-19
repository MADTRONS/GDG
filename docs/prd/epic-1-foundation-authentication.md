# Epic 1: Foundation & Authentication

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Active

---

## Epic Goal

Establish the foundational project setup including repository initialization, development environment configuration, CI/CD pipeline, and core authentication system.

---

## Expanded Goal

This epic delivers a working login page where students can authenticate using institutional credentials (\\domain\username format), maintains secure sessions, and handles blocked user scenarios. By the end of this epic, the basic project structure is deployment-ready with automated testing and a functional (though minimal) authentication flow that serves as the foundation for all subsequent features.

---

## User Stories

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

---

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

---

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

---

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

---

### Story 1.5: Student Logout API Endpoint

**As a** student,  
**I want** to securely log out of my session,  
**so that** my account is protected when I'm finished using the platform.

**Acceptance Criteria:**

1. POST /api/auth/logout endpoint created requiring valid JWT authentication.
2. Endpoint clears the httpOnly authentication cookie and returns 200 success response.
3. After logout, subsequent requests to authenticated endpoints return 401 unauthorized.
4. Unit tests verify logout clears session and prevents further authenticated access.

---

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

---

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

---

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

## Definition of Done

- [x] All 8 stories completed with acceptance criteria met
- [x] Authentication system fully functional (login/logout)
- [x] Project structure established and documented
- [x] CI/CD pipeline operational
- [x] Database schema deployed
- [x] Unit and integration tests passing
- [x] Deployment to production environment successful
- [x] Documentation complete (README, deployment guide)

---

**Document Status:** Active - Ready for Development