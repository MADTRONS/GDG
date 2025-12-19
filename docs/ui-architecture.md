# College Student Counseling Platform - Frontend Architecture Document

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Complete  
**References:** [Backend Architecture](architecture.md), [PRD](prd.md), [Wireframes](wireframes.md)

---

## Template and Framework Selection

### Framework Analysis

Based on the backend architecture document and PRD requirements, the frontend uses:

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5.3.3
- **UI Library:** React 18.3.0
- **Component Library:** shadcn/ui (Radix UI primitives)
- **Styling:** Tailwind CSS 3.4.1

**No Starter Template:** This is a greenfield project without a pre-existing starter template. The Next.js 14 App Router provides the foundational structure, and we'll implement custom patterns optimized for real-time WebRTC counseling sessions.

**Key Constraints from Backend:**
- Must integrate with Daily.co SDK for voice calling
- Must integrate with LiveKit client for video calling  
- Must maintain type safety with shared TypeScript types from `packages/shared`
- Must implement JWT authentication via httpOnly cookies
- Must support real-time transcript display during sessions

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-19 | 1.0 | Initial frontend architecture document | Winston (Architect) |

---

## Frontend Tech Stack

**CRITICAL:** This tech stack is synchronized with the main architecture document. All changes must be reflected in both documents.

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Framework** | Next.js | 14.2.0 | React-based web framework | App Router for modern routing, server components, built-in optimization, SEO support |
| **UI Library** | React | 18.3.0 | Component-based UI library | Concurrent features, hooks ecosystem, industry standard |
| **Language** | TypeScript | 5.3.3 | Type-safe JavaScript | Strict mode, shared types with backend, prevents runtime errors |
| **Build Tool** | Next.js (Turbopack) | Built-in | Fast refresh and bundling | Integrated with Next.js, faster than Webpack |
| **Component Library** | shadcn/ui | Latest | Accessible component primitives | Radix UI based, highly customizable, copy-paste components |
| **Styling** | Tailwind CSS | 3.4.1 | Utility-first CSS framework | Rapid development, consistent design system, JIT compilation |
| **State Management** | React Context + Zustand | 18.3.0 + 4.5.0 | Global state management | Context for auth, Zustand for complex state if needed |
| **Form Handling** | React Hook Form | 7.51.0 | Form validation and state | Minimal re-renders, excellent DX, Zod integration |
| **Schema Validation** | Zod | 3.22.4 | Runtime type validation | Shared schemas with backend, type-safe validation |
| **Routing** | Next.js App Router | Built-in | File-system based routing | Automatic code splitting, layouts, nested routes |
| **API Client** | Fetch API + Custom Wrapper | Native | HTTP requests | Native browser API, wrapped for auth and error handling |
| **WebRTC (Voice)** | @daily-co/daily-js | Latest | Voice calling infrastructure | Official Daily.co SDK, handles media streams |
| **WebRTC (Video)** | livekit-client | 0.11.0 | Video calling infrastructure | Official LiveKit SDK, avatar streaming support |
| **Testing** | Vitest | 1.2.0 | Unit testing framework | Fast, Vite-native, modern alternative to Jest |
| **Testing Library** | @testing-library/react | 14.0.0 | Component testing | User-centric testing, accessibility focused |
| **E2E Testing** | Playwright | 1.41.0 | Browser automation | Cross-browser, reliable, network mocking |
| **Linting** | ESLint | 8.56.0 | Code quality | Next.js config, TypeScript rules |
| **Formatting** | Prettier | 3.2.4 | Code formatting | Consistent style across team |
| **Animation** | Framer Motion | 10.16.0 | UI animations | Declarative animations, spring physics, variants |
| **Icons** | Lucide React | 0.294.0 | Icon library | Consistent icons, tree-shakeable, 1000+ icons |
| **Date Handling** | date-fns | 3.0.0 | Date utilities | Lightweight, functional, i18n support |
| **Dev Tools** | React DevTools | Latest | React debugging | Component tree inspection, hooks debugging |

**Key Frontend-Specific Decisions:**

- **Next.js App Router over Pages Router:** Enables server components, streaming, better data fetching patterns
- **shadcn/ui over Material-UI/Chakra:** Copy-paste approach gives full control, no runtime JS overhead
- **Zustand over Redux:** Simpler API, less boilerplate, sufficient for MVP scope
- **Vitest over Jest:** Faster test execution, native ESM support, better DX
- **Framer Motion:** Smooth animations for session transitions and UI feedback

---

## Project Structure

```plaintext
packages/frontend/
├── app/                              # Next.js 14 App Router
│   ├── layout.tsx                   # Root layout with providers
│   ├── page.tsx                     # Login page (/)
│   ├── globals.css                  # Tailwind imports + global styles
│   ├── providers.tsx                # Client-side providers wrapper
│   │
│   ├── dashboard/                   # Main dashboard route
│   │   ├── page.tsx                # Dashboard page component
│   │   └── loading.tsx             # Loading UI for dashboard
│   │
│   ├── voice-session/              # Voice calling route
│   │   ├── page.tsx                # Voice session page
│   │   ├── loading.tsx             # Loading UI
│   │   └── error.tsx               # Error boundary
│   │
│   ├── video-session/              # Video calling route
│   │   ├── page.tsx                # Video session page
│   │   ├── loading.tsx             # Loading UI
│   │   └── error.tsx               # Error boundary
│   │
│   ├── sessions/                    # Session history routes
│   │   ├── page.tsx                # Session list page
│   │   ├── [id]/                   # Dynamic session detail route
│   │   │   └── page.tsx            # Session detail with transcript
│   │   └── loading.tsx
│   │
│   └── api/                         # API route handlers (if needed)
│       └── health/
│           └── route.ts            # Health check endpoint
│
├── components/                       # React components
│   ├── ui/                          # shadcn/ui components (generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── toast.tsx
│   │   ├── select.tsx
│   │   ├── slider.tsx
│   │   └── ...                     # Other shadcn components
│   │
│   ├── auth/                        # Authentication components
│   │   ├── LoginForm.tsx           # Login form with validation
│   │   ├── AuthProvider.tsx        # Auth context provider
│   │   └── ProtectedRoute.tsx      # Route protection wrapper
│   │
│   ├── dashboard/                   # Dashboard components
│   │   ├── CounselorCard.tsx      # Counselor category card
│   │   ├── StatsWidget.tsx         # Session statistics
│   │   └── Header.tsx              # Dashboard header with user menu
│   │
│   ├── voice/                       # Voice session components
│   │   ├── VoiceClient.tsx         # Daily.co client wrapper
│   │   ├── AudioWaveform.tsx       # Audio visualization
│   │   ├── TranscriptPanel.tsx     # Live transcript display
│   │   ├── VoiceControls.tsx       # Mute, volume, end call
│   │   └── ConnectionStatus.tsx    # Connection quality indicator
│   │
│   ├── video/                       # Video session components
│   │   ├── VideoClient.tsx         # LiveKit client wrapper
│   │   ├── AvatarPlayer.tsx        # Video player for avatar
│   │   ├── VideoControls.tsx       # Video-specific controls
│   │   ├── TranscriptSidebar.tsx   # Transcript in sidebar
│   │   └── QualityIndicator.tsx    # Video quality badge
│   │
│   ├── sessions/                    # Session history components
│   │   ├── SessionCard.tsx         # Individual session card
│   │   ├── SessionFilters.tsx      # Filter controls
│   │   ├── TranscriptView.tsx      # Full transcript display
│   │   ├── Pagination.tsx          # Pagination controls
│   │   └── EmptyState.tsx          # No sessions message
│   │
│   └── shared/                      # Shared/common components
│       ├── ErrorBoundary.tsx       # Error boundary wrapper
│       ├── LoadingSpinner.tsx      # Loading indicator
│       ├── EmergencyBanner.tsx     # Crisis detection banner
│       └── Footer.tsx              # App footer
│
├── lib/                             # Utility functions and configurations
│   ├── api-client.ts               # API client with auth
│   ├── daily-client.ts             # Daily.co SDK wrapper
│   ├── livekit-client.ts           # LiveKit SDK wrapper
│   ├── logger.ts                   # Frontend logging utility
│   ├── utils.ts                    # General utilities (cn, formatters)
│   └── validators.ts               # Zod schemas for forms
│
├── hooks/                           # Custom React hooks
│   ├── useAuth.ts                  # Authentication hook
│   ├── useVoiceSession.ts          # Voice session management
│   ├── useVideoSession.ts          # Video session management
│   ├── useTranscript.ts            # Transcript state management
│   ├── useSessionHistory.ts        # Session list fetching
│   └── useMediaDevices.ts          # Microphone/camera access
│
├── stores/                          # Zustand stores (if needed)
│   └── sessionStore.ts             # Complex session state
│
├── types/                           # TypeScript type definitions
│   ├── index.ts                    # Re-export from shared package
│   ├── daily.d.ts                  # Daily.co type augmentations
│   ├── livekit.d.ts                # LiveKit type augmentations
│   └── components.d.ts             # Component-specific types
│
├── styles/                          # Global styles
│   └── globals.css                 # Tailwind + custom CSS
│
├── public/                          # Static assets
│   ├── icons/                      # Counselor category icons
│   │   ├── health.svg
│   │   ├── career.svg
│   │   ├── academic.svg
│   │   ├── financial.svg
│   │   ├── social.svg
│   │   └── personal-development.svg
│   ├── logo.svg                    # Platform logo
│   └── favicon.ico
│
├── __tests__/                       # Test files
│   ├── components/
│   │   ├── LoginForm.test.tsx
│   │   ├── CounselorCard.test.tsx
│   │   └── ...
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   └── ...
│   └── utils/
│       └── api-client.test.ts
│
├── .env.example                     # Environment variables template
├── .eslintrc.json                   # ESLint configuration
├── .prettierrc                      # Prettier configuration
├── next.config.js                   # Next.js configuration
├── tailwind.config.ts               # Tailwind configuration
├── tsconfig.json                    # TypeScript configuration
├── vitest.config.ts                 # Vitest configuration
├── playwright.config.ts             # Playwright configuration
└── package.json                     # Dependencies and scripts
```

**Structure Rationale:**

1. **App Directory:** Next.js 14 App Router structure with co-located loading/error states
2. **Component Organization:** Grouped by feature (auth, dashboard, voice, video, sessions)
3. **shadcn/ui in components/ui:** Standard location for shadcn components
4. **Hooks Directory:** Centralized custom hooks for reusability
5. **Lib for Utilities:** Pure functions, wrappers, and configurations
6. **Types from Shared Package:** Import from `@repo/shared` for backend type alignment
7. **Public Directory:** Static assets with organized subdirectories
8. **Tests Co-located:** Can also place `*.test.tsx` next to components if preferred

---

## Component Standards

### Component Template

```typescript
'use client'; // Only if component uses client-side features (hooks, events)

import { type FC } from 'react';
import { cn } from '@/lib/utils';

// Props interface - always define explicitly
interface ComponentNameProps {
  /** Prop description */
  propName: string;
  /** Optional prop with default */
  optionalProp?: boolean;
  /** Event handler */
  onAction?: () => void;
  /** Children if needed */
  children?: React.ReactNode;
  /** For styling */
  className?: string;
}

/**
 * ComponentName - Brief description of component purpose
 * 
 * @example
 * ```tsx
 * <ComponentName propName="value" onAction={() => {}} />
 * ```
 */
export const ComponentName: FC<ComponentNameProps> = ({
  propName,
  optionalProp = false,
  onAction,
  children,
  className,
}) => {
  // Hooks at top
  // const [state, setState] = useState();
  
  // Event handlers
  const handleClick = () => {
    onAction?.();
  };
  
  // Early returns for conditional rendering
  if (!propName) {
    return null;
  }
  
  return (
    <div className={cn('base-classes', className)}>
      {/* Component JSX */}
      <button onClick={handleClick}>
        {children}
      </button>
    </div>
  );
};

// Default export if page component, named export otherwise
export default ComponentName; // Only for page.tsx files
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| **Components** | PascalCase | `LoginForm`, `CounselorCard` |
| **Component Files** | PascalCase.tsx | `LoginForm.tsx`, `CounselorCard.tsx` |
| **Hooks** | camelCase with `use` prefix | `useAuth`, `useVoiceSession` |
| **Hook Files** | camelCase.ts | `useAuth.ts`, `useVoiceSession.ts` |
| **Utilities** | camelCase | `formatDate`, `parseUsername` |
| **Utility Files** | kebab-case.ts | `api-client.ts`, `daily-client.ts` |
| **Types/Interfaces** | PascalCase | `User`, `SessionResponse`, `AuthContext` |
| **Constants** | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES` |
| **CSS Classes** | Tailwind utilities | `bg-blue-500`, `text-lg` |
| **Custom CSS** | kebab-case | `.audio-waveform`, `.transcript-message` |
| **Routes** | kebab-case | `/voice-session`, `/sessions/[id]` |
| **API Endpoints** | kebab-case | `/api/voice/create-room` |

**Component File Organization:**
- One component per file (exceptions: small related components)
- Export component with same name as file
- Place types/interfaces above component definition
- Group imports: React → Third-party → Local → Types

---

## State Management

### Store Structure

```plaintext
stores/
├── sessionStore.ts                  # Active session state (if using Zustand)
└── index.ts                         # Store exports
```

**Primary Strategy:** React Context for authentication state, local component state for UI, Zustand only if complexity demands.

### Authentication Context (Primary State)

```typescript
// components/auth/AuthProvider.tsx
'use client';

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '@repo/shared';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  async function checkAuthStatus() {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include', // Send httpOnly cookie
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function login(username: string, password: string) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setUser(data.user);
  }

  async function logout() {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    });
    setUser(null);
  }

  async function refreshUser() {
    await checkAuthStatus();
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Zustand Store Template (Optional, for Complex State)

```typescript
// stores/sessionStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface SessionState {
  // State
  activeSessionId: string | null;
  transcript: Array<{ speaker: 'user' | 'counselor'; text: string; timestamp: Date }>;
  isRecording: boolean;
  connectionQuality: 'excellent' | 'good' | 'fair' | 'poor' | null;
  
  // Actions
  setActiveSession: (sessionId: string) => void;
  clearActiveSession: () => void;
  addTranscriptMessage: (speaker: 'user' | 'counselor', text: string) => void;
  clearTranscript: () => void;
  setRecording: (isRecording: boolean) => void;
  setConnectionQuality: (quality: SessionState['connectionQuality']) => void;
}

export const useSessionStore = create<SessionState>()(
  devtools(
    (set) => ({
      // Initial state
      activeSessionId: null,
      transcript: [],
      isRecording: false,
      connectionQuality: null,
      
      // Actions
      setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),
      
      clearActiveSession: () => set({
        activeSessionId: null,
        transcript: [],
        isRecording: false,
        connectionQuality: null,
      }),
      
      addTranscriptMessage: (speaker, text) => set((state) => ({
        transcript: [...state.transcript, { speaker, text, timestamp: new Date() }],
      })),
      
      clearTranscript: () => set({ transcript: [] }),
      
      setRecording: (isRecording) => set({ isRecording }),
      
      setConnectionQuality: (quality) => set({ connectionQuality: quality }),
    }),
    { name: 'SessionStore' }
  )
);
```

**State Management Guidelines:**
- Use React Context for authentication (read-heavy, infrequent updates)
- Use local useState for UI state (modals, form inputs, loading states)
- Use Zustand for complex shared state (active sessions, real-time transcripts)
- Avoid Redux - overkill for MVP scope
- Keep state as local as possible - lift only when needed

---

## API Integration

### API Client Configuration

```typescript
// lib/api-client.ts
import type { User, Session, CounselorCategory } from '@repo/shared';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean;
}

async function fetchWithAuth(
  endpoint: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { requiresAuth = true, ...fetchOptions } = options;

  const config: RequestInit = {
    ...fetchOptions,
    credentials: 'include', // Always send cookies (JWT)
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // Handle errors
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An error occurred',
      code: 'UNKNOWN_ERROR',
    }));

    if (response.status === 401 && requiresAuth) {
      // Redirect to login on auth failure
      window.location.href = '/';
      throw new ApiError('Unauthorized', 401, 'AUTH_REQUIRED');
    }

    throw new ApiError(
      error.detail || 'Request failed',
      response.status,
      error.code
    );
  }

  return response;
}

// Auth API
export const authApi = {
  async login(username: string, password: string): Promise<{ user: User; access_token: string }> {
    const response = await fetchWithAuth('/api/auth/login', {
      method: 'POST',
      requiresAuth: false,
      body: JSON.stringify({ username, password }),
    });
    return response.json();
  },

  async logout(): Promise<void> {
    await fetchWithAuth('/api/auth/logout', {
      method: 'POST',
    });
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetchWithAuth('/api/auth/me');
    return response.json();
  },
};

// Counselor API
export const counselorApi = {
  async getCategories(): Promise<CounselorCategory[]> {
    const response = await fetchWithAuth('/api/counselors/categories');
    return response.json();
  },
};

// Voice Session API
export const voiceApi = {
  async createRoom(counselorCategory: string): Promise<{
    room_url: string;
    user_token: string;
    session_id: string;
  }> {
    const response = await fetchWithAuth('/api/voice/create-room', {
      method: 'POST',
      body: JSON.stringify({ counselor_category: counselorCategory }),
    });
    return response.json();
  },

  async endSession(sessionId: string, transcript: string): Promise<void> {
    await fetchWithAuth('/api/voice/end-session', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, transcript }),
    });
  },
};

// Video Session API
export const videoApi = {
  async createRoom(counselorCategory: string): Promise<{
    room_url: string;
    user_token: string;
    session_id: string;
    avatar_id: string;
  }> {
    const response = await fetchWithAuth('/api/video/create-room', {
      method: 'POST',
      body: JSON.stringify({ counselor_category: counselorCategory }),
    });
    return response.json();
  },

  async endSession(sessionId: string, avatarId: string, transcript: string): Promise<void> {
    await fetchWithAuth('/api/video/end-session', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, avatar_id: avatarId, transcript }),
    });
  },
};

// Session History API
export const sessionApi = {
  async getSessions(params?: {
    category?: string;
    mode?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    per_page?: number;
  }): Promise<{
    sessions: Session[];
    total: number;
    page: number;
    per_page: number;
  }> {
    const queryParams = new URLSearchParams(params as Record<string, string>);
    const response = await fetchWithAuth(`/api/sessions?${queryParams}`);
    return response.json();
  },

  async getSession(sessionId: string): Promise<Session> {
    const response = await fetchWithAuth(`/api/sessions/${sessionId}`);
    return response.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    await fetchWithAuth(`/api/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },

  async downloadTranscript(sessionId: string): Promise<Blob> {
    const response = await fetchWithAuth(`/api/sessions/${sessionId}/download`);
    return response.blob();
  },
};
```

### Service Template Example

```typescript
// lib/daily-client.ts
import Daily, { DailyCall, DailyEvent, DailyParticipant } from '@daily-co/daily-js';

export interface DailyClientConfig {
  roomUrl: string;
  token: string;
  onJoined?: () => void;
  onLeft?: () => void;
  onParticipantJoined?: (participant: DailyParticipant) => void;
  onParticipantLeft?: (participant: DailyParticipant) => void;
  onTranscript?: (message: { speaker: string; text: string }) => void;
  onError?: (error: Error) => void;
}

export class DailyClient {
  private call: DailyCall | null = null;
  private config: DailyClientConfig;

  constructor(config: DailyClientConfig) {
    this.config = config;
  }

  async join(): Promise<void> {
    try {
      // Create Daily call object
      this.call = Daily.createCallObject();

      // Set up event listeners
      this.setupEventListeners();

      // Join the room
      await this.call.join({
        url: this.config.roomUrl,
        token: this.config.token,
      });

      this.config.onJoined?.();
    } catch (error) {
      this.config.onError?.(error as Error);
      throw error;
    }
  }

  async leave(): Promise<void> {
    if (this.call) {
      await this.call.leave();
      this.call.destroy();
      this.call = null;
      this.config.onLeft?.();
    }
  }

  setMuted(muted: boolean): void {
    this.call?.setLocalAudio(!muted);
  }

  isMuted(): boolean {
    return !this.call?.localAudio();
  }

  private setupEventListeners(): void {
    if (!this.call) return;

    this.call.on('participant-joined', (event) => {
      this.config.onParticipantJoined?.(event.participant);
    });

    this.call.on('participant-left', (event) => {
      this.config.onParticipantLeft?.(event.participant);
    });

    this.call.on('error', (error) => {
      this.config.onError?.(new Error(error.errorMsg));
    });

    // If Daily provides transcript events
    this.call.on('app-message' as DailyEvent, (event: any) => {
      if (event.data?.type === 'transcript') {
        this.config.onTranscript?.(event.data);
      }
    });
  }

  getConnectionStats() {
    return this.call?.getNetworkStats();
  }

  destroy(): void {
    this.call?.destroy();
    this.call = null;
  }
}
```

---

## Routing

### Route Configuration

```typescript
// app/providers.tsx
'use client';

import { AuthProvider } from '@/components/auth/AuthProvider';
import { Toaster } from '@/components/ui/toaster';
import type { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <Toaster />
    </AuthProvider>
  );
}
```

```typescript
// components/auth/ProtectedRoute.tsx
'use client';

import { useAuth } from './AuthProvider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
```

```typescript
// app/dashboard/page.tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardContent } from '@/components/dashboard/DashboardContent';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
```

**Route Structure:**
- `/` - Login page (public)
- `/dashboard` - Main dashboard (protected)
- `/voice-session` - Voice calling page (protected)
- `/video-session` - Video calling page (protected)
- `/sessions` - Session history list (protected)
- `/sessions/[id]` - Session detail with transcript (protected)

**Navigation Pattern:**
```typescript
// Using Next.js navigation
import { useRouter } from 'next/navigation';

const router = useRouter();

// Navigate to dashboard
router.push('/dashboard');

// Navigate with query params
router.push('/sessions?category=Health&mode=voice');

// Go back
router.back();
```

---

## Styling Guidelines

### Styling Approach

**Primary:** Tailwind CSS utility classes for all styling  
**Secondary:** CSS custom properties for theme variables  
**Minimal:** Custom CSS only for complex animations or WebRTC canvas elements

**Component Styling Pattern:**

```tsx
import { cn } from '@/lib/utils';

export function CounselorCard({ category, isActive, className }) {
  return (
    <div
      className={cn(
        // Base styles
        'rounded-lg border bg-card p-6 shadow-sm transition-all',
        // Interactive styles
        'hover:shadow-md hover:border-primary hover:-translate-y-1',
        // Conditional styles
        isActive && 'border-primary bg-primary/5',
        // Consumer overrides
        className
      )}
    >
      {/* Content */}
    </div>
  );
}
```

### Global Theme Variables

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Colors - Soft Blue Primary */
    --color-primary: 74 144 226; /* #4A90E2 */
    --color-primary-hover: 64 131 206; /* Darker blue */
    --color-secondary: 111 207 151; /* #6FCF97 - Calming green */
    
    /* Neutral Grays */
    --color-gray-50: 249 250 251;
    --color-gray-100: 245 245 245;
    --color-gray-200: 229 231 235;
    --color-gray-300: 209 213 219;
    --color-gray-400: 156 163 175;
    --color-gray-500: 107 114 128;
    --color-gray-600: 75 85 99;
    --color-gray-700: 55 65 81;
    --color-gray-800: 31 41 55;
    --color-gray-900: 17 24 39;
    
    /* Semantic Colors */
    --color-error: 231 76 60; /* #E74C3C */
    --color-success: 39 174 96; /* #27AE60 */
    --color-warning: 243 156 18; /* #F39C12 */
    
    /* Background & Foreground */
    --background: 0 0 100%; /* White */
    --foreground: var(--color-gray-900);
    
    /* Card */
    --card: 0 0 100%;
    --card-foreground: var(--color-gray-900);
    
    /* Border */
    --border: var(--color-gray-200);
    --input: var(--color-gray-300);
    
    /* Ring (focus) */
    --ring: var(--color-primary);
    
    /* Radius */
    --radius-sm: 0.25rem;  /* 4px */
    --radius-md: 0.5rem;   /* 8px */
    --radius-lg: 0.75rem;  /* 12px */
    --radius-full: 9999px;
    
    /* Spacing Scale */
    --spacing-xs: 0.25rem;  /* 4px */
    --spacing-sm: 0.5rem;   /* 8px */
    --spacing-md: 1rem;     /* 16px */
    --spacing-lg: 1.5rem;   /* 24px */
    --spacing-xl: 2rem;     /* 32px */
    --spacing-2xl: 3rem;    /* 48px */
    --spacing-3xl: 4rem;    /* 64px */
    
    /* Typography */
    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
    
    /* Shadows */
    --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  /* Dark mode support (future) */
  .dark {
    --background: var(--color-gray-900);
    --foreground: var(--color-gray-50);
    --card: var(--color-gray-800);
    --card-foreground: var(--color-gray-50);
    --border: var(--color-gray-700);
    --input: var(--color-gray-600);
  }
  
  * {
    @apply border-border;
  }
  
  body {
    @apply bg-background text-foreground font-sans;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

@layer utilities {
  /* Custom scrollbar for transcript panels */
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: rgb(var(--color-primary) / 0.3) transparent;
  }
  
  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: rgb(var(--color-primary) / 0.3);
    border-radius: 9999px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background-color: rgb(var(--color-primary) / 0.5);
  }
}

/* Custom animations */
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Audio waveform visualization */
.audio-waveform {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 200px;
}

.audio-waveform-bar {
  width: 6px;
  background: linear-gradient(
    to top,
    rgb(var(--color-primary)),
    rgb(var(--color-secondary))
  );
  border-radius: 9999px;
  transition: height var(--transition-fast);
}
```

### Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        primary: {
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          hover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
        },
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        error: 'rgb(var(--color-error) / <alpha-value>)',
        success: 'rgb(var(--color-success) / <alpha-value>)',
        warning: 'rgb(var(--color-warning) / <alpha-value>)',
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        full: 'var(--radius-full)',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        DEFAULT: 'var(--shadow-md)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
      transitionDuration: {
        fast: 'var(--transition-fast)',
        DEFAULT: 'var(--transition-base)',
        slow: 'var(--transition-slow)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
} satisfies Config;

export default config;
```

---

## Testing Requirements

### Component Test Template

```typescript
// __tests__/components/LoginForm.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '@/components/auth/LoginForm';
import { AuthProvider } from '@/components/auth/AuthProvider';

// Mock API client
vi.mock('@/lib/api-client', () => ({
  authApi: {
    login: vi.fn(),
  },
}));

import { authApi } from '@/lib/api-client';

describe('LoginForm', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form with username and password fields', () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('validates username format before submission', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    // Enter invalid username format
    await user.type(usernameInput, 'invalid-username');
    await user.click(submitButton);

    expect(await screen.findByText(/invalid username format/i)).toBeInTheDocument();
    expect(authApi.login).not.toHaveBeenCalled();
  });

  it('submits form with valid credentials', async () => {
    const mockLogin = vi.mocked(authApi.login);
    mockLogin.mockResolvedValue({
      user: { id: '1', username: '\\COLLEGE\\jdoe', is_blocked: false },
      access_token: 'fake-token',
    });

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await user.type(usernameInput, '\\COLLEGE\\jdoe');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('\\COLLEGE\\jdoe', 'password123');
    });
  });

  it('displays error message on login failure', async () => {
    const mockLogin = vi.mocked(authApi.login);
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await user.type(usernameInput, '\\COLLEGE\\jdoe');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);

    expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
  });

  it('displays blocked account message', async () => {
    const mockLogin = vi.mocked(authApi.login);
    mockLogin.mockRejectedValue({
      statusCode: 403,
      message: 'Your account has been blocked. Please contact support.',
    });

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await user.type(usernameInput, '\\COLLEGE\\blocked');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    expect(await screen.findByText(/contact support/i)).toBeInTheDocument();
  });
});
```

### Testing Best Practices

1. **Unit Tests**: Test individual components in isolation
   - Mock all external dependencies (API calls, context, hooks)
   - Focus on component logic, rendering, and user interactions
   - Use `@testing-library/react` for DOM queries
   - Aim for 70-80% coverage

2. **Integration Tests**: Test component interactions
   - Test multiple components working together
   - Mock only external APIs, use real context/state
   - Test user flows (login → dashboard → session)
   - Focus on critical paths

3. **E2E Tests**: Test critical user flows (using Playwright)
   - Login and navigation
   - Session creation (stop before WebRTC connection)
   - Session history viewing
   - Manual testing required for WebRTC audio/video

4. **Coverage Goals**: Aim for 80% code coverage
   - 80% for utility functions and hooks
   - 70% for components
   - 100% for critical paths (auth, session creation)

5. **Test Structure**: Arrange-Act-Assert pattern
   ```typescript
   it('description', async () => {
     // Arrange: Set up test data and mocks
     const mockData = { ... };
     vi.mocked(apiClient).mockResolvedValue(mockData);
     
     // Act: Perform action
     render(<Component />);
     await user.click(screen.getByRole('button'));
     
     // Assert: Verify outcome
     expect(screen.getByText('Result')).toBeInTheDocument();
   });
   ```

6. **Mock External Dependencies**: API calls, routing, state management
   - Use `vi.mock()` for module mocks
   - Use `vi.fn()` for function mocks
   - Clear mocks between tests with `beforeEach`

---

## Environment Configuration

### Environment Variables

```bash
# .env.local (not committed to Git)

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# WebRTC Services (if needed on frontend)
NEXT_PUBLIC_DAILY_DOMAIN=example.daily.co
NEXT_PUBLIC_LIVEKIT_URL=wss://example.livekit.cloud

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_VIDEO_CALLS=true
NEXT_PUBLIC_ENABLE_SESSION_DOWNLOAD=true

# Sentry Error Tracking
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...
SENTRY_AUTH_TOKEN=... # Server-side only

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

### Environment Variable Usage

```typescript
// lib/config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  
  features: {
    enableVideoCalls: process.env.NEXT_PUBLIC_ENABLE_VIDEO_CALLS === 'true',
    enableSessionDownload: process.env.NEXT_PUBLIC_ENABLE_SESSION_DOWNLOAD === 'true',
  },
  
  webrtc: {
    dailyDomain: process.env.NEXT_PUBLIC_DAILY_DOMAIN,
    livekitUrl: process.env.NEXT_PUBLIC_LIVEKIT_URL,
  },
  
  sentry: {
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  },
} as const;

// Type-safe config access
export type Config = typeof config;
```

**Environment Variable Rules:**
- Prefix with `NEXT_PUBLIC_` for client-side access
- No `NEXT_PUBLIC_` prefix for server-side only (API keys)
- Never commit `.env.local` to Git
- Use `.env.example` to document required variables
- Validate required env vars at build time

---

## Frontend Developer Standards

### Critical Coding Rules

**MANDATORY RULES - AI agents must follow these exactly:**

1. **Never use `console.log` in production code**
   - Use `logger.info()`, `logger.error()`, etc.
   - Console methods only allowed in development with env checks
   ```typescript
   // ❌ Bad
   console.log('User logged in', user);
   
   // ✅ Good
   logger.info('User logged in', { userId: user.id });
   ```

2. **All components must have explicit TypeScript types**
   - No `any` types allowed (strict mode enforced)
   - Define props interfaces for every component
   ```typescript
   // ❌ Bad
   export function Component({ data }: any) { }
   
   // ✅ Good
   interface ComponentProps {
     data: UserData;
   }
   export function Component({ data }: ComponentProps) { }
   ```

3. **Use `'use client'` directive only when necessary**
   - Default to Server Components in Next.js App Router
   - Add `'use client'` only if using: hooks, event handlers, browser APIs
   ```typescript
   // ❌ Bad (unnecessary client component)
   'use client';
   export function StaticContent() {
     return <div>Hello</div>;
   }
   
   // ✅ Good (server component by default)
   export function StaticContent() {
     return <div>Hello</div>;
   }
   
   // ✅ Good (client component needed for hooks)
   'use client';
   export function InteractiveComponent() {
     const [count, setCount] = useState(0);
     return <button onClick={() => setCount(count + 1)}>{count}</button>;
   }
   ```

4. **All API calls must use the api-client wrapper**
   - No direct `fetch()` calls outside of `lib/api-client.ts`
   - Centralized auth handling and error management
   ```typescript
   // ❌ Bad
   const response = await fetch('/api/sessions');
   
   // ✅ Good
   const sessions = await sessionApi.getSessions();
   ```

5. **Form validation must use Zod schemas**
   - Define schemas in `lib/validators.ts`
   - Use with React Hook Form for form handling
   ```typescript
   // lib/validators.ts
   export const loginSchema = z.object({
     username: z.string().regex(/^\\[^\\]+\\[^\\]+$/, 'Invalid username format'),
     password: z.string().min(8, 'Password must be at least 8 characters'),
   });
   ```

6. **Styling must use Tailwind classes**
   - No inline styles or CSS modules
   - Use `cn()` utility for conditional classes
   ```typescript
   // ❌ Bad
   <div style={{ color: 'blue' }}>
   <div className="custom-style">
   
   // ✅ Good
   <div className={cn('text-blue-500', isActive && 'font-bold')}>
   ```

7. **Error boundaries must wrap route segments**
   - Create `error.tsx` in each route folder
   - Catch and display user-friendly errors
   ```typescript
   // app/dashboard/error.tsx
   'use client';
   export default function Error({ error, reset }: ErrorProps) {
     return (
       <div>
         <h2>Something went wrong!</h2>
         <button onClick={reset}>Try again</button>
       </div>
     );
   }
   ```

8. **Async operations must have loading states**
   - Use React Suspense or loading.tsx files
   - Show skeletons or spinners during data fetching
   ```typescript
   // app/dashboard/loading.tsx
   export default function Loading() {
     return <DashboardSkeleton />;
   }
   ```

9. **WebRTC clients must be properly cleaned up**
   - Always call `destroy()` or `leave()` in useEffect cleanup
   - Prevent memory leaks from hanging connections
   ```typescript
   useEffect(() => {
     const client = new DailyClient(config);
     client.join();
     
     return () => {
       client.destroy(); // Cleanup
     };
   }, []);
   ```

10. **Accessibility attributes required**
    - Use semantic HTML (`<button>`, `<nav>`, `<main>`)
    - Add ARIA labels for icon buttons
    - Ensure keyboard navigation works
    ```typescript
    // ❌ Bad
    <div onClick={handleClick}>Click me</div>
    
    // ✅ Good
    <button onClick={handleClick} aria-label="Submit form">
      Click me
    </button>
    ```

11. **Authentication checks on protected pages**
    - Wrap with `<ProtectedRoute>` component
    - Redirect unauthenticated users to login
    ```typescript
    export default function DashboardPage() {
      return (
        <ProtectedRoute>
          <DashboardContent />
        </ProtectedRoute>
      );
    }
    ```

12. **Imports must follow order**
    - React imports first
    - Third-party libraries
    - Local components/utilities
    - Types last
    ```typescript
    import { useState, useEffect } from 'react';
    import { useRouter } from 'next/navigation';
    import { Button } from '@/components/ui/button';
    import { authApi } from '@/lib/api-client';
    import type { User } from '@repo/shared';
    ```

### Quick Reference

**Common Commands:**
```bash
# Development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Type check
pnpm type-check

# Lint
pnpm lint

# Format code
pnpm format

# E2E tests
pnpm test:e2e
```

**Key Import Patterns:**
```typescript
// Components
import { Button } from '@/components/ui/button';
import { LoginForm } from '@/components/auth/LoginForm';

// Hooks
import { useAuth } from '@/components/auth/AuthProvider';
import { useVoiceSession } from '@/hooks/useVoiceSession';

// Utilities
import { cn } from '@/lib/utils';
import { authApi } from '@/lib/api-client';

// Types from shared package
import type { User, Session } from '@repo/shared';

// Next.js
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
```

**File Naming:**
- Pages: `page.tsx` (App Router convention)
- Layouts: `layout.tsx` (App Router convention)
- Components: `PascalCase.tsx`
- Hooks: `useHookName.ts`
- Utilities: `kebab-case.ts`
- Tests: `*.test.tsx` or `*.test.ts`

**Project-Specific Patterns:**
```typescript
// API calls
const sessions = await sessionApi.getSessions({ category: 'Health' });

// Navigation
router.push('/dashboard');

// Toast notifications
import { toast } from '@/components/ui/use-toast';
toast({ title: 'Success', description: 'Session created' });

// Auth check
const { isAuthenticated, user } = useAuth();

// Conditional classes
className={cn('base-class', condition && 'conditional-class')}

// WebRTC cleanup
useEffect(() => {
  const client = new DailyClient(config);
  return () => client.destroy();
}, []);
```

---

## Component Library Integration (shadcn/ui)

### Adding shadcn/ui Components

```bash
# Initialize shadcn/ui (already done in setup)
npx shadcn-ui@latest init

# Add specific components as needed
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add select
npx shadcn-ui@latest add slider
```

### Custom Component Wrapper Example

```typescript
// components/ui/counselor-button.tsx
import { Button, type ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Mic, Video } from 'lucide-react';

interface CounselorButtonProps extends ButtonProps {
  mode: 'voice' | 'video';
}

export function CounselorButton({ mode, className, ...props }: CounselorButtonProps) {
  const Icon = mode === 'voice' ? Mic : Video;
  const bgColor = mode === 'voice' ? 'bg-primary' : 'bg-secondary';
  
  return (
    <Button
      className={cn(
        bgColor,
        'hover:opacity-90 transition-opacity',
        className
      )}
      {...props}
    >
      <Icon className="mr-2 h-4 w-4" />
      {mode === 'voice' ? 'Voice Call' : 'Video Call'}
    </Button>
  );
}
```

---

## Performance Optimization

### Code Splitting

```typescript
// Lazy load heavy components
import dynamic from 'next/dynamic';

const VideoClient = dynamic(
  () => import('@/components/video/VideoClient'),
  { 
    loading: () => <LoadingSpinner />,
    ssr: false, // Disable SSR for WebRTC components
  }
);
```

### Image Optimization

```typescript
// Always use Next.js Image component
import Image from 'next/image';

<Image
  src="/icons/health.svg"
  alt="Health counselor"
  width={48}
  height={48}
  priority={false} // Set true for above-fold images
/>
```

### Bundle Size Monitoring

```typescript
// next.config.js
const config = {
  // Enable bundle analyzer in development
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'disabled',
          generateStatsFile: true,
        })
      );
    }
    return config;
  },
};
```

---

## Accessibility Guidelines

**WCAG 2.1 AA Compliance Required:**

1. **Keyboard Navigation**
   - All interactive elements accessible via Tab
   - Focus indicators visible (2px outline)
   - Logical tab order maintained

2. **Screen Reader Support**
   - Semantic HTML elements
   - ARIA labels for icon-only buttons
   - Live regions for dynamic content (transcripts)

3. **Color Contrast**
   - Text on background: minimum 4.5:1 ratio
   - UI components: minimum 3:1 ratio
   - Use tools like Contrast Checker

4. **Form Labels**
   - All inputs have associated labels
   - Error messages announced to screen readers
   - Required fields indicated

5. **Focus Management**
   - Focus trapped in modals
   - Focus restored after modal close
   - Skip links for main content

**Implementation:**
```typescript
// Accessible button
<button
  onClick={handleClick}
  aria-label="Start voice counseling session"
  className="focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
>
  <Mic className="h-6 w-6" aria-hidden="true" />
</button>

// Accessible form input
<div>
  <label htmlFor="username" className="sr-only">Username</label>
  <input
    id="username"
    type="text"
    aria-required="true"
    aria-invalid={!!error}
    aria-describedby={error ? "username-error" : undefined}
  />
  {error && <span id="username-error" role="alert">{error}</span>}
</div>
```

---

## Next Steps

This frontend architecture document is now complete and ready for implementation. Here are the recommended next steps:

### For Frontend Development Team

1. **Project Setup:**
   - Clone repository and install dependencies (`pnpm install`)
   - Copy `.env.example` to `.env.local` and configure
   - Run `pnpm dev` to start development server
   - Verify Next.js app runs on `localhost:3000`

2. **shadcn/ui Setup:**
   - Run `npx shadcn-ui@latest init`
   - Add required components: `button`, `card`, `input`, `dialog`, `toast`, `select`, `slider`
   - Verify components render correctly

3. **Begin Implementation (Epic 1 Stories):**
   - Story 1.6: Login Page UI
   - Story 1.7: Session State Management
   - Configure TypeScript strict mode
   - Set up ESLint and Prettier

4. **WebRTC Integration (Epic 3 & 4):**
   - Install Daily.co SDK: `pnpm add @daily-co/daily-js`
   - Install LiveKit client: `pnpm add livekit-client`
   - Create wrapper clients in `lib/`
   - Test voice and video connections

### For QA Team

1. Set up Vitest for unit/integration tests
2. Set up Playwright for E2E tests
3. Create test fixtures for common scenarios
4. Manual test plan for WebRTC functionality

### For Design Team

1. Export icons to SVG format (health, career, academic, etc.)
2. Provide logo assets in multiple formats
3. Review color palette alignment with wireframes
4. Validate component designs match wireframes

### Integration with Backend

- Ensure backend API is running on `localhost:8000`
- Verify CORS configuration allows `localhost:3000`
- Test authentication flow end-to-end
- Confirm shared types package is working

---

**Document Status:** ✅ **Complete**  
**Ready for Implementation:** Yes  
**References:** [Backend Architecture](architecture.md), [PRD](prd.md), [Wireframes](wireframes.md)

