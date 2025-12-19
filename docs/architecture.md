# College Student Counseling Platform Architecture Document

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** In Progress

---

## Introduction

This document outlines the overall project architecture for the **College Student Counseling Platform**, including backend systems, shared services, and non-UI specific concerns. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:**
If the project includes a significant user interface, a separate Frontend Architecture Document will detail the frontend-specific design and MUST be used in conjunction with this document. Core technology stack choices documented herein (see "Tech Stack") are definitive for the entire project, including any frontend components.

### Starter Template or Existing Project

**Analysis:** This is a **greenfield project** with explicit technology selections defined in the PRD. The project is not based on a specific starter template, though it references the PipeCat integration guide repository (https://github.com/mksinha01/agent-starter-embed) for voice calling implementation patterns.

**Technology Foundation:**
- Frontend: Next.js 14 (App Router) with React 18
- Backend: FastAPI with Python 3.11+
- Monorepo: pnpm workspaces or Turborepo
- UI: shadcn/ui with Tailwind CSS

The PipeCat reference repository provides integration guidance for voice AI functionality but does not serve as the project foundation. This approach gives maximum architectural flexibility while maintaining clear technology boundaries defined in the PRD.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-19 | 1.0 | Initial architecture document | Winston (Architect) |

---

## High Level Architecture

### Technical Summary

The College Student Counseling Platform employs a **hybrid monolithic architecture** with modular service boundaries, deployed as a monorepo containing distinct frontend and backend applications. The system leverages **FastAPI** (Python) for the backend API and **Next.js 14** (TypeScript) for the frontend, communicating via RESTful APIs and real-time WebRTC connections. Key external integrations include **PipeCat** for voice AI counseling, **Beyond Presence** for avatar video, **Daily.co/LiveKit** for WebRTC infrastructure, **Deepgram** for speech-to-text, **Cartesia** for text-to-speech, and **Google Gemini 2.0 Flash/OpenAI GPT-4** for LLM capabilities. This architecture prioritizes **rapid MVP development** while maintaining modularity for future microservice extraction, supporting the PRD goal of delivering instant-access counseling with 99.5% uptime and <30 second connection times.

### High Level Overview

**1. Architectural Style**

**Hybrid Monolith with Modular Services** - A single FastAPI application organized into modular routers (authentication, sessions, counselor management) that can be extracted into microservices if scale demands. The frontend is a separate Next.js application, creating a clear separation between presentation and business logic layers.

**2. Repository Structure**

**Monorepo** using pnpm workspaces or Turborepo, containing:
- `packages/frontend` - Next.js 14 application
- `packages/backend` - FastAPI Python application
- `packages/shared` - Shared TypeScript types and utilities
- Root-level configuration for monorepo tooling

This structure enables atomic commits across full-stack features, simplified dependency management, and consistent TypeScript types shared between frontend and backend.

**3. Service Architecture**

- **Frontend Service:** Next.js 14 App Router serving the UI, handling client-side state, and managing WebRTC connections
- **Backend Service:** FastAPI monolith providing REST APIs for authentication, session management, counselor configuration, and orchestration of external AI services
- **External Managed Services:** PipeCat voice agents, Beyond Presence avatar API, Daily.co/LiveKit WebRTC infrastructure treated as black-box dependencies
- **Data Layer:** Single PostgreSQL instance for user accounts, session logs, and counselor configurations

**4. Primary User Interaction Flow**

```
Student Login → Authentication (JWT) → Dashboard (Counselor Selection) 
    ↓
Voice Call: Backend creates Daily.co room → Spawns PipeCat bot → Student joins via WebRTC → Real-time transcription
    ↓
Video Call: Backend creates LiveKit room → Triggers Beyond Presence avatar → Student joins via WebRTC → Avatar lip-sync
    ↓
Session History → View transcripts → Download/Delete sessions
```

**5. Key Architectural Decisions**

- **Monolith over Microservices:** Simplifies MVP development, reduces operational complexity, and avoids premature optimization. Backend remains cohesive while maintaining internal modularity through FastAPI routers.

- **Monorepo over Polyrepo:** Enables shared TypeScript types between frontend/backend, atomic feature commits, and simplified dependency updates. Aligns with PRD's rapid iteration goals.

- **Managed WebRTC Services (Daily.co/LiveKit):** Offloads complex real-time infrastructure (TURN/STUN servers, bandwidth optimization, recording) to proven platforms, allowing team to focus on counseling experience rather than WebRTC plumbing.

- **JWT in httpOnly Cookies:** Balances security (XSS protection) with stateless authentication, enabling horizontal scaling of backend without session store dependency.

- **PostgreSQL over NoSQL:** Session transcripts and user data have clear relational structure. ACID guarantees ensure consistency for authentication and session logging. Future sharding possible if scale requires.

### High Level Project Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Student Browser]
    end
    
    subgraph "Application Layer - Monorepo"
        Frontend[Next.js 14 Frontend<br/>TypeScript + React 18<br/>shadcn/ui]
        Backend[FastAPI Backend<br/>Python 3.11+<br/>Modular Routers]
        Shared[Shared Package<br/>TypeScript Types]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>User Data + Sessions)]
    end
    
    subgraph "External AI Services"
        PipeCat[PipeCat Voice Agent<br/>Daily.co Transport]
        BeyondPresence[Beyond Presence<br/>Avatar API]
        Deepgram[Deepgram STT<br/>Nova-2]
        Cartesia[Cartesia TTS<br/>Sonic-English]
        LLM[Google Gemini 2.0 Flash<br/>+ OpenAI GPT-4 fallback]
    end
    
    subgraph "WebRTC Infrastructure"
        Daily[Daily.co<br/>Voice Rooms]
        LiveKit[LiveKit<br/>Video Rooms]
    end
    
    Browser -->|HTTPS/REST| Frontend
    Browser -->|WebRTC| Daily
    Browser -->|WebRTC| LiveKit
    
    Frontend -->|REST API| Backend
    Frontend -.->|Shared Types| Shared
    Backend -.->|Shared Types| Shared
    
    Backend -->|SQL| PostgreSQL
    Backend -->|Create Room/Token| Daily
    Backend -->|Create Room/Token| LiveKit
    Backend -->|Spawn Bot| PipeCat
    Backend -->|Avatar Request| BeyondPresence
    
    PipeCat -->|Join Room| Daily
    PipeCat -->|STT| Deepgram
    PipeCat -->|TTS| Cartesia
    PipeCat -->|LLM| LLM
    
    BeyondPresence -->|Avatar Stream| LiveKit
    BeyondPresence -->|LLM| LLM
    
    style Frontend fill:#4A90E2,color:#fff
    style Backend fill:#6FCF97,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style PipeCat fill:#FFB84D,color:#000
    style BeyondPresence fill:#FFB84D,color:#000
```

### Architectural and Design Patterns

**Backend Core Patterns:**

- **Repository Pattern:** Abstract data access logic behind repository interfaces (`UserRepository`, `SessionRepository`). Enables testing with mock repositories and future database migration flexibility.  
  _Rationale:_ Decouples business logic from SQLAlchemy specifics, critical for unit testing and maintaining clean architecture boundaries.

- **Dependency Injection:** FastAPI's native DI system for injecting database sessions, repositories, and services into route handlers.  
  _Rationale:_ Improves testability (inject mocks), reduces coupling, and aligns with FastAPI best practices.

- **Router/Controller Pattern:** Organize endpoints into logical routers (`auth_router`, `session_router`, `counselor_router`) within modular backend structure.  
  _Rationale:_ Enables clear separation of concerns and future extraction to microservices if needed without major refactoring.

**Integration Patterns:**

- **Adapter Pattern:** Wrap external APIs (Daily.co, PipeCat, Beyond Presence) in adapter classes with consistent interfaces.  
  _Rationale:_ Isolates external API changes, simplifies testing with mock adapters, and enables provider switching if needed.

- **Circuit Breaker Pattern:** Protect against cascading failures from external service outages (Daily.co, Deepgram, etc.) using circuit breaker library (e.g., `pybreaker`).  
  _Rationale:_ PRD requires 99.5% uptime and graceful degradation; circuit breakers prevent thread exhaustion from hanging external calls.

**Communication Patterns:**

- **REST API:** Synchronous HTTP/JSON for authentication, session creation, history retrieval. Standard CRUD operations with OpenAPI documentation.  
  _Rationale:_ Simple, well-understood, and sufficient for non-real-time operations. Aligns with PRD's explicit REST API requirement.

- **WebRTC Signaling:** Backend orchestrates WebRTC room creation and token generation; actual media streams bypass backend entirely (peer-to-peer via Daily.co/LiveKit TURN servers).  
  _Rationale:_ Reduces backend bandwidth costs, offloads WebRTC complexity to managed services, enables 50+ concurrent sessions per PRD.

**Data Patterns:**

- **Active Record (via SQLAlchemy ORM):** Database models contain both data and persistence logic, standard for Python/FastAPI projects.  
  _Rationale:_ Balances simplicity with functionality; Repository pattern abstracts this at service layer.

- **Event Logging Pattern:** All counseling sessions logged as immutable records with metadata (student_id, category, duration, transcript). No event sourcing complexity in MVP.  
  _Rationale:_ Supports PRD requirements for session history, analytics, and FERPA compliance auditing.

---

## Tech Stack

**CRITICAL:** This section is the DEFINITIVE technology selection for the entire project. All agents (dev, frontend architect, QA) MUST reference these exact versions. Any deviation requires updating this document.

### Cloud Infrastructure

- **Provider:** Railway (for MVP), with migration path to AWS/GCP if scale demands
- **Key Services:** 
  - PostgreSQL (Railway-managed)
  - Docker container hosting
  - Environment variable management
  - Automatic HTTPS/SSL
- **Deployment Regions:** US-based (single region for MVP)

**Rationale:** Railway offers the fastest path to production with minimal DevOps overhead, automatic deployments from GitHub, and managed PostgreSQL. The containerized architecture ensures portability to AWS/GCP when needed. PRD emphasizes MVP speed over enterprise infrastructure.

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Languages** |
| Backend Language | Python | 3.11.7 | Primary backend development language | Async/await support, strong typing via Pydantic, excellent AI/ML library ecosystem, team preference per PRD |
| Frontend Language | TypeScript | 5.3.3 | Primary frontend development language | Strict mode enabled, type safety across frontend/backend boundary, PRD requirement |
| **Runtimes** |
| JavaScript Runtime | Node.js | 20.11.0 LTS | Frontend build and development runtime | Long-term support, stable for Next.js 14 |
| **Frontend** |
| Web Framework | Next.js | 14.2.0 | React-based web framework | App Router for modern routing, server components, API routes, PRD requirement |
| UI Library | React | 18.3.0 | Component-based UI library | Latest stable, concurrent features, included with Next.js |
| UI Components | shadcn/ui | Latest | Accessible component library | Built on Radix UI primitives, highly customizable, PRD requirement |
| Styling | Tailwind CSS | 3.4.1 | Utility-first CSS framework | Rapid styling, design system consistency, PRD requirement |
| State Management | React Context + Zustand | 18.3.0 + 4.5.0 | Global state management | Context for auth state, Zustand if complexity grows, PRD guidance |
| Form Handling | React Hook Form | 7.51.0 | Form validation and state | Minimal re-renders, integrates with Zod validation |
| Schema Validation | Zod | 3.22.4 | Runtime type validation | Shared schemas with backend, type-safe API contracts |
| **Backend** |
| Web Framework | FastAPI | 0.110.0 | Python async web framework | High performance, auto OpenAPI docs, Pydantic validation, PRD requirement |
| Validation | Pydantic | 2.6.0 | Data validation and settings | Type-safe request/response models, included with FastAPI |
| Database ORM | SQLAlchemy | 2.0.27 | Async ORM for PostgreSQL | Async support, mature ecosystem, PRD requirement |
| Database Migrations | Alembic | 1.13.1 | Database schema migrations | Standard with SQLAlchemy, version-controlled schemas |
| Authentication | python-jose | 3.3.0 | JWT token generation/validation | HS256 signing, httpOnly cookie storage per PRD |
| Password Hashing | bcrypt | 4.1.2 | Secure password hashing | Industry standard, OWASP recommended |
| **Database** |
| Primary Database | PostgreSQL | 16.1 | Relational database | ACID guarantees, JSON support, mature replication, PRD requirement |
| Connection Pooling | asyncpg | 0.29.0 | Async PostgreSQL driver | High performance, used by SQLAlchemy async |
| **Real-Time Communication** |
| Voice WebRTC | Daily.co SDK | Latest | Voice call infrastructure | Managed TURN/STUN, recording, PRD requirement |
| Video WebRTC | LiveKit Client | 0.11.0 | Video call infrastructure | Low latency, scalable, PRD requirement |
| PipeCat Framework | @pipecat-ai/client-js + Python SDK | Latest | Voice AI agent framework | Daily.co integration, STT/TTS/LLM orchestration, PRD requirement |
| **AI Services** |
| Primary LLM | Google Gemini 2.0 Flash | API Latest | Counseling conversation generation | Fast, cost-effective, PRD requirement |
| Fallback LLM | OpenAI GPT-4 | gpt-4-turbo-preview | LLM fallback if Gemini unavailable | Reliability, PRD requirement |
| Speech-to-Text | Deepgram Nova-2 | API Latest | Voice transcription | Real-time streaming, high accuracy, PRD requirement |
| Text-to-Speech | Cartesia Sonic-English | API Latest | Natural voice synthesis | Low latency, expressive, PRD requirement |
| Avatar Service | Beyond Presence API | API Latest | AI avatar video generation | Lip-sync, emotional expressions, PRD requirement |
| **Development Tools** |
| Package Manager | pnpm | 8.15.0 | Monorepo package management | Fast, disk-efficient, workspace support |
| Monorepo Tool | Turborepo | 1.12.0 | Build orchestration | Caching, parallelization, PRD mentions this or pnpm workspaces |
| Linting (Frontend) | ESLint | 8.56.0 | JavaScript/TypeScript linting | Standard for Next.js projects |
| Formatting | Prettier | 3.2.4 | Code formatting | Consistent style across team |
| Linting (Backend) | Ruff | 0.1.15 | Fast Python linting/formatting | Replaces Black+Flake8, significantly faster |
| Type Checking (Backend) | mypy | 1.8.0 | Static type checking for Python | Enforce type safety |
| Testing (Frontend) | Vitest | 1.2.0 | Unit testing framework | Fast, Vite-native, modern alternative to Jest |
| Testing (Backend) | pytest | 8.0.0 | Python testing framework | Async support, fixtures, standard in Python |
| E2E Testing | Playwright | 1.41.0 | Browser automation testing | Cross-browser, reliable, PRD mentions limited E2E for MVP |
| **Deployment & DevOps** |
| Containerization | Docker | 25.0.0 | Application containerization | Consistent environments, PRD requirement |
| Container Orchestration | Docker Compose | 2.24.0 | Local multi-container orchestration | Development environment |
| CI/CD Platform | GitHub Actions | Latest | Automated testing and deployment | Free for public repos, PRD requirement |
| Deployment Platform | Railway | Latest | Cloud hosting (MVP) | Simple deployment, managed Postgres, auto-scaling |
| **Observability** |
| Logging (Backend) | Loguru | 0.7.2 | Structured logging | Simple API, structured output, PRD requirement |
| Logging (Frontend) | Custom Logger | N/A | Browser console abstraction | Structured logs, environment-aware |
| Error Tracking | Sentry | Latest SDK | Error monitoring and alerting | Captures exceptions, performance monitoring, PRD mentions |
| **Security & Secrets** |
| Secrets Management (Dev) | .env files | N/A | Local environment variables | Standard for development, PRD requirement |
| Secrets Management (Prod) | Railway Environment Variables | N/A | Production secrets | Encrypted, per-environment isolation |
| CORS Handling | fastapi-cors-middleware | Built-in | Cross-origin request handling | Included with FastAPI |

---

## Data Models

### User Model

**Purpose:** Represents student accounts for authentication and session tracking.

**Key Attributes:**
- `id`: UUID (primary key) - Unique identifier for the student
- `username`: String (unique, indexed) - Institutional credentials format `\domain\username`
- `password_hash`: String - Bcrypt-hashed password (never store plaintext)
- `is_blocked`: Boolean (default: false) - Account restriction flag
- `created_at`: DateTime (UTC) - Account creation timestamp
- `updated_at`: DateTime (UTC) - Last modification timestamp

**Relationships:**
- One-to-Many with `Session` - A user can have multiple counseling sessions

**Security Notes:**
- Username must be validated against `\domain\username` format
- Password hashing uses bcrypt with work factor 12+
- `is_blocked` checked on every login attempt

### Session Model

**Purpose:** Logs all counseling sessions for history, analytics, and FERPA compliance.

**Key Attributes:**
- `id`: UUID (primary key) - Unique session identifier
- `user_id`: UUID (foreign key to User) - Student who initiated session
- `counselor_category`: Enum - Category (Health, Career, Academic, Financial, Social, Personal Development)
- `mode`: Enum - Interaction mode (voice, video)
- `started_at`: DateTime (UTC) - Session start timestamp
- `ended_at`: DateTime (UTC, nullable) - Session end timestamp (null if active)
- `duration_seconds`: Integer (calculated) - Total session duration
- `transcript`: Text - Full conversation transcript (encrypted at rest)
- `room_name`: String - Daily.co/LiveKit room identifier for debugging
- `connection_quality`: String (nullable) - Average quality (excellent/good/fair/poor)
- `created_at`: DateTime (UTC) - Record creation timestamp

**Relationships:**
- Many-to-One with `User` - Each session belongs to one student

**Data Retention:**
- Transcripts auto-purged after 90 days per PRD (FERPA compliance)
- Metadata (duration, category, timestamps) retained indefinitely for analytics

### CounselorCategory Model

**Purpose:** Configuration for available counselor types and their AI prompts.

**Key Attributes:**
- `id`: UUID (primary key) - Unique category identifier
- `name`: String (unique) - Category name (e.g., "Health", "Career")
- `description`: String - Short description for dashboard cards
- `icon_name`: String - Icon identifier for UI rendering
- `system_prompt`: Text - LLM system prompt for this counselor persona
- `enabled`: Boolean (default: true) - Whether category is active
- `created_at`: DateTime (UTC) - Record creation timestamp
- `updated_at`: DateTime (UTC) - Last modification timestamp

**Relationships:**
- Referenced by `Session.counselor_category` (not a strict FK for flexibility)

**Configuration Notes:**
- Loaded at application startup and cached
- System prompts can be updated without code deployment
- Disabling categories hides them from dashboard without deleting data

### Data Model Diagram

```mermaid
erDiagram
    User ||--o{ Session : "has many"
    
    User {
        uuid id PK
        string username UK
        string password_hash
        boolean is_blocked
        datetime created_at
        datetime updated_at
    }
    
    Session {
        uuid id PK
        uuid user_id FK
        enum counselor_category
        enum mode
        datetime started_at
        datetime ended_at
        integer duration_seconds
        text transcript
        string room_name
        string connection_quality
        datetime created_at
    }
    
    CounselorCategory {
        uuid id PK
        string name UK
        string description
        string icon_name
        text system_prompt
        boolean enabled
        datetime created_at
        datetime updated_at
    }
```

---

## Components

### Authentication Service

**Responsibility:** Handle user authentication, JWT token management, and session validation.

**Key Interfaces:**
- `POST /api/auth/login` - Validate credentials and issue JWT token
- `POST /api/auth/logout` - Clear authentication cookie and invalidate session
- `GET /api/auth/me` - Retrieve current authenticated user info
- `Middleware: authenticate()` - Validate JWT on protected routes

**Dependencies:**
- `UserRepository` for database queries
- `bcrypt` for password verification
- `python-jose` for JWT operations
- PostgreSQL database

**Technology Stack:** FastAPI router (`auth_router`), SQLAlchemy async, JWT in httpOnly cookies

### Counselor Management Service

**Responsibility:** Provide counselor category configuration and manage availability.

**Key Interfaces:**
- `GET /api/counselors/categories` - List enabled counselor categories with descriptions
- `GET /api/counselors/categories/{id}` - Retrieve specific category details (admin only, future)

**Dependencies:**
- `CounselorCategoryRepository` for database queries
- Application startup cache for performance

**Technology Stack:** FastAPI router (`counselor_router`), SQLAlchemy async, in-memory caching

### Voice Session Service

**Responsibility:** Orchestrate voice calling sessions via PipeCat and Daily.co integration.

**Key Interfaces:**
- `POST /api/voice/create-room` - Create Daily.co room and spawn PipeCat bot
- `POST /api/voice/end-session` - Terminate bot and finalize session record
- Internal: `spawn_pipecat_bot()` - Launch PipeCat process with counselor context

**Dependencies:**
- `Daily.co API` for room creation and token generation
- `PipeCat Python SDK` for bot spawning
- `SessionRepository` for logging
- `Deepgram`, `Cartesia`, `Gemini/GPT-4` (via PipeCat configuration)

**Technology Stack:** FastAPI router (`voice_router`), Daily.co REST API, subprocess/background tasks for bot management

### Video Session Service

**Responsibility:** Orchestrate video calling sessions via Beyond Presence and LiveKit integration.

**Key Interfaces:**
- `POST /api/video/create-room` - Create LiveKit room and trigger Beyond Presence avatar
- `POST /api/video/end-session` - Terminate avatar stream and finalize session
- Internal: `trigger_avatar()` - Send avatar generation request with counselor persona

**Dependencies:**
- `LiveKit API` for room creation and token generation
- `Beyond Presence API` for avatar streaming
- `SessionRepository` for logging
- `Gemini/GPT-4` (used by Beyond Presence for conversation)

**Technology Stack:** FastAPI router (`video_router`), LiveKit REST API, Beyond Presence REST API, async HTTP client

### Session History Service

**Responsibility:** Retrieve, filter, and manage past counseling session records.

**Key Interfaces:**
- `GET /api/sessions` - List user's sessions with pagination and filters (category, mode, date range)
- `GET /api/sessions/{id}` - Retrieve detailed session with full transcript
- `DELETE /api/sessions/{id}` - Delete session (soft delete, mark for purge)
- `GET /api/sessions/{id}/download` - Export transcript as text file

**Dependencies:**
- `SessionRepository` for database queries
- Authentication middleware to ensure users only access own sessions
- Background job for 90-day transcript purge (FERPA compliance)

**Technology Stack:** FastAPI router (`session_router`), SQLAlchemy async with filtering, background scheduler (APScheduler)

### External Service Adapters

**Responsibility:** Abstract external API integrations behind consistent interfaces for testing and provider flexibility.

**Components:**
- `DailyAdapter` - Wraps Daily.co REST API (room creation, token generation)
- `LiveKitAdapter` - Wraps LiveKit REST API (room creation, token generation)
- `BeyondPresenceAdapter` - Wraps Beyond Presence API (avatar requests)
- `LLMAdapter` - Abstracts Gemini/GPT-4 with fallback logic

**Key Interfaces:**
- Each adapter exposes domain-specific methods (e.g., `create_voice_room()`, `create_video_room()`)
- Consistent error handling and retry policies
- Circuit breaker integration for resilience

**Dependencies:**
- External service API clients (Daily.co SDK, LiveKit SDK, httpx for REST APIs)
- `pybreaker` for circuit breaker pattern
- Configuration from environment variables

**Technology Stack:** Python adapter classes, httpx async HTTP client, SDK integrations

### Data Access Layer (Repositories)

**Responsibility:** Abstract database operations and provide clean interfaces for business logic.

**Components:**
- `UserRepository` - CRUD operations for User model
- `SessionRepository` - CRUD operations for Session model, complex queries (filtering, pagination)
- `CounselorCategoryRepository` - CRUD for CounselorCategory model

**Key Interfaces:**
- Standard methods: `create()`, `get_by_id()`, `update()`, `delete()`
- Domain-specific queries: `get_user_by_username()`, `get_sessions_by_user()`, `get_enabled_categories()`

**Dependencies:**
- SQLAlchemy async session (injected via FastAPI DI)
- Data models (User, Session, CounselorCategory)

**Technology Stack:** Repository pattern classes, SQLAlchemy 2.0 async

### Component Interaction Diagram

```mermaid
graph TB
    subgraph "API Layer"
        AuthRouter[Auth Router]
        CounselorRouter[Counselor Router]
        VoiceRouter[Voice Session Router]
        VideoRouter[Video Session Router]
        SessionRouter[Session History Router]
    end
    
    subgraph "Service Layer"
        AuthService[Authentication Service]
        VoiceService[Voice Session Service]
        VideoService[Video Session Service]
        SessionService[Session History Service]
    end
    
    subgraph "Adapter Layer"
        DailyAdapter[Daily.co Adapter]
        LiveKitAdapter[LiveKit Adapter]
        BPAdapter[Beyond Presence Adapter]
        LLMAdapter[LLM Adapter]
    end
    
    subgraph "Data Layer"
        UserRepo[User Repository]
        SessionRepo[Session Repository]
        CategoryRepo[Counselor Category Repository]
        DB[(PostgreSQL)]
    end
    
    AuthRouter --> AuthService
    CounselorRouter --> CategoryRepo
    VoiceRouter --> VoiceService
    VideoRouter --> VideoService
    SessionRouter --> SessionService
    
    AuthService --> UserRepo
    VoiceService --> DailyAdapter
    VoiceService --> SessionRepo
    VideoService --> LiveKitAdapter
    VideoService --> BPAdapter
    VideoService --> SessionRepo
    SessionService --> SessionRepo
    
    UserRepo --> DB
    SessionRepo --> DB
    CategoryRepo --> DB
    
    DailyAdapter -.->|External API| Daily[Daily.co]
    LiveKitAdapter -.->|External API| LiveKit[LiveKit]
    BPAdapter -.->|External API| BP[Beyond Presence]
    LLMAdapter -.->|External API| LLM[Gemini/GPT-4]
    
    VoiceService --> LLMAdapter
    VideoService --> LLMAdapter
    
    style AuthService fill:#4A90E2,color:#fff
    style VoiceService fill:#6FCF97,color:#fff
    style VideoService fill:#6FCF97,color:#fff
    style SessionService fill:#6FCF97,color:#fff
    style DB fill:#336791,color:#fff
```

---

## External APIs

### Daily.co API

- **Purpose:** WebRTC infrastructure for voice calling sessions
- **Documentation:** https://docs.daily.co/reference/rest-api
- **Base URL(s):** `https://api.daily.co/v1`
- **Authentication:** Bearer token via `DAILY_API_KEY` environment variable
- **Rate Limits:** 100 requests/minute (standard plan)

**Key Endpoints Used:**
- `POST /rooms` - Create temporary voice call room (max_participants=2, enable_chat=true)
- `POST /meeting-tokens` - Generate user and bot tokens with room access
- `DELETE /rooms/{room_name}` - Clean up room after session ends

**Integration Notes:** 
- Rooms configured with 1-hour expiration for security
- Bot tokens include `is_owner: true` for full control
- User tokens restricted to `audio: true, video: false` for voice-only sessions

### LiveKit API

- **Purpose:** WebRTC infrastructure for video calling sessions with avatar streaming
- **Documentation:** https://docs.livekit.io/home/server/api/
- **Base URL(s):** `wss://[project].livekit.cloud`
- **Authentication:** JWT tokens signed with API secret
- **Rate Limits:** 1000 requests/minute (standard plan)

**Key Endpoints Used:**
- `CreateRoom` - Create video session room
- `CreateToken` - Generate access tokens with participant permissions
- `UpdateParticipant` - Modify avatar stream settings during session

**Integration Notes:**
- Rooms support adaptive bitrate for quality degradation scenarios
- Avatar participant joins with `canPublish: true, canSubscribe: false`
- Student participant joins with `canPublish: true, canSubscribe: true` for audio input

### Beyond Presence API

- **Purpose:** AI-powered avatar generation with lip-sync and emotional expressions
- **Documentation:** https://docs.beyondpresence.com/api (assumed URL)
- **Base URL(s):** `https://api.beyondpresence.com/v1`
- **Authentication:** API key via `BEYOND_PRESENCE_API_KEY` header
- **Rate Limits:** 50 concurrent avatars (enterprise plan)

**Key Endpoints Used:**
- `POST /avatars/start` - Initiate avatar session with persona configuration
- `POST /avatars/{id}/stream` - Connect avatar to LiveKit room
- `DELETE /avatars/{id}` - Terminate avatar and free resources

**Integration Notes:**
- Avatar pre-configured with counselor persona (category-specific)
- Lip-sync latency <100ms requirement enforced via `latency_mode: low`
- Emotional expressions controlled by LLM sentiment analysis

### Deepgram API

- **Purpose:** Real-time speech-to-text transcription for voice sessions
- **Documentation:** https://developers.deepgram.com/docs
- **Base URL(s):** `wss://api.deepgram.com/v1/listen`
- **Authentication:** API key via `DEEPGRAM_API_KEY` header
- **Rate Limits:** Unlimited (pay-per-use)

**Key Endpoints Used:**
- WebSocket streaming endpoint with `model=nova-2`, `language=en-US`, `punctuate=true`

**Integration Notes:**
- Integrated via PipeCat SDK, not called directly by backend
- PipeCat handles WebSocket connection and transcript aggregation
- Transcripts stored in Session model after each utterance

### Cartesia API

- **Purpose:** High-quality text-to-speech synthesis for counselor responses
- **Documentation:** https://docs.cartesia.ai/api-reference
- **Base URL(s):** `https://api.cartesia.ai/v1`
- **Authentication:** API key via `CARTESIA_API_KEY` header
- **Rate Limits:** 500 requests/minute

**Key Endpoints Used:**
- `POST /tts/stream` - Generate streaming audio from text with Sonic-English voice

**Integration Notes:**
- Integrated via PipeCat SDK for low-latency streaming
- Voice parameters: `speed: 1.0`, `emotion: supportive`, `prosody: conversational`
- Audio format: PCM 16kHz mono for WebRTC compatibility

### Google Gemini API

- **Purpose:** Primary LLM for counseling conversation generation
- **Documentation:** https://ai.google.dev/docs
- **Base URL(s):** `https://generativelanguage.googleapis.com/v1`
- **Authentication:** API key via `GOOGLE_API_KEY` query parameter
- **Rate Limits:** 60 requests/minute (free tier), higher for paid

**Key Endpoints Used:**
- `POST /models/gemini-2.0-flash:generateContent` - Generate counselor responses with streaming

**Integration Notes:**
- System prompt includes counselor category persona and safety guidelines
- Streaming enabled for lower latency in real-time conversations
- Fallback to OpenAI GPT-4 if error rate >10% in 5-minute window

### OpenAI API

- **Purpose:** Fallback LLM if Gemini unavailable or experiencing issues
- **Documentation:** https://platform.openai.com/docs/api-reference
- **Base URL(s):** `https://api.openai.com/v1`
- **Authentication:** Bearer token via `OPENAI_API_KEY` header
- **Rate Limits:** 3500 requests/minute (tier 3)

**Key Endpoints Used:**
- `POST /chat/completions` - Generate counselor responses with `gpt-4-turbo-preview` model

**Integration Notes:**
- Identical prompt structure to Gemini for consistency
- Circuit breaker monitors both LLMs independently
- Cost approximately 3x higher than Gemini per request

---

## Core Workflows

### Student Authentication Flow

```mermaid
sequenceDiagram
    actor Student
    participant Frontend
    participant AuthRouter
    participant AuthService
    participant UserRepo
    participant DB
    
    Student->>Frontend: Enter credentials
    Frontend->>AuthRouter: POST /api/auth/login {username, password}
    AuthRouter->>AuthService: validate_credentials()
    AuthService->>UserRepo: get_user_by_username()
    UserRepo->>DB: SELECT * FROM users WHERE username=?
    DB-->>UserRepo: User record
    UserRepo-->>AuthService: User object
    
    alt User not found
        AuthService-->>AuthRouter: 401 Unauthorized
        AuthRouter-->>Frontend: Invalid credentials error
        Frontend-->>Student: Display error message
    else User is blocked
        AuthService-->>AuthRouter: 403 Forbidden
        AuthRouter-->>Frontend: Account blocked error
        Frontend-->>Student: Contact support message
    else Valid credentials
        AuthService->>AuthService: verify_password(password, hash)
        AuthService->>AuthService: generate_jwt_token(user_id)
        AuthService-->>AuthRouter: JWT token
        AuthRouter-->>Frontend: Set httpOnly cookie + token
        Frontend->>Frontend: Store auth state
        Frontend-->>Student: Redirect to dashboard
    end
```

### Voice Calling Session Flow

```mermaid
sequenceDiagram
    actor Student
    participant Frontend
    participant VoiceRouter
    participant VoiceService
    participant DailyAdapter
    participant Daily.co
    participant PipeCat
    participant SessionRepo
    participant DB
    
    Student->>Frontend: Click "Voice Call" on Health counselor
    Frontend->>VoiceRouter: POST /api/voice/create-room {category: "Health"}
    VoiceRouter->>VoiceService: create_voice_session()
    
    VoiceService->>DailyAdapter: create_room()
    DailyAdapter->>Daily.co: POST /rooms {properties}
    Daily.co-->>DailyAdapter: room_url, room_name
    
    VoiceService->>DailyAdapter: create_tokens(room_name)
    DailyAdapter->>Daily.co: POST /meeting-tokens
    Daily.co-->>DailyAdapter: user_token, bot_token
    
    VoiceService->>SessionRepo: create_session(user_id, "Health", "voice")
    SessionRepo->>DB: INSERT INTO sessions
    DB-->>SessionRepo: session_id
    
    VoiceService->>PipeCat: spawn_bot(room_url, bot_token, "Health" prompt)
    Note over PipeCat: Bot joins room, connects Deepgram+Cartesia+Gemini
    
    VoiceService-->>VoiceRouter: {room_url, user_token, session_id}
    VoiceRouter-->>Frontend: Session credentials
    
    Frontend->>Daily.co: Join room with user_token
    Daily.co-->>Frontend: WebRTC connection established
    
    loop Conversation
        Student->>Daily.co: Speak (audio stream)
        Daily.co->>PipeCat: Forward audio
        PipeCat->>Deepgram: STT transcription
        Deepgram-->>PipeCat: Text transcript
        PipeCat->>Gemini: Generate response with counselor prompt
        Gemini-->>PipeCat: Response text
        PipeCat->>Cartesia: TTS synthesis
        Cartesia-->>PipeCat: Audio stream
        PipeCat->>Daily.co: Send audio response
        Daily.co-->>Frontend: Play audio to student
        Frontend->>Frontend: Display transcript in real-time
    end
    
    Student->>Frontend: Click "End Session"
    Frontend->>VoiceRouter: POST /api/voice/end-session {session_id}
    VoiceRouter->>VoiceService: end_session()
    VoiceService->>PipeCat: Terminate bot process
    VoiceService->>SessionRepo: update_session(ended_at, transcript)
    SessionRepo->>DB: UPDATE sessions SET ended_at=?, transcript=?
    VoiceService->>DailyAdapter: delete_room(room_name)
    DailyAdapter->>Daily.co: DELETE /rooms/{room_name}
    VoiceService-->>VoiceRouter: Success
    VoiceRouter-->>Frontend: Session ended
    Frontend-->>Student: Redirect to session history
```

### Video Calling Session Flow

```mermaid
sequenceDiagram
    actor Student
    participant Frontend
    participant VideoRouter
    participant VideoService
    participant LiveKitAdapter
    participant BPAdapter
    participant LiveKit
    participant BeyondPresence
    participant SessionRepo
    
    Student->>Frontend: Click "Video Call" on Career counselor
    Frontend->>VideoRouter: POST /api/video/create-room {category: "Career"}
    VideoRouter->>VideoService: create_video_session()
    
    VideoService->>LiveKitAdapter: create_room()
    LiveKitAdapter->>LiveKit: CreateRoom RPC
    LiveKit-->>LiveKitAdapter: room_name, url
    
    VideoService->>LiveKitAdapter: create_tokens(room_name)
    LiveKitAdapter-->>VideoService: user_token, avatar_token
    
    VideoService->>BPAdapter: start_avatar({persona: "Career", room: room_name, token: avatar_token})
    BPAdapter->>BeyondPresence: POST /avatars/start
    BeyondPresence->>LiveKit: Join room as avatar participant
    BeyondPresence-->>BPAdapter: avatar_id, status: "streaming"
    
    VideoService->>SessionRepo: create_session(user_id, "Career", "video")
    SessionRepo-->>VideoService: session_id
    
    VideoService-->>VideoRouter: {room_url, user_token, session_id}
    VideoRouter-->>Frontend: Session credentials
    
    Frontend->>LiveKit: Join room with user_token
    LiveKit-->>Frontend: WebRTC connection + avatar video stream
    
    loop Conversation with Avatar
        Student->>LiveKit: Speak (audio stream)
        LiveKit->>BeyondPresence: Forward audio
        BeyondPresence->>Gemini: Generate response with Career counselor prompt
        Gemini-->>BeyondPresence: Response text
        BeyondPresence->>BeyondPresence: Generate lip-sync + expression
        BeyondPresence->>LiveKit: Video stream with talking avatar
        LiveKit-->>Frontend: Display avatar video + audio
        Frontend->>Frontend: Display transcript in sidebar
    end
    
    Student->>Frontend: Click "End Session"
    Frontend->>VideoRouter: POST /api/video/end-session {session_id}
    VideoRouter->>VideoService: end_session()
    VideoService->>BPAdapter: stop_avatar(avatar_id)
    BPAdapter->>BeyondPresence: DELETE /avatars/{avatar_id}
    VideoService->>SessionRepo: update_session(ended_at, transcript)
    VideoService-->>VideoRouter: Success
    Frontend-->>Student: Redirect to session history
```

---

## REST API Spec

```yaml
openapi: 3.0.0
info:
  title: College Student Counseling Platform API
  version: 1.0.0
  description: Backend API for AI-powered counseling sessions via voice and video

servers:
  - url: https://api.counseling-platform.example.com
    description: Production server
  - url: http://localhost:8000
    description: Local development server

components:
  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: access_token
      
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        username:
          type: string
          example: "\\COLLEGE\\jdoe"
        is_blocked:
          type: boolean
        created_at:
          type: string
          format: date-time
          
    Session:
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        counselor_category:
          type: string
          enum: [Health, Career, Academic, Financial, Social, Personal Development]
        mode:
          type: string
          enum: [voice, video]
        started_at:
          type: string
          format: date-time
        ended_at:
          type: string
          format: date-time
          nullable: true
        duration_seconds:
          type: integer
        transcript:
          type: string
        connection_quality:
          type: string
          enum: [excellent, good, fair, poor]
          nullable: true
          
    CounselorCategory:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        icon_name:
          type: string
        enabled:
          type: boolean
          
    Error:
      type: object
      properties:
        detail:
          type: string
        code:
          type: string
          
security:
  - cookieAuth: []

paths:
  /api/auth/login:
    post:
      summary: Authenticate student and issue JWT token
      tags: [Authentication]
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [username, password]
              properties:
                username:
                  type: string
                  example: "\\COLLEGE\\jdoe"
                password:
                  type: string
                  format: password
      responses:
        '200':
          description: Login successful
          headers:
            Set-Cookie:
              schema:
                type: string
                example: access_token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                    example: bearer
                  user:
                    $ref: '#/components/schemas/User'
        '401':
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '403':
          description: Account blocked
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
                
  /api/auth/logout:
    post:
      summary: Clear authentication session
      tags: [Authentication]
      responses:
        '200':
          description: Logout successful
          headers:
            Set-Cookie:
              schema:
                type: string
                example: access_token=; Max-Age=0
                
  /api/auth/me:
    get:
      summary: Get current authenticated user
      tags: [Authentication]
      responses:
        '200':
          description: User information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: Not authenticated
          
  /api/counselors/categories:
    get:
      summary: List enabled counselor categories
      tags: [Counselors]
      responses:
        '200':
          description: List of categories
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CounselorCategory'
                  
  /api/voice/create-room:
    post:
      summary: Create voice calling session
      tags: [Voice Sessions]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [counselor_category]
              properties:
                counselor_category:
                  type: string
                  enum: [Health, Career, Academic, Financial, Social, Personal Development]
      responses:
        '200':
          description: Room created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  room_url:
                    type: string
                    example: "https://example.daily.co/room-name"
                  user_token:
                    type: string
                  session_id:
                    type: string
                    format: uuid
        '500':
          description: Failed to create room
          
  /api/voice/end-session:
    post:
      summary: End voice calling session
      tags: [Voice Sessions]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [session_id]
              properties:
                session_id:
                  type: string
                  format: uuid
                transcript:
                  type: string
                  description: Final transcript from frontend
      responses:
        '200':
          description: Session ended successfully
          
  /api/video/create-room:
    post:
      summary: Create video calling session with avatar
      tags: [Video Sessions]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [counselor_category]
              properties:
                counselor_category:
                  type: string
                  enum: [Health, Career, Academic, Financial, Social, Personal Development]
      responses:
        '200':
          description: Room created and avatar started
          content:
            application/json:
              schema:
                type: object
                properties:
                  room_url:
                    type: string
                  user_token:
                    type: string
                  session_id:
                    type: string
                    format: uuid
                  avatar_id:
                    type: string
                    
  /api/video/end-session:
    post:
      summary: End video calling session
      tags: [Video Sessions]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [session_id]
              properties:
                session_id:
                  type: string
                  format: uuid
                avatar_id:
                  type: string
                transcript:
                  type: string
      responses:
        '200':
          description: Session ended successfully
          
  /api/sessions:
    get:
      summary: List user's past counseling sessions
      tags: [Session History]
      parameters:
        - name: category
          in: query
          schema:
            type: string
            enum: [Health, Career, Academic, Financial, Social, Personal Development]
        - name: mode
          in: query
          schema:
            type: string
            enum: [voice, video]
        - name: start_date
          in: query
          schema:
            type: string
            format: date
        - name: end_date
          in: query
          schema:
            type: string
            format: date
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: per_page
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Paginated session list
          content:
            application/json:
              schema:
                type: object
                properties:
                  sessions:
                    type: array
                    items:
                      $ref: '#/components/schemas/Session'
                  total:
                    type: integer
                  page:
                    type: integer
                  per_page:
                    type: integer
                    
  /api/sessions/{session_id}:
    get:
      summary: Get detailed session with full transcript
      tags: [Session History]
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Session details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'
        '404':
          description: Session not found
          
    delete:
      summary: Delete session record
      tags: [Session History]
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: Session deleted successfully
        '404':
          description: Session not found
          
  /api/sessions/{session_id}/download:
    get:
      summary: Download session transcript as text file
      tags: [Session History]
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Transcript file
          content:
            text/plain:
              schema:
                type: string
        '404':
          description: Session not found
```

---

## Database Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE counselor_category_enum AS ENUM (
  'Health',
  'Career', 
  'Academic',
  'Financial',
  'Social',
  'Personal Development'
);

CREATE TYPE session_mode_enum AS ENUM ('voice', 'video');

CREATE TYPE connection_quality_enum AS ENUM (
  'excellent',
  'good',
  'fair',
  'poor'
);

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_blocked BOOLEAN DEFAULT FALSE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  -- Constraints
  CONSTRAINT username_format_check CHECK (username ~ '^\\\\[^\\\\]+\\\\[^\\\\]+$')
);

-- Index for fast username lookups during login
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_blocked ON users(is_blocked) WHERE is_blocked = TRUE;

-- Sessions table
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  counselor_category counselor_category_enum NOT NULL,
  mode session_mode_enum NOT NULL,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  ended_at TIMESTAMP WITH TIME ZONE,
  duration_seconds INTEGER GENERATED ALWAYS AS (
    EXTRACT(EPOCH FROM (ended_at - started_at))::INTEGER
  ) STORED,
  transcript TEXT,
  room_name VARCHAR(255),
  connection_quality connection_quality_enum,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  -- Constraints
  CONSTRAINT ended_after_started CHECK (ended_at IS NULL OR ended_at > started_at)
);

-- Indexes for session queries
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);
CREATE INDEX idx_sessions_category ON sessions(counselor_category);
CREATE INDEX idx_sessions_mode ON sessions(mode);
CREATE INDEX idx_sessions_user_started ON sessions(user_id, started_at DESC);

-- Composite index for common filter queries
CREATE INDEX idx_sessions_user_category_mode ON sessions(
  user_id,
  counselor_category,
  mode,
  started_at DESC
);

-- Counselor categories table
CREATE TABLE counselor_categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT NOT NULL,
  icon_name VARCHAR(50) NOT NULL,
  system_prompt TEXT NOT NULL,
  enabled BOOLEAN DEFAULT TRUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index for enabled categories lookup
CREATE INDEX idx_counselor_categories_enabled ON counselor_categories(enabled) WHERE enabled = TRUE;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic updated_at
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_counselor_categories_updated_at
  BEFORE UPDATE ON counselor_categories
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Seed data for counselor categories
INSERT INTO counselor_categories (name, description, icon_name, system_prompt, enabled) VALUES
('Health', 'Mental health, stress management, wellness, and self-care support', 'heart-pulse', 
 'You are a supportive health counselor specializing in student wellness. Focus on mental health, stress management, sleep hygiene, and healthy habits. Be empathetic and non-judgmental. If a student expresses suicidal ideation, immediately provide the National Suicide Prevention Lifeline: 988.', 
 TRUE),
 
('Career', 'Career exploration, job search strategies, resume help, and interview prep', 'briefcase',
 'You are an experienced career counselor helping college students navigate their professional futures. Provide guidance on career paths, job search strategies, resume writing, and interview preparation. Ask probing questions to understand their interests, skills, and goals.',
 TRUE),
 
('Academic', 'Study strategies, time management, course selection, and academic planning', 'graduation-cap',
 'You are an academic advisor specializing in student success. Help with study strategies, time management, course selection, and academic planning. Be encouraging and practical in your advice. Focus on evidence-based learning techniques.',
 TRUE),
 
('Financial', 'Budgeting, student loans, financial aid, and money management', 'dollar-sign',
 'You are a financial counselor educated in personal finance for college students. Provide guidance on budgeting, managing student loans, understanding financial aid, and building healthy money habits. Be non-judgmental about financial situations.',
 TRUE),
 
('Social', 'Relationships, communication skills, campus involvement, and social well-being', 'users',
 'You are a counselor focused on social and interpersonal development. Help students navigate friendships, romantic relationships, roommate conflicts, and campus involvement. Provide communication strategies and encourage healthy social connections.',
 TRUE),
 
('Personal Development', 'Goal setting, self-awareness, life skills, and personal growth', 'star',
 'You are a personal development coach for college students. Focus on goal setting, self-awareness, building life skills, and fostering personal growth. Help students discover their values, strengths, and areas for development. Be motivating and forward-thinking.',
 TRUE);

-- View for active sessions (currently in progress)
CREATE VIEW active_sessions AS
SELECT 
  s.*,
  u.username
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE s.ended_at IS NULL;

-- View for session statistics per user
CREATE VIEW user_session_stats AS
SELECT
  user_id,
  COUNT(*) as total_sessions,
  COUNT(*) FILTER (WHERE mode = 'voice') as voice_sessions,
  COUNT(*) FILTER (WHERE mode = 'video') as video_sessions,
  AVG(duration_seconds) as avg_duration_seconds,
  MAX(started_at) as last_session_at
FROM sessions
WHERE ended_at IS NOT NULL
GROUP BY user_id;
```

**Schema Design Notes:**

1. **UUID Primary Keys:** Used for all tables to avoid sequential ID leakage and enable distributed systems if needed.

2. **Enum Types:** PostgreSQL enums for counselor_category and mode ensure data integrity and efficient storage.

3. **Computed Column:** `duration_seconds` is generated automatically from `started_at` and `ended_at` to avoid inconsistencies.

4. **Indexes Strategy:**
   - Single-column indexes for common filters (user_id, category, mode)
   - Composite index for complex queries (user + category + mode + date sorting)
   - Partial index on `is_blocked=TRUE` since most users aren't blocked
   - DESC index on `started_at` for efficient session history pagination

5. **Cascading Deletes:** Sessions cascade delete with users (GDPR right to erasure).

6. **Timestamp with Timezone:** All timestamps use `TIMESTAMP WITH TIME ZONE` for proper multi-timezone support.

7. **Audit Triggers:** Automatic `updated_at` triggers on users and counselor_categories tables.

8. **Views:** Pre-defined views for common queries (active sessions, user statistics) to simplify application code.

9. **Transcript Storage:** Text field adequate for MVP; consider moving to S3 with DB reference if transcripts exceed PostgreSQL text limits (~1GB theoretical, ~10MB practical).

---

## Source Tree

```plaintext
college-counseling-platform/
├── .github/
│   └── workflows/
│       ├── ci-frontend.yml           # Frontend CI: lint, typecheck, test
│       ├── ci-backend.yml            # Backend CI: lint, typecheck, test
│       └── deploy.yml                # CD: build Docker images, deploy to Railway
│
├── packages/
│   ├── frontend/                     # Next.js 14 application
│   │   ├── app/                      # App Router structure
│   │   │   ├── layout.tsx           # Root layout with auth provider
│   │   │   ├── page.tsx             # Login page (/)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx         # Main dashboard
│   │   │   ├── voice-session/
│   │   │   │   └── page.tsx         # Voice calling view
│   │   │   ├── video-session/
│   │   │   │   └── page.tsx         # Video calling view
│   │   │   └── sessions/
│   │   │       ├── page.tsx         # Session history list
│   │   │       └── [id]/
│   │   │           └── page.tsx     # Session detail/transcript
│   │   ├── components/              # React components
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── AuthProvider.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── CounselorCard.tsx
│   │   │   ├── voice/
│   │   │   │   ├── VoiceClient.tsx
│   │   │   │   ├── AudioWaveform.tsx
│   │   │   │   └── TranscriptPanel.tsx
│   │   │   ├── video/
│   │   │   │   ├── VideoClient.tsx
│   │   │   │   ├── AvatarPlayer.tsx
│   │   │   │   └── VideoControls.tsx
│   │   │   └── sessions/
│   │   │       ├── SessionCard.tsx
│   │   │       ├── SessionFilters.tsx
│   │   │       └── TranscriptView.tsx
│   │   ├── lib/                     # Utility functions
│   │   │   ├── api-client.ts       # API client with auth handling
│   │   │   ├── daily-client.ts     # Daily.co SDK wrapper
│   │   │   ├── livekit-client.ts   # LiveKit SDK wrapper
│   │   │   └── utils.ts            # General utilities
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useVoiceSession.ts
│   │   │   └── useVideoSession.ts
│   │   ├── types/                   # TypeScript types
│   │   │   └── index.ts            # Re-exports from shared package
│   │   ├── styles/
│   │   │   └── globals.css         # Tailwind imports + custom styles
│   │   ├── public/                  # Static assets
│   │   │   └── icons/              # Counselor category icons
│   │   ├── .eslintrc.json
│   │   ├── next.config.js
│   │   ├── package.json
│   │   ├── tailwind.config.ts
│   │   └── tsconfig.json
│   │
│   ├── backend/                      # FastAPI application
│   │   ├── app/
│   │   │   ├── main.py              # FastAPI app initialization
│   │   │   ├── config.py            # Settings from environment variables
│   │   │   ├── dependencies.py      # FastAPI dependency injection
│   │   │   ├── middleware/
│   │   │   │   ├── auth.py         # JWT authentication middleware
│   │   │   │   ├── cors.py         # CORS configuration
│   │   │   │   └── logging.py      # Request logging
│   │   │   ├── routers/             # API route handlers
│   │   │   │   ├── auth.py         # /api/auth/* endpoints
│   │   │   │   ├── counselors.py   # /api/counselors/* endpoints
│   │   │   │   ├── voice.py        # /api/voice/* endpoints
│   │   │   │   ├── video.py        # /api/video/* endpoints
│   │   │   │   └── sessions.py     # /api/sessions/* endpoints
│   │   │   ├── services/            # Business logic layer
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── voice_service.py
│   │   │   │   ├── video_service.py
│   │   │   │   └── session_service.py
│   │   │   ├── adapters/            # External API wrappers
│   │   │   │   ├── daily_adapter.py
│   │   │   │   ├── livekit_adapter.py
│   │   │   │   ├── beyond_presence_adapter.py
│   │   │   │   └── llm_adapter.py
│   │   │   ├── repositories/        # Data access layer
│   │   │   │   ├── base.py         # Base repository with common methods
│   │   │   │   ├── user_repository.py
│   │   │   │   ├── session_repository.py
│   │   │   │   └── counselor_category_repository.py
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   │   ├── base.py         # Base model class
│   │   │   │   ├── user.py
│   │   │   │   ├── session.py
│   │   │   │   └── counselor_category.py
│   │   │   ├── schemas/             # Pydantic request/response schemas
│   │   │   │   ├── auth.py
│   │   │   │   ├── session.py
│   │   │   │   ├── counselor.py
│   │   │   │   └── voice.py
│   │   │   ├── core/                # Core utilities
│   │   │   │   ├── security.py     # JWT, password hashing
│   │   │   │   ├── database.py     # Database connection
│   │   │   │   └── logging.py      # Loguru configuration
│   │   │   ├── pipecat/             # PipeCat bot management
│   │   │   │   ├── bot_spawner.py  # Subprocess management
│   │   │   │   ├── bot_config.py   # Bot configuration templates
│   │   │   │   └── prompts/        # Counselor system prompts
│   │   │   └── scripts/             # Utility scripts
│   │   │       ├── seed_db.py      # Database seeding
│   │   │       └── purge_old_transcripts.py  # 90-day purge job
│   │   ├── alembic/                 # Database migrations
│   │   │   ├── versions/           # Migration files
│   │   │   └── env.py              # Alembic configuration
│   │   ├── tests/                   # Pytest tests
│   │   │   ├── unit/
│   │   │   │   ├── test_auth_service.py
│   │   │   │   ├── test_repositories.py
│   │   │   │   └── test_adapters.py
│   │   │   ├── integration/
│   │   │   │   ├── test_auth_endpoints.py
│   │   │   │   ├── test_voice_endpoints.py
│   │   │   │   └── test_session_endpoints.py
│   │   │   └── conftest.py         # Pytest fixtures
│   │   ├── .env.example
│   │   ├── alembic.ini
│   │   ├── pyproject.toml           # Poetry or pip-tools config
│   │   ├── pytest.ini
│   │   └── requirements.txt
│   │
│   └── shared/                       # Shared TypeScript types
│       ├── src/
│       │   ├── api-types.ts        # API request/response types
│       │   ├── models.ts           # Data model types (User, Session, etc.)
│       │   └── index.ts            # Re-exports
│       ├── package.json
│       └── tsconfig.json
│
├── scripts/                          # Monorepo management scripts
│   ├── setup-dev.sh                # Initial development setup
│   ├── generate-types.py           # Generate TS types from Pydantic schemas
│   └── run-tests.sh                # Run all tests across packages
│
├── docker/
│   ├── Dockerfile.frontend         # Frontend production image
│   ├── Dockerfile.backend          # Backend production image
│   └── docker-compose.yml          # Local development environment
│
├── .gitignore
├── .env.example
├── pnpm-workspace.yaml             # pnpm workspace configuration
├── turbo.json                      # Turborepo pipeline configuration
├── package.json                    # Root package.json with workspace scripts
└── README.md                       # Project documentation
```

**Directory Structure Rationale:**

1. **Monorepo with Packages:** Clear separation of frontend, backend, and shared code while enabling atomic commits and type sharing.

2. **Frontend App Router:** Next.js 14 App Router structure with co-located components per route for better organization.

3. **Backend Layered Architecture:** Clear separation of routers (HTTP), services (business logic), adapters (external APIs), and repositories (data access).

4. **Shared Package:** TypeScript types shared between frontend and backend to ensure type safety across API boundary.

5. **PipeCat Integration:** Dedicated directory for bot spawning logic and counselor prompts, isolating AI integration complexity.

6. **Tests Parallel to Source:** Backend tests mirror source structure for easy navigation.

7. **Scripts Directory:** Monorepo-level scripts for common operations (dev setup, type generation, testing).

8. **Docker Setup:** Separate Dockerfiles for frontend/backend enable independent deployment and scaling.

9. **Alembic Migrations:** Standard location for SQLAlchemy migrations with version control.

10. **Configuration Files:** Root-level configs (pnpm-workspace, turbo.json) for monorepo tooling.

---

## Infrastructure and Deployment

### Infrastructure as Code

- **Tool:** Railway CLI + Docker Compose (for local dev)
- **Location:** `docker/` directory for Dockerfiles, `docker-compose.yml` for local orchestration
- **Approach:** Railway uses Dockerfile detection for automatic deployment; no explicit IaC files needed for MVP. Future migration to Terraform if moving to AWS/GCP.

### Deployment Strategy

- **Strategy:** Continuous Deployment with automatic rollbacks
- **CI/CD Platform:** GitHub Actions
- **Pipeline Configuration:** `.github/workflows/`

**Pipeline Stages:**

1. **CI Pipeline (on PR):**
   - Checkout code
   - Install dependencies (pnpm install)
   - Lint frontend (ESLint) and backend (Ruff)
   - Type check (TypeScript tsc, mypy)
   - Run unit tests (Vitest, pytest)
   - Run integration tests (pytest with TestClient)
   - Build Docker images (validation only)

2. **CD Pipeline (on merge to main):**
   - Run full CI pipeline
   - Build Docker images (frontend and backend)
   - Push images to Railway container registry
   - Deploy to Railway (automatic via Railway GitHub integration)
   - Run smoke tests against deployed environment
   - Notify team via Slack/Discord webhook

### Environments

- **Development:** Local Docker Compose environment with hot-reload
  - PostgreSQL in container
  - Frontend on `localhost:3000`
  - Backend on `localhost:8000`
  - Shared network for inter-service communication

- **Staging:** Railway staging project (future, post-MVP)
  - Separate Railway project with production-like configuration
  - Used for QA testing and client demos
  - Seeded with test data

- **Production:** Railway production project
  - Managed PostgreSQL with automated backups
  - Auto-scaling enabled (2-10 instances based on CPU)
  - Custom domain with automatic HTTPS
  - Environment variables for all secrets

### Environment Promotion Flow

```
Development (Local) → Pull Request (CI checks) → Main Branch (Auto-deploy to Production)
```

For post-MVP with staging:
```
Development → PR → Main (Staging) → Manual approval → Production tag → Production deploy
```

### Rollback Strategy

- **Primary Method:** Railway automatic rollback on health check failure
  - Health check endpoint: `GET /api/health` (backend), `GET /` (frontend)
  - Failure threshold: 3 consecutive failures in 30 seconds
  - Automatic rollback to previous deployment

- **Manual Rollback:** Railway CLI or dashboard
  ```bash
  railway rollback <deployment-id>
  ```

- **Trigger Conditions:**
  - Health check failures
  - Error rate >5% in first 5 minutes after deployment
  - Manual trigger by on-call engineer

- **Recovery Time Objective:** <5 minutes from detection to rollback completion

---

## Error Handling Strategy

### General Approach

- **Error Model:** Structured error responses with `detail` and `code` fields
- **Exception Hierarchy:**
  - `AppException` (base) - All application exceptions inherit from this
  - `AuthenticationError` - Invalid credentials, blocked accounts
  - `AuthorizationError` - Insufficient permissions
  - `ValidationError` - Invalid input data (Pydantic already handles this)
  - `ExternalServiceError` - Failures from Daily.co, LiveKit, etc.
  - `DatabaseError` - Database connection or query failures
  
- **Error Propagation:** 
  - Services raise domain exceptions
  - Routers catch exceptions and convert to HTTP responses
  - Global exception handlers for uncaught exceptions

### Logging Standards

- **Library:** Loguru 0.7.2 (backend), custom logger (frontend)
- **Format:** JSON structured logs with fields:
  ```json
  {
    "timestamp": "2025-12-19T10:30:00Z",
    "level": "INFO",
    "correlation_id": "uuid-v4",
    "service": "backend|frontend",
    "user_id": "uuid-v4",
    "endpoint": "/api/voice/create-room",
    "message": "Voice session created",
    "duration_ms": 245
  }
  ```
- **Levels:** 
  - `DEBUG` - Detailed diagnostic information (disabled in production)
  - `INFO` - General informational messages (session created, user logged in)
  - `WARNING` - Recoverable errors (external API retry, degraded performance)
  - `ERROR` - Errors requiring attention (external API failures, database errors)
  - `CRITICAL` - System failures requiring immediate action
  
- **Required Context:**
  - **Correlation ID:** UUID generated per request, passed through all log entries
  - **Service Context:** Service name (backend/frontend), environment (dev/prod)
  - **User Context:** User ID if authenticated, never log PII (passwords, transcripts in logs)

### Error Handling Patterns

#### External API Errors

- **Retry Policy:**
  - Exponential backoff: 1s, 2s, 4s delays
  - Max 3 retries for idempotent operations (GET requests)
  - No retries for non-idempotent operations (POST create-room) - fail fast
  
- **Circuit Breaker:**
  - Library: `pybreaker`
  - Failure threshold: 5 failures in 60 seconds
  - Open state duration: 60 seconds
  - Half-open state: Allow 1 request to test recovery
  
- **Timeout Configuration:**
  - Daily.co API: 10 second timeout
  - LiveKit API: 10 second timeout
  - Beyond Presence API: 15 second timeout (avatar init slower)
  - LLM APIs: 30 second timeout (generation can be slow)
  
- **Error Translation:**
  - External 404 → `ExternalServiceError("Resource not found")`
  - External 429 → `ExternalServiceError("Rate limit exceeded, try again later")`
  - External 500/503 → `ExternalServiceError("Service temporarily unavailable")`
  - Circuit breaker open → `ExternalServiceError("Service unavailable, please try again soon")`

#### Business Logic Errors

- **Custom Exceptions:**
  - `InvalidCredentialsError` - Wrong username/password
  - `AccountBlockedError` - User account is blocked
  - `SessionNotFoundError` - Session ID doesn't exist or doesn't belong to user
  - `CounselorCategoryDisabledError` - Selected category is disabled
  
- **User-Facing Errors:**
  - Format: `{"detail": "Human-readable message", "code": "ERROR_CODE"}`
  - Example: `{"detail": "Your account has been blocked. Please contact support.", "code": "ACCOUNT_BLOCKED"}`
  
- **Error Codes:**
  - `AUTH_001` - Invalid credentials
  - `AUTH_002` - Account blocked
  - `AUTH_003` - Token expired
  - `SESSION_001` - Session not found
  - `SESSION_002` - Session already ended
  - `EXTERNAL_001` - Daily.co service unavailable
  - `EXTERNAL_002` - LiveKit service unavailable
  - `EXTERNAL_003` - LLM service unavailable

#### Data Consistency

- **Transaction Strategy:**
  - Use SQLAlchemy sessions with automatic commit/rollback
  - Transactions span single database operations (create user, create session)
  - No distributed transactions across services (external APIs are eventual consistency)
  
- **Compensation Logic:**
  - If PipeCat bot fails to spawn, delete session record (synchronous)
  - If Daily.co room creation succeeds but session insert fails, delete room (compensation)
  - Cleanup jobs run hourly to remove orphaned rooms (eventual consistency)
  
- **Idempotency:**
  - Session creation: Generate session ID client-side (UUID), server checks for duplicates
  - Room deletion: Idempotent (DELETE returns success even if room doesn't exist)
  - Transcript updates: Use session ID as idempotency key

---

## Coding Standards

**CRITICAL: These standards are MANDATORY for AI agents. Deviations will cause code review failures.**

### Core Standards

- **Languages & Runtimes:**
  - Backend: Python 3.11.7 with type hints on all function signatures
  - Frontend: TypeScript 5.3.3 with strict mode enabled, no `any` types
  
- **Style & Linting:**
  - Frontend: ESLint with Next.js config, Prettier for formatting
  - Backend: Ruff for linting/formatting (replaces Black + Flake8), mypy for type checking
  
- **Test Organization:**
  - Test files: `test_<module_name>.py` (backend), `<component>.test.tsx` (frontend)
  - Location: `tests/` directory parallel to source (backend), `__tests__/` next to component (frontend)

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Python Classes | PascalCase | `UserRepository`, `VoiceService` |
| Python Functions/Methods | snake_case | `create_voice_session()`, `get_user_by_username()` |
| Python Constants | UPPER_SNAKE_CASE | `JWT_SECRET_KEY`, `MAX_SESSION_DURATION` |
| Python Files/Modules | snake_case | `auth_service.py`, `daily_adapter.py` |
| TypeScript Interfaces/Types | PascalCase | `SessionResponse`, `CounselorCategory` |
| TypeScript Functions | camelCase | `createVoiceSession()`, `getUserById()` |
| React Components | PascalCase | `CounselorCard`, `TranscriptPanel` |
| React Hooks | camelCase with `use` prefix | `useAuth()`, `useVoiceSession()` |
| CSS Classes (Tailwind) | kebab-case | `counselor-card`, `transcript-panel` |

### Critical Rules

- **Never use `console.log` in production code** - Use `logger.info()` (backend) or custom logger (frontend)

- **All API responses must use Pydantic schemas** - No raw dictionaries returned from routers

- **Database queries must use repository pattern** - Never write raw SQL or direct ORM queries in routers/services

- **External API calls must use adapter classes** - No direct `httpx.post()` calls outside adapters

- **Secrets must never be hardcoded** - Always load from environment variables via `config.py`

- **JWT tokens must be in httpOnly cookies** - Never store JWT in localStorage or sessionStorage

- **User passwords must be hashed with bcrypt** - Never store plaintext passwords

- **All user inputs must be validated** - Use Pydantic schemas (backend) or Zod schemas (frontend)

- **Session transcripts must be encrypted at rest** - Use PostgreSQL pgcrypto extension or application-level encryption

- **Error messages must never leak sensitive data** - No stack traces or internal paths in API responses

- **All async functions must have proper error handling** - Use try/except in Python, try/catch in TypeScript

- **Database migrations must be reversible** - Every Alembic migration needs `upgrade()` and `downgrade()`

- **React components must use TypeScript** - No `.jsx` files, only `.tsx`

- **Tailwind classes must be used for styling** - No inline styles or CSS modules except for dynamic values

- **API endpoints must match OpenAPI spec** - Update spec when adding/changing endpoints

### Language-Specific Guidelines

#### Python Specifics

- **Async/Await:** All database operations and external API calls must use `async`/`await`
- **Type Hints:** Required on all function parameters and return types
- **Docstrings:** Use for public functions in services and adapters (Google style)
- **Imports:** Group into stdlib, third-party, local (separated by blank lines)
- **Error Handling:** Raise specific exceptions, never generic `Exception`

#### TypeScript Specifics

- **No Implicit Any:** Enable `noImplicitAny` in `tsconfig.json`
- **Strict Null Checks:** Enable `strictNullChecks` in `tsconfig.json`
- **Functional Components:** Use function declarations, not arrow functions for components
- **Hooks Rules:** Follow React Hooks rules (only call at top level, only in React functions)
- **Props Interface:** Define explicit interface for all component props

---

## Test Strategy and Standards

### Testing Philosophy

- **Approach:** Test-after for MVP (write tests alongside feature development, not strict TDD)
- **Coverage Goals:** 
  - Backend: 80% line coverage, 100% for critical paths (auth, session creation)
  - Frontend: 70% line coverage, focus on business logic and hooks
- **Test Pyramid:** 
  - 70% Unit tests (fast, isolated)
  - 20% Integration tests (API endpoints, database)
  - 10% E2E tests (critical user journeys only)

### Test Types and Organization

#### Unit Tests

- **Framework:** pytest 8.0.0 (backend), Vitest 1.2.0 (frontend)
- **File Convention:** 
  - Backend: `tests/unit/test_<module>.py`
  - Frontend: `components/<name>/__tests__/<name>.test.tsx`
- **Location:** 
  - Backend: `packages/backend/tests/unit/`
  - Frontend: `__tests__/` directory next to tested component
- **Mocking Library:** 
  - Backend: `pytest-mock` for mocking
  - Frontend: Vitest mocking utilities
- **Coverage Requirement:** 80% for backend services and repositories, 70% for frontend components

**AI Agent Requirements:**
- Generate tests for all public methods in services, repositories, and adapters
- Cover edge cases and error conditions (invalid input, external API failures)
- Follow AAA pattern (Arrange, Act, Assert) for test structure
- Mock all external dependencies (database, HTTP clients, external APIs)

#### Integration Tests

- **Scope:** API endpoints with real database and mocked external services
- **Location:** 
  - Backend: `packages/backend/tests/integration/`
- **Test Infrastructure:**
  - **Database:** Testcontainers PostgreSQL for integration tests (Docker container per test run)
  - **External APIs:** WireMock or `responses` library for stubbing HTTP responses
  - **Authentication:** Generate test JWT tokens for authenticated endpoint testing

**Example Test Structure:**
```python
# test_voice_endpoints.py
async def test_create_voice_room_success(test_client, mock_daily_adapter):
    # Arrange: Mock external API responses
    mock_daily_adapter.create_room.return_value = {"room_url": "...", "room_name": "..."}
    
    # Act: Call API endpoint
    response = await test_client.post("/api/voice/create-room", json={"counselor_category": "Health"})
    
    # Assert: Verify response and side effects
    assert response.status_code == 200
    assert "session_id" in response.json()
    mock_daily_adapter.create_room.assert_called_once()
```

#### End-to-End Tests

- **Framework:** Playwright 1.41.0
- **Scope:** Critical user journeys only (MVP has limited E2E due to WebRTC complexity)
  - Login → Dashboard → Voice call initiation (stops before WebRTC connection)
  - Login → Session history → View transcript
- **Environment:** Staging environment (future) or local dev environment
- **Test Data:** Seeded test users with known credentials

**E2E Tests Not Included in MVP:**
- Full voice/video call testing (WebRTC hard to automate reliably)
- Avatar lip-sync validation (requires manual QA)
- Real-time transcript accuracy (requires speech recognition validation)

### Test Data Management

- **Strategy:** Factory pattern for test data creation
- **Fixtures:** pytest fixtures for common test data (users, sessions, counselor categories)
- **Factories:** Use `factory_boy` library for generating test models
  ```python
  class UserFactory(factory.Factory):
      class Meta:
          model = User
      
      id = factory.Faker('uuid4')
      username = factory.Sequence(lambda n: f"\\COLLEGE\\user{n}")
      is_blocked = False
  ```
- **Cleanup:** Database rollback after each test (SQLAlchemy transactions)

### Continuous Testing

- **CI Integration:**
  - Unit tests run on every PR
  - Integration tests run on every PR
  - E2E tests run on merge to main (future, post-MVP)
  - Coverage reports posted as PR comments
  
- **Performance Tests:** Not included in MVP; consider JMeter or Locust post-MVP for load testing
  
- **Security Tests:** 
  - SAST: Bandit (Python) and ESLint security plugin (TypeScript) in CI
  - Dependency scanning: Dependabot for automated vulnerability alerts
  - DAST: OWASP ZAP scan post-MVP

---

## Security

### Input Validation

- **Validation Library:** Pydantic 2.6.0 (backend), Zod 3.22.4 (frontend)
- **Validation Location:** 
  - Backend: At API boundary in Pydantic request schemas before business logic
  - Frontend: At form submission using Zod schemas and React Hook Form
- **Required Rules:**
  - All external inputs MUST be validated against explicit schemas
  - Validation at API boundary before processing (defense in depth)
  - Whitelist approach preferred over blacklist (enumerate allowed values)
  - Username format: Regex `^\\[^\\]+\\[^\\]+$` to enforce domain format
  - Password: Minimum 8 characters (backend enforces, frontend provides guidance)

### Authentication & Authorization

- **Auth Method:** JWT tokens in httpOnly cookies with HS256 signing
- **Session Management:** Stateless JWT tokens, no server-side session store
- **Required Patterns:**
  - All protected endpoints require `@require_auth` decorator (FastAPI dependency)
  - JWT payload includes: `user_id`, `username`, `exp` (expiration: 24 hours)
  - Refresh token not implemented in MVP (users re-login after 24 hours)
  - Password reset flow deferred to post-MVP (contact admin for now)

**Authorization Rules:**
- Students can only access their own sessions (check `user_id` in session record)
- Admin endpoints (future) require `is_admin` flag in JWT payload
- Blocked users cannot log in (check `is_blocked` before issuing JWT)

### Secrets Management

- **Development:** `.env` files (never committed to Git, use `.env.example` as template)
- **Production:** Railway environment variables (encrypted at rest)
- **Code Requirements:**
  - NEVER hardcode secrets (API keys, database URLs, JWT secret)
  - Access via configuration service only (`config.py` using Pydantic Settings)
  - No secrets in logs or error messages (sanitize error output)
  - Rotate secrets every 90 days (manual process for MVP, automate post-MVP)

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# JWT
JWT_SECRET_KEY=<random-256-bit-key>
JWT_ALGORITHM=HS256

# External Services
DAILY_API_KEY=<daily-co-api-key>
LIVEKIT_API_KEY=<livekit-api-key>
LIVEKIT_API_SECRET=<livekit-api-secret>
BEYOND_PRESENCE_API_KEY=<beyond-presence-key>
DEEPGRAM_API_KEY=<deepgram-key>
CARTESIA_API_KEY=<cartesia-key>
GOOGLE_API_KEY=<gemini-key>
OPENAI_API_KEY=<openai-key>

# Sentry
SENTRY_DSN=<sentry-project-dsn>
```

### API Security

- **Rate Limiting:** 
  - Library: `slowapi` (FastAPI rate limiting)
  - Limits: 100 requests per minute per IP for public endpoints
  - Limits: 1000 requests per minute per user for authenticated endpoints
  - Stricter limits on session creation: 10 voice/video sessions per hour per user
  
- **CORS Policy:**
  - Allow origins: Production frontend domain + localhost for development
  - Allow methods: GET, POST, DELETE (no PUT/PATCH in MVP)
  - Allow credentials: True (for httpOnly cookies)
  - Max age: 3600 seconds
  
- **Security Headers:**
  ```python
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
  ```
  
- **HTTPS Enforcement:** 
  - Railway automatic HTTPS for production
  - Redirect HTTP → HTTPS (middleware in FastAPI)
  - HSTS header enforces HTTPS for 1 year

### Data Protection

- **Encryption at Rest:** 
  - PostgreSQL pgcrypto extension for sensitive fields (transcripts)
  - Database backups encrypted by Railway
  - API keys encrypted by Railway environment variable storage
  
- **Encryption in Transit:** 
  - TLS 1.3 for all HTTP communication
  - WebRTC uses DTLS-SRTP for media encryption (handled by Daily.co/LiveKit)
  
- **PII Handling:**
  - Transcripts considered PII under FERPA - encrypted and auto-purged after 90 days
  - Usernames are institutional IDs - not considered PII
  - No collection of email, phone, address in MVP
  
- **Logging Restrictions:**
  - NEVER log passwords, tokens, or session transcripts
  - Log user_id only (not username) in most log entries
  - Sanitize error messages to remove sensitive data before logging

### Dependency Security

- **Scanning Tool:** 
  - Dependabot (GitHub) for automated dependency alerts
  - `pip-audit` for Python dependencies in CI
  - `npm audit` for JavaScript dependencies in CI
  
- **Update Policy:** 
  - Security patches applied within 1 week of disclosure
  - Minor version updates reviewed monthly
  - Major version updates planned and tested before deployment
  
- **Approval Process:**
  - New dependencies require PR review and security check
  - Check npm/PyPI package reputation and download counts
  - Avoid dependencies with known CVEs or unmaintained packages

### Security Testing

- **SAST Tool:** 
  - Bandit for Python static analysis (in CI)
  - ESLint security plugin for TypeScript
  
- **DAST Tool:** 
  - OWASP ZAP manual scan post-MVP (not automated in CI for MVP)
  
- **Penetration Testing:** 
  - Internal security review before launch
  - Third-party pentest deferred to post-MVP after first 1000 users

---

## Next Steps

This architecture document serves as the foundation for implementation. Here are the recommended next steps:

### For Frontend Architecture

Since this project has a significant user interface, you should create a **Frontend Architecture Document** using the Frontend Architect mode. That document will detail:

- Frontend-specific component architecture (beyond what's in the source tree)
- State management strategy in detail
- WebRTC client implementation patterns
- UI/UX design system implementation
- Frontend-specific error handling and loading states
- Performance optimization strategies (code splitting, lazy loading)
- Accessibility implementation details

**Prompt for Frontend Architect:**

```
Create a frontend architecture document for the College Student Counseling Platform. 
Reference the backend architecture at docs/architecture.md and PRD at docs/prd.md.
Focus on:
- Next.js 14 App Router structure and routing strategy
- WebRTC client integration for voice (Daily.co) and video (LiveKit)
- Real-time transcript display and synchronization
- shadcn/ui component customization and design system
- Authentication flow and protected route implementation
- State management across voice/video sessions
- Error handling and graceful degradation for connection issues
- Performance optimization for real-time media streams
```

---

## Real-Time Transcript Transport

### WebSocket Architecture Decision

**Selected Approach:** WebSocket connection for bidirectional real-time transcript streaming

**Rationale:**
- PRD FR8/FR9 require real-time transcription display during voice/video sessions
- WebSocket provides low-latency, bidirectional communication ideal for streaming updates
- Enables server-push for crisis alerts without client polling
- Single persistent connection reduces overhead vs. repeated HTTP requests

**Implementation:** FastAPI WebSocket endpoint `/ws/sessions/{session_id}/transcript`

### Transcript Delivery Flow

1. **Session Creation:** Backend returns `websocket_url` in session creation response
2. **WebSocket Connection:** Frontend connects with JWT token as query parameter
3. **Transcript Streaming:** 
   - PipeCat/Deepgram sends interim transcripts to backend
   - Backend broadcasts via WebSocket to connected client
   - Frontend displays in real-time transcript panel
4. **Connection Quality Updates:** Periodic bandwidth/latency stats pushed to client
5. **Crisis Alerts:** Immediate push if crisis keywords detected
6. **Session End:** WebSocket closes, full transcript saved to database

**Fallback Strategy:** If WebSocket fails, transcripts stored in database and retrieved via REST API after session ends (degraded UX but functional).

---

## Transcript Storage Schema

### Database Model Extension

**Table:** `transcript_messages`

```sql
CREATE TABLE transcript_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- Message Content
    speaker VARCHAR(20) NOT NULL, -- 'student' or 'counselor'
    text TEXT NOT NULL,
    is_final BOOLEAN DEFAULT true, -- false for interim transcripts
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ordering
    sequence_number INTEGER NOT NULL,
    
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX idx_transcript_session ON transcript_messages(session_id, sequence_number);
CREATE INDEX idx_transcript_timestamp ON transcript_messages(session_id, timestamp);
```

**Updated Session Model:**
- Remove `transcript` TEXT column (replaced by separate table)
- Add `transcript_message_count` INTEGER for quick stats
- Add `crisis_detected` BOOLEAN for flagging sessions with crisis events

**Benefits:**
- Efficient querying of individual messages
- Better performance for long transcripts
- Easier to implement search/filter within transcripts
- Supports streaming delivery during session

---

## Environment Variables Specification

### Required Environment Variables

**Backend (.env):**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/counseling_platform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Authentication
JWT_SECRET_KEY=your-256-bit-secret-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# CORS (Frontend URL)
ALLOWED_ORIGINS=http://localhost:3000,https://counseling-platform.edu

# Daily.co (Voice Calling)
DAILY_API_KEY=your-daily-api-key
DAILY_DOMAIN=university.daily.co
DAILY_ROOM_EXPIRATION_MINUTES=120

# LiveKit (Video Calling)
LIVEKIT_URL=wss://livekit.counseling-platform.edu
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# Deepgram (Speech-to-Text)
DEEPGRAM_API_KEY=your-deepgram-api-key
DEEPGRAM_MODEL=nova-2

# Cartesia (Text-to-Speech)
CARTESIA_API_KEY=your-cartesia-api-key
CARTESIA_VOICE_ID=sonic-english

# Google Gemini (Primary LLM)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash

# OpenAI (Fallback LLM)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Beyond Presence (Avatar Video)
BEYOND_PRESENCE_API_KEY=your-beyond-presence-api-key
BEYOND_PRESENCE_BASE_URL=https://api.beyondpresence.ai

# PipeCat Configuration
PIPECAT_BOT_PATH=/usr/local/bin/pipecat-bot
PIPECAT_LOG_LEVEL=INFO

# Logging & Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
SESSION_RATE_LIMIT_PER_MINUTE=10

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SECONDS=60

# Data Retention
TRANSCRIPT_RETENTION_DAYS=90

# Application
ENV=development
DEBUG=true
PORT=8000
```

**Frontend (.env.local):**

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_VIDEO_SESSIONS=true
NEXT_PUBLIC_ENABLE_VOICE_SESSIONS=true

# Analytics (Optional for MVP)
NEXT_PUBLIC_ANALYTICS_ID=

# Environment
NEXT_PUBLIC_ENV=development
```

---

## Rate Limiting Configuration

### Strategy

**Library:** `slowapi` (FastAPI-compatible rate limiting)

**Rate Limit Tiers:**

| Endpoint Category | Limit | Window | Identifier |
|-------------------|-------|--------|------------|
| Authentication | 10 requests | per minute | IP address |
| Session Creation | 10 requests | per minute | User ID |
| Session History | 50 requests | per minute | User ID |
| Transcript Retrieval | 20 requests | per minute | User ID |
| WebSocket Connections | 5 concurrent | - | User ID |
| Health Check | Unlimited | - | - |

**Implementation:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to specific routes
@router.post("/sessions/voice/create")
@limiter.limit("10/minute")
async def create_voice_session(request: Request, ...):
    ...
```

**Error Response (429):** See API Specification document for format

---

## Database Indexing Strategy

### Performance-Critical Indexes

**Users Table:**
```sql
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_blocked ON users(is_blocked) WHERE is_blocked = true;
```

**Sessions Table:**
```sql
CREATE INDEX idx_sessions_user_started ON sessions(user_id, started_at DESC);
CREATE INDEX idx_sessions_category ON sessions(counselor_category);
CREATE INDEX idx_sessions_mode ON sessions(mode);
CREATE INDEX idx_sessions_active ON sessions(ended_at) WHERE ended_at IS NULL;
```

**Transcript Messages Table:**
```sql
CREATE INDEX idx_transcript_session_seq ON transcript_messages(session_id, sequence_number);
CREATE INDEX idx_transcript_timestamp ON transcript_messages(timestamp);
```

**Crisis Events Table:**
```sql
CREATE INDEX idx_crisis_session ON crisis_events(session_id);
CREATE INDEX idx_crisis_review ON crisis_events(flagged_for_review) WHERE flagged_for_review = true;
```

**Rationale:**
- `idx_sessions_user_started`: Optimizes session history queries (most common)
- `idx_sessions_active`: Quickly find active sessions for monitoring
- `idx_transcript_session_seq`: Efficient transcript retrieval in order
- `idx_crisis_review`: Admin dashboard for flagged crisis events

---

## Circuit Breaker Configuration

### External Service Protection

**Library:** `pybreaker`

**Configuration per Service:**

| Service | Failure Threshold | Timeout | Reset Timeout |
|---------|------------------|---------|---------------|
| Daily.co | 5 failures | 30s | 60s |
| LiveKit | 5 failures | 30s | 60s |
| Deepgram | 3 failures | 20s | 45s |
| Cartesia | 3 failures | 20s | 45s |
| Gemini | 3 failures | 20s | 45s |
| Beyond Presence | 5 failures | 30s | 60s |

**Implementation Example:**

```python
import pybreaker

daily_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    timeout_duration=30,
    reset_timeout=60,
    name="daily_co"
)

@daily_breaker
async def create_daily_room(...):
    # API call to Daily.co
    ...
```

**Fallback Behavior:**
- Voice/Video Creation: Return 503 with retry-after header
- Transcription: Continue session without live transcript (save for later)
- TTS: Use cached responses or simpler voice synthesis
- LLM: Switch from Gemini to OpenAI automatically

---

## Logging Standards

### Structured Logging Format

**Backend (Loguru):**

```python
import logging
from loguru import logger

# Configure JSON structured logging
logger.add(
    "logs/app.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="100 MB",
    retention="30 days",
    serialize=True  # JSON output
)

# Usage with context
logger.bind(
    request_id=request_id,
    user_id=user_id,
    session_id=session_id
).info("Session created", extra={
    "counselor_category": "health",
    "mode": "voice"
})
```

**Log Levels:**
- `DEBUG`: Development debugging, disabled in production
- `INFO`: Normal operations (session creation, API calls)
- `WARNING`: Recoverable errors, degraded service
- `ERROR`: Request failures, external service errors
- `CRITICAL`: System failures requiring immediate attention

**Required Context in Logs:**
- `request_id`: Unique identifier for request tracing
- `user_id`: Student identifier (for session-related logs)
- `session_id`: Session identifier (for session-specific logs)
- `service`: External service name (for integration logs)

---

## Browser Compatibility Matrix

### Minimum Supported Versions

| Browser | Minimum Version | WebRTC Support | Notes |
|---------|----------------|----------------|-------|
| Chrome | 100+ | Full | Recommended, best WebRTC support |
| Edge | 100+ | Full | Chromium-based, same as Chrome |
| Firefox | 100+ | Full | Good WebRTC support |
| Safari | 15.4+ | Full | Requires iOS 15.4+ for mobile |
| Safari iOS | 15.4+ | Full | Critical for mobile support |
| Chrome Android | 100+ | Full | Standard Android browser |

**Unsupported:**
- Internet Explorer (all versions)
- Safari < 15.4 (lacks modern WebRTC APIs)
- Firefox < 100 (missing required features)

**Detection Strategy:**
- Use `@vitejs/plugin-legacy` for basic polyfills
- Display compatibility warning for unsupported browsers
- Feature detection for WebRTC capabilities (getUserMedia, RTCPeerConnection)

---

## Test Data Strategy

### Development Seed Data

**Test Users:**

```sql
INSERT INTO users (id, username, password_hash, is_blocked, first_name, last_name) VALUES
('550e8400-e29b-41d4-a716-446655440000', '\domain\testuser1', '$2b$12$...', false, 'Alice', 'Student'),
('550e8400-e29b-41d4-a716-446655440001', '\domain\testuser2', '$2b$12$...', false, 'Bob', 'Student'),
('550e8400-e29b-41d4-a716-446655440002', '\domain\blockeduser', '$2b$12$...', true, 'Charlie', 'Blocked');

-- Password for all test users: "TestPassword123!"
```

**Test Sessions (Historical Data):**

```python
# Factory pattern for test data generation
def create_test_session(
    user_id: str,
    category: str,
    mode: str,
    duration_minutes: int,
    days_ago: int
):
    started_at = datetime.utcnow() - timedelta(days=days_ago)
    ended_at = started_at + timedelta(minutes=duration_minutes)
    
    return Session(
        user_id=user_id,
        counselor_category=category,
        mode=mode,
        started_at=started_at,
        ended_at=ended_at,
        duration_seconds=duration_minutes * 60,
        connection_quality="excellent"
    )
```

**Mock Transcript Data:**
- Use faker library to generate realistic conversation snippets
- Seed 10-20 past sessions per test user
- Include varied session lengths (5 mins to 45 mins)
- Mix of voice and video sessions
- Include one session with crisis_detected=true for testing

---

## Deployment Configuration

### Docker Configuration

**Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source and build
COPY . .
RUN pnpm build

# Production image
FROM node:20-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
RUN pnpm install --prod --frozen-lockfile

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["pnpm", "start"]
```

**docker-compose.yml (Development):**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: counseling
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: counseling_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./packages/backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://counseling:devpassword@postgres:5432/counseling_platform
    env_file:
      - ./packages/backend/.env
    depends_on:
      - postgres
    volumes:
      - ./packages/backend:/app

  frontend:
    build: ./packages/frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000/api/v1
    volumes:
      - ./packages/frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

---

## State Management Guidelines

### Decision Matrix

Use this matrix to determine the appropriate state management approach:

| State Type | Tool | When to Use | Example |
|------------|------|-------------|---------|
| **Authentication** | React Context | Infrequent updates, global access | User login status, user object |
| **Active Session** | Zustand | Frequent updates, complex logic | Real-time transcript, connection quality |
| **UI State** | Local useState | Component-specific, temporary | Modal open/closed, form inputs |
| **Form State** | React Hook Form | Form validation needed | Login form, filter forms |
| **Server State** | React Query (optional) | Data fetching, caching | Session history API calls |

**Context vs Zustand Decision Tree:**

```
Does state change frequently during sessions? 
├─ Yes → Is it shared across multiple components?
│  ├─ Yes → Use Zustand (e.g., live transcript, connection status)
│  └─ No → Use Local State
└─ No → Is it needed globally?
   ├─ Yes → Use Context (e.g., auth state)
   └─ No → Use Local State
```

---

## FERPA Compliance Checklist

### Required Implementations

- [ ] **Encryption at Rest:** AES-256 for database transcript columns (SQLAlchemy `encrypted` field type)
- [ ] **Encryption in Transit:** TLS 1.3 for all API communication (enforced at load balancer)
- [ ] **Access Control:** Students can only access their own session data (enforced in repositories)
- [ ] **Data Retention:** Automatic transcript purge after 90 days (scheduled job)
- [ ] **Audit Logging:** All transcript access logged with timestamp, user_id
- [ ] **Consent:** Terms of Service disclosure before first session
- [ ] **Parent/Guardian Access:** Not applicable (college students are 18+)
- [ ] **Health/Safety Exception:** Crisis detection triggers permitted disclosure (documented in crisis-protocol.md)

### Audit Trail Implementation

**Table:** `audit_log`

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- 'view_transcript', 'delete_transcript', 'download_transcript'
    resource_type VARCHAR(50) NOT NULL, -- 'session', 'transcript'
    resource_id UUID NOT NULL,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id, timestamp DESC);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
```

---

## Performance Monitoring SLAs

### Target Metrics (PRD Requirements)

| Metric | Target | Measurement | Alert Threshold |
|--------|--------|-------------|-----------------|
| **Uptime** | 99.5% | Uptime Robot | < 99.0% monthly |
| **Connection Time** | <30s | API duration logs | >45s p95 |
| **API Response Time** | <500ms | Sentry | >1000ms p95 |
| **Page Load Time** | <3s | Lighthouse | >5s median |
| **WebSocket Latency** | <500ms | Custom metrics | >1000ms p95 |
| **Voice Quality** | 4.0/5.0 | User surveys | <3.5 average |
| **Concurrent Sessions** | 50+ | Load testing | Failures <50 |

### Monitoring Stack

- **Uptime Monitoring:** UptimeRobot (free tier) for basic health checks
- **Error Tracking:** Sentry for exception capture and performance monitoring
- **Custom Metrics:** Export to Prometheus/Grafana if scale requires (post-MVP)
- **User Feedback:** In-session rating modal after each counseling session

---

### For Development Team

1. **Repository Setup:**
   - Initialize Git repository with monorepo structure
   - Set up pnpm workspaces and Turborepo
   - Configure ESLint, Prettier, Ruff, mypy
   - Create `.env.example` files with required variables (see Environment Variables section)

2. **Database Setup:**
   - Run initial Alembic migration to create schema
   - Seed counselor categories with provided SQL
   - Create test users for development

3. **Begin Epic 1 Implementation:**
   - Start with Story 1.1: Project Initialization
   - Set up CI/CD pipelines in GitHub Actions
   - Configure Railway projects for deployment
   - Implement authentication system (Epic 1 Stories 1.3-1.7)

### For QA Team

1. Review test strategy section and prepare test infrastructure
2. Set up Testcontainers for integration testing
3. Create test data factories and fixtures
4. Prepare manual test cases for WebRTC functionality (voice/video)

### For DevOps/Platform Team

1. Set up Railway projects (production + staging future)
2. Configure environment variables in Railway
3. Set up GitHub repository and Actions
4. Configure Sentry for error tracking
5. Set up monitoring and alerting

### For Product Team

1. Review architecture against PRD requirements
2. Validate counselor category prompts with subject matter experts
3. Plan user acceptance testing approach
4. Prepare go-live checklist

---

**Document Status:** ✅ **Complete**  
**Ready for Review:** Yes  
**Next Action:** Share with team and create Frontend Architecture Document

