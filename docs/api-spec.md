# API Specification - College Student Counseling Platform

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Complete  
**Base URL:** `http://localhost:8000/api/v1` (development), `https://api.counseling-platform.edu/api/v1` (production)

---

## Overview

This document defines the complete REST API contract for the College Student Counseling Platform. All endpoints use JSON for request/response bodies unless otherwise specified. Authentication is handled via JWT tokens stored in httpOnly cookies.

### API Conventions

- **HTTP Methods:** Standard REST semantics (GET, POST, PUT, DELETE)
- **Status Codes:** 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Internal Server Error)
- **Date Format:** ISO 8601 UTC timestamps (`2025-12-19T14:30:00Z`)
- **Error Response Format:**
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable error message",
      "details": {} // Optional additional context
    }
  }
  ```

---

## Authentication Endpoints

### POST /auth/login

Authenticate a student and create a session.

**Request Body:**
```json
{
  "username": "\\domain\\jsmith",
  "password": "securePassword123"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "\\domain\\jsmith",
    "first_name": "John",
    "last_name": "Smith",
    "is_blocked": false
  },
  "message": "Login successful"
}
```

**Sets Cookie:** `access_token` (httpOnly, secure, sameSite=strict, max-age=86400)

**Error Responses:**
- `400` - Invalid credentials format
  ```json
  {
    "error": {
      "code": "INVALID_CREDENTIALS_FORMAT",
      "message": "Username must be in format \\domain\\username"
    }
  }
  ```
- `401` - Authentication failed
  ```json
  {
    "error": {
      "code": "AUTHENTICATION_FAILED",
      "message": "Invalid username or password"
    }
  }
  ```
- `403` - Account blocked
  ```json
  {
    "error": {
      "code": "ACCOUNT_BLOCKED",
      "message": "Your account has been restricted. Please contact support at support@university.edu or call (555) 123-4567."
    }
  }
  ```

---

### POST /auth/logout

End the current session and clear authentication cookie.

**Authentication:** Required

**Request Body:** None

**Success Response (200):**
```json
{
  "message": "Logout successful"
}
```

**Clears Cookie:** `access_token`

---

### GET /auth/me

Retrieve current authenticated user information.

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "\\domain\\jsmith",
  "first_name": "John",
  "last_name": "Smith",
  "is_blocked": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401` - Not authenticated
  ```json
  {
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Authentication required"
    }
  }
  ```

---

## Counselor Endpoints

### GET /counselors/categories

Retrieve all available counselor categories with their configurations.

**Authentication:** Required

**Success Response (200):**
```json
{
  "categories": [
    {
      "id": "health",
      "name": "Health & Wellness",
      "description": "Physical and mental health support, stress management, sleep issues",
      "icon": "heart-pulse",
      "voice_enabled": true,
      "video_enabled": true,
      "avatar_id": "bp_health_avatar_01",
      "system_prompt": "You are a compassionate health counselor..."
    },
    {
      "id": "career",
      "name": "Career Counseling",
      "description": "Job search guidance, resume help, interview preparation",
      "icon": "briefcase",
      "voice_enabled": true,
      "video_enabled": true,
      "avatar_id": "bp_career_avatar_01",
      "system_prompt": "You are an experienced career advisor..."
    }
    // ... additional categories
  ]
}
```

---

## Session Endpoints

### POST /sessions/voice/create

Create a new voice counseling session and Daily.co room.

**Authentication:** Required

**Request Body:**
```json
{
  "counselor_category": "health"
}
```

**Success Response (201):**
```json
{
  "session": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "counselor_category": "health",
    "mode": "voice",
    "status": "initializing",
    "created_at": "2025-12-19T14:30:00Z"
  },
  "room": {
    "url": "https://university.daily.co/counseling-session-abc123",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-12-19T16:30:00Z"
  },
  "websocket_url": "wss://api.counseling-platform.edu/ws/sessions/660e8400-e29b-41d4-a716-446655440000/transcript"
}
```

**Error Responses:**
- `400` - Invalid category
  ```json
  {
    "error": {
      "code": "INVALID_CATEGORY",
      "message": "Counselor category 'invalid' does not exist",
      "details": {
        "valid_categories": ["health", "career", "academic", "financial", "social", "personal-development"]
      }
    }
  }
  ```
- `503` - Service unavailable
  ```json
  {
    "error": {
      "code": "SERVICE_UNAVAILABLE",
      "message": "Unable to create voice session. Daily.co service is temporarily unavailable.",
      "details": {
        "retry_after_seconds": 30
      }
    }
  }
  ```

---

### POST /sessions/video/create

Create a new video counseling session with Beyond Presence avatar.

**Authentication:** Required

**Request Body:**
```json
{
  "counselor_category": "career"
}
```

**Success Response (201):**
```json
{
  "session": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "counselor_category": "career",
    "mode": "video",
    "status": "initializing",
    "created_at": "2025-12-19T14:35:00Z"
  },
  "room": {
    "url": "wss://livekit.counseling-platform.edu",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-12-19T16:35:00Z"
  },
  "avatar": {
    "id": "bp_career_avatar_01",
    "stream_url": "https://stream.beyondpresence.ai/avatar-abc123"
  },
  "websocket_url": "wss://api.counseling-platform.edu/ws/sessions/770e8400-e29b-41d4-a716-446655440000/transcript"
}
```

---

### POST /sessions/{session_id}/end

End an active counseling session.

**Authentication:** Required

**Path Parameters:**
- `session_id` (UUID) - Session identifier

**Request Body:**
```json
{
  "reason": "user_ended" // Optional: "user_ended", "timeout", "error"
}
```

**Success Response (200):**
```json
{
  "session": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "counselor_category": "health",
    "mode": "voice",
    "status": "completed",
    "duration_seconds": 1842,
    "started_at": "2025-12-19T14:30:00Z",
    "ended_at": "2025-12-19T15:00:42Z"
  },
  "transcript_available": true
}
```

**Error Responses:**
- `404` - Session not found
- `403` - Session belongs to different user
- `409` - Session already ended

---

### GET /sessions/history

Retrieve user's counseling session history with pagination and filters.

**Authentication:** Required

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `limit` (integer, default: 20, max: 100) - Items per page
- `category` (string, optional) - Filter by counselor category
- `mode` (string, optional) - Filter by mode ("voice" or "video")
- `start_date` (ISO 8601, optional) - Filter sessions from this date
- `end_date` (ISO 8601, optional) - Filter sessions until this date

**Example Request:**
```
GET /sessions/history?page=1&limit=20&category=health&mode=voice
```

**Success Response (200):**
```json
{
  "sessions": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "counselor_category": "health",
      "category_name": "Health & Wellness",
      "mode": "voice",
      "status": "completed",
      "duration_seconds": 1842,
      "started_at": "2025-12-19T14:30:00Z",
      "ended_at": "2025-12-19T15:00:42Z",
      "transcript_available": true,
      "crisis_detected": false
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "counselor_category": "health",
      "category_name": "Health & Wellness",
      "mode": "video",
      "status": "completed",
      "duration_seconds": 2156,
      "started_at": "2025-12-15T10:15:00Z",
      "ended_at": "2025-12-15T10:50:56Z",
      "transcript_available": true,
      "crisis_detected": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 42,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### GET /sessions/{session_id}

Retrieve detailed information about a specific session.

**Authentication:** Required

**Path Parameters:**
- `session_id` (UUID) - Session identifier

**Success Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "counselor_category": "health",
  "category_name": "Health & Wellness",
  "mode": "voice",
  "status": "completed",
  "duration_seconds": 1842,
  "started_at": "2025-12-19T14:30:00Z",
  "ended_at": "2025-12-19T15:00:42Z",
  "connection_quality_avg": "excellent",
  "crisis_detected": false,
  "transcript_message_count": 47
}
```

**Error Responses:**
- `404` - Session not found
- `403` - Session belongs to different user

---

### GET /sessions/{session_id}/transcript

Retrieve the full transcript of a completed session.

**Authentication:** Required

**Path Parameters:**
- `session_id` (UUID) - Session identifier

**Success Response (200):**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "transcript": [
    {
      "id": "msg_001",
      "speaker": "student",
      "text": "Hi, I've been having trouble sleeping lately.",
      "timestamp": "2025-12-19T14:30:15Z"
    },
    {
      "id": "msg_002",
      "speaker": "counselor",
      "text": "I understand sleep issues can be really challenging. Can you tell me more about what's been going on?",
      "timestamp": "2025-12-19T14:30:22Z"
    },
    {
      "id": "msg_003",
      "speaker": "student",
      "text": "I stay up late studying and my mind races when I try to sleep.",
      "timestamp": "2025-12-19T14:30:45Z"
    }
    // ... additional messages
  ],
  "metadata": {
    "counselor_category": "health",
    "mode": "voice",
    "duration_seconds": 1842,
    "message_count": 47,
    "generated_at": "2025-12-19T15:00:42Z"
  }
}
```

**Error Responses:**
- `404` - Session or transcript not found
- `403` - Session belongs to different user
- `410` - Transcript has been purged (>90 days old and not saved)

---

### DELETE /sessions/{session_id}/transcript

Delete a session transcript (student privacy control).

**Authentication:** Required

**Path Parameters:**
- `session_id` (UUID) - Session identifier

**Success Response (204):**
No content

**Error Responses:**
- `404` - Session not found
- `403` - Session belongs to different user
- `409` - Transcript already deleted

---

### POST /sessions/{session_id}/transcript/save

Mark a transcript to be saved beyond the 90-day automatic purge.

**Authentication:** Required

**Path Parameters:**
- `session_id` (UUID) - Session identifier

**Request Body:**
```json
{
  "retention_days": 365 // Optional, default: indefinite
}
```

**Success Response (200):**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440000",
  "saved": true,
  "expires_at": "2026-12-19T15:00:42Z" // null if indefinite
}
```

---

## WebSocket Endpoint

### WS /ws/sessions/{session_id}/transcript

Real-time transcript streaming during active sessions.

**Authentication:** Required (JWT token passed as query parameter `?token=...`)

**Connection URL:**
```
wss://api.counseling-platform.edu/ws/sessions/660e8400-e29b-41d4-a716-446655440000/transcript?token=eyJhbGci...
```

**Message Format (Server → Client):**

**Transcript Message:**
```json
{
  "type": "transcript",
  "data": {
    "id": "msg_042",
    "speaker": "counselor",
    "text": "That's a great question. Let me explain...",
    "timestamp": "2025-12-19T14:45:30Z",
    "is_final": true
  }
}
```

**Interim Transcript (for live updates):**
```json
{
  "type": "transcript",
  "data": {
    "id": "msg_043_interim",
    "speaker": "student",
    "text": "I think that makes sen...",
    "timestamp": "2025-12-19T14:45:45Z",
    "is_final": false
  }
}
```

**Connection Quality Update:**
```json
{
  "type": "connection_quality",
  "data": {
    "quality": "good",
    "bandwidth_mbps": 2.4,
    "latency_ms": 45,
    "packet_loss_percent": 0.5
  }
}
```

**Crisis Detected:**
```json
{
  "type": "crisis_alert",
  "data": {
    "detected_at": "2025-12-19T14:46:00Z",
    "keywords_matched": ["suicide"],
    "emergency_resources": [
      {
        "name": "National Suicide Prevention Lifeline",
        "phone": "988",
        "url": "https://988lifeline.org"
      },
      {
        "name": "Campus Security",
        "phone": "(555) 123-4567",
        "available_24_7": true
      }
    ]
  }
}
```

**Session Status Update:**
```json
{
  "type": "session_status",
  "data": {
    "status": "active",
    "duration_seconds": 420
  }
}
```

**Error Message:**
```json
{
  "type": "error",
  "data": {
    "code": "TRANSCRIPTION_SERVICE_ERROR",
    "message": "Temporary issue with transcription. Audio continues normally.",
    "recoverable": true
  }
}
```

**Message Format (Client → Server):**

**Heartbeat (every 30 seconds):**
```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong",
  "data": {
    "timestamp": "2025-12-19T14:45:50Z"
  }
}
```

---

## Health Check Endpoints

### GET /health

Basic health check for load balancers.

**Authentication:** None

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T14:30:00Z"
}
```

---

### GET /health/detailed

Detailed health check including external service status.

**Authentication:** Required (admin only)

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T14:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 5
    },
    "daily_co": {
      "status": "healthy",
      "latency_ms": 120
    },
    "livekit": {
      "status": "healthy",
      "latency_ms": 95
    },
    "deepgram": {
      "status": "healthy",
      "latency_ms": 80
    },
    "beyond_presence": {
      "status": "degraded",
      "latency_ms": 450,
      "message": "High latency detected"
    },
    "gemini": {
      "status": "healthy",
      "latency_ms": 200
    }
  }
}
```

---

## Rate Limiting

All authenticated endpoints are subject to rate limiting:

- **Default:** 100 requests per minute per user
- **Session Creation:** 10 requests per minute per user
- **WebSocket Connections:** 5 concurrent connections per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1703001600
```

**Rate Limit Exceeded Response (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 42 seconds.",
    "details": {
      "retry_after_seconds": 42
    }
  }
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS_FORMAT` | 400 | Username format incorrect |
| `AUTHENTICATION_FAILED` | 401 | Invalid username/password |
| `ACCOUNT_BLOCKED` | 403 | User account restricted |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `INVALID_CATEGORY` | 400 | Unknown counselor category |
| `SESSION_NOT_FOUND` | 404 | Session does not exist |
| `SESSION_ALREADY_ENDED` | 409 | Session already completed |
| `TRANSCRIPT_NOT_AVAILABLE` | 404 | Transcript not yet generated |
| `TRANSCRIPT_PURGED` | 410 | Transcript auto-deleted |
| `SERVICE_UNAVAILABLE` | 503 | External service down |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

---

## OpenAPI Schema

The complete OpenAPI 3.0 schema is automatically generated by FastAPI and available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **JSON Schema:** `http://localhost:8000/openapi.json`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-19 | Initial API specification |
