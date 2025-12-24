<div align="center">

# 🎓 College Student Counseling Platform

[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AI-powered counseling platform providing instant 24/7 access to specialized counselors through voice and video AI interactions.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **College Student Counseling Platform** addresses the mental health crisis among college students by providing instant, scalable AI counseling. Traditional campus counseling centers face 2-4 week wait times with student-to-counselor ratios exceeding 1:1500. This platform eliminates those barriers.

### 🌟 Key Benefits

| Benefit | Description |
|---------|-------------|
| ⚡ **Instant Access** | Connect to counselors in <30 seconds, 24/7 |
| 🎭 **Dual Modalities** | Voice-only or full video with realistic AI avatars |
| 🔒 **Privacy-First** | FERPA compliant with end-to-end encryption |
| 📈 **Scalable** | Supports 50+ concurrent sessions without degradation |
| 🎯 **Specialized** | Six counselor categories tailored to student needs |

---

## ✨ Features

### 🗣️ Voice Counseling (PipeCat)
- Real-time speech-to-text transcription via **Deepgram Nova-2**
- Natural text-to-speech responses via **Cartesia Sonic**
- Live transcript display during sessions
- Low-latency WebRTC via **Daily.co**

### 🎥 Video Counseling (Beyond Presence)
- Photorealistic AI avatar counselors
- Lip-sync matching within 100ms accuracy
- Emotional expressions (concerned, supportive, thoughtful)
- Graceful degradation to voice-only on poor connections

### 👥 Counselor Categories

| Category | Focus Area |
|----------|------------|
| 🏥 **Health & Wellness** | Physical health, sleep, nutrition, stress |
| 💼 **Career Development** | Job search, interviews, career planning |
| 📚 **Academic Support** | Study skills, time management, coursework |
| 💰 **Financial Aid** | Scholarships, budgeting, loan guidance |
| 🤝 **Social Connection** | Relationships, community, belonging |
| 🌱 **Personal Development** | Goals, self-improvement, mindfulness |

### 🔐 Security & Compliance
- JWT authentication with httpOnly cookies
- AES-256 encryption at rest, TLS 1.3 in transit
- FERPA compliance for student data
- 90-day automatic transcript purging
- Crisis detection with emergency resource display

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Student Browser (WebRTC + HTTPS)                │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   Next.js 14    │    │    Daily.co WebRTC  │    │  LiveKit WebRTC │
│   Frontend      │    │    (Voice Rooms)    │    │  (Video Rooms)  │
│   App Router    │    └─────────────────────┘    └─────────────────┘
└────────┬────────┘                │                        │
         │                         │                        │
         ▼                         ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI (Python 3.11+)                    │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │   │
│  │  │  Auth   │  │ Session │  │Counselor│  │  Orchestration  │ │   │
│  │  │ Router  │  │ Router  │  │ Router  │  │     Router      │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │                         │                        │
         ▼                         ▼                        ▼
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     PipeCat Bot     │    │ Beyond Presence │
│   (Data Store)  │    │  (Voice AI Agent)   │    │  (Avatar API)   │
└─────────────────┘    └─────────┬───────────┘    └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────────┐
              │ Deepgram │ │ Cartesia │ │ Gemini 2.0 / │
              │   STT    │ │   TTS    │ │   GPT-4      │
              └──────────┘ └──────────┘ └──────────────┘
```

---

## 🛠️ Tech Stack

<table>
<tr>
<td valign="top" width="50%">

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.0 | React framework (App Router) |
| React | 18.3.0 | UI library |
| TypeScript | 5.3.3 | Type safety |
| Tailwind CSS | 3.4.1 | Styling |
| shadcn/ui | Latest | Component library |
| Zustand | Latest | State management |

</td>
<td valign="top" width="50%">

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.110.0 | API framework |
| Python | 3.11+ | Runtime |
| SQLAlchemy | 2.0.27 | Async ORM |
| PostgreSQL | 16.1 | Database |
| Pydantic | 2.6.0 | Validation |
| Alembic | Latest | Migrations |

</td>
</tr>
<tr>
<td valign="top">

### AI Services
| Service | Purpose |
|---------|---------|
| PipeCat | Voice AI agent framework |
| Beyond Presence | Avatar video rendering |
| Deepgram Nova-2 | Speech-to-text |
| Cartesia Sonic | Text-to-speech |
| Google Gemini 2.0 | Primary LLM |
| OpenAI GPT-4 | Fallback LLM |

</td>
<td valign="top">

### Infrastructure
| Technology | Purpose |
|------------|---------|
| pnpm | Package manager |
| Turborepo | Monorepo orchestration |
| Docker | Containerization |
| GitHub Actions | CI/CD |
| Daily.co | Voice WebRTC |
| LiveKit | Video WebRTC |

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js | 20.11.0 LTS |
| Python | 3.11+ |
| pnpm | 8.15.0+ |
| Docker | Latest (optional) |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/MADTRONS/GDG.git
cd GDG

# 2. Install frontend dependencies
pnpm install

# 3. Install backend dependencies
cd packages/backend
pip install -r requirements.txt -r requirements-dev.txt
cd ../..

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down
```

#### Option 2: Manual Start

**Terminal 1 — Database:**
```bash
docker-compose up db
```

**Terminal 2 — Backend:**
```bash
cd packages/backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd packages/frontend
pnpm dev
```

### Access Points

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:3000 |
| 🔌 Backend API | http://localhost:8000 |
| 📖 Swagger Docs | http://localhost:8000/docs |
| 📚 ReDoc | http://localhost:8000/redoc |

---

## 💻 Development

### Frontend Commands

```bash
cd packages/frontend

pnpm dev          # Start development server
pnpm build        # Build for production
pnpm lint         # Run ESLint
pnpm format       # Format with Prettier
pnpm test         # Run tests
```

### Backend Commands

```bash
cd packages/backend

uvicorn app.main:app --reload   # Start dev server
ruff check .                     # Lint code
ruff format .                    # Format code
mypy .                           # Type checking
pytest                           # Run tests
pytest --cov=app                 # Tests with coverage
```

### Monorepo Commands

```bash
# From project root
pnpm dev      # Start all dev servers
pnpm build    # Build all packages
pnpm lint     # Lint all packages
pnpm format   # Format all code
pnpm test     # Run all tests
```

### Database Migrations

```bash
cd packages/backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 📁 Project Structure

```
college-counseling-platform/
├── 📂 packages/
│   ├── 📂 frontend/               # Next.js 14 application
│   │   ├── 📂 app/                # App Router pages
│   │   ├── 📂 components/         # React components
│   │   │   ├── 📂 ui/             # shadcn/ui components
│   │   │   └── 📂 features/       # Feature components
│   │   ├── 📂 lib/                # Utilities & helpers
│   │   ├── 📂 types/              # TypeScript types
│   │   └── 📂 public/             # Static assets
│   │
│   └── 📂 backend/                # FastAPI application
│       ├── 📂 app/
│       │   ├── 📄 main.py         # Application entry point
│       │   ├── 📄 config.py       # Configuration
│       │   ├── 📂 routers/        # API route handlers
│       │   ├── 📂 models/         # SQLAlchemy models
│       │   ├── 📂 schemas/        # Pydantic schemas
│       │   ├── 📂 services/       # Business logic
│       │   └── 📂 utils/          # Utilities
│       ├── 📂 tests/              # Test files
│       └── 📂 alembic/            # Database migrations
│
├── 📂 docs/                       # Project documentation
│   ├── 📄 prd.md                  # Product requirements
│   ├── 📄 architecture.md         # Architecture details
│   ├── 📂 stories/                # User stories
│   └── 📂 prd/                    # Epic documentation
│
├── 📂 .github/
│   └── 📂 workflows/              # CI/CD pipelines
│
├── 📄 docker-compose.yml          # Docker orchestration
├── 📄 turbo.json                  # Turborepo config
├── 📄 pnpm-workspace.yaml         # pnpm workspaces
└── 📄 README.md                   # This file
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/counseling_platform

# Authentication
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Daily.co (Voice Calls)
DAILY_API_KEY=your-daily-api-key

# LiveKit (Video Calls)
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-secret
LIVEKIT_URL=wss://your-livekit-server

# Beyond Presence (Avatars)
BEYOND_PRESENCE_API_KEY=your-beyond-presence-key

# Deepgram (Speech-to-Text)
DEEPGRAM_API_KEY=your-deepgram-key

# Cartesia (Text-to-Speech)
CARTESIA_API_KEY=your-cartesia-key

# LLM Providers
GOOGLE_API_KEY=your-google-gemini-key
OPENAI_API_KEY=your-openai-key
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Actions |
|----------|---------|---------|
| **Frontend CI** | PR to `main` | Lint, Type Check, Test, Build |
| **Backend CI** | PR to `main` | Lint, Type Check, Test with Coverage |
| **Deploy** | Push to `main` | Build Images, Push to GHCR, Deploy |

### Required GitHub Secrets

```yaml
# CI Testing
DATABASE_URL_TEST: postgresql://postgres:test@localhost:5432/counseling_test

# Deployment
RAILWAY_TOKEN: your-railway-token
JWT_SECRET_KEY: production-jwt-secret

# Optional
DOCKER_USERNAME: your-docker-username
DOCKER_PASSWORD: your-docker-password
```

### Branch Protection Rules

- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

---

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Frontend tests with coverage
cd packages/frontend && pnpm test:coverage

# Backend tests with coverage
cd packages/backend && pytest --cov=app --cov-report=html

# Open coverage report
open packages/backend/htmlcov/index.html
```

### Code Quality

| Tool | Purpose | Config |
|------|---------|--------|
| ESLint | Frontend linting | `.eslintrc.json` |
| Prettier | Code formatting | `.prettierrc` |
| Ruff | Backend linting | `pyproject.toml` |
| mypy | Type checking | `pyproject.toml` |

---

## 📖 API Documentation

Interactive API documentation is available when the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/logout` | End session |
| GET | `/api/v1/counselors` | List counselor categories |
| POST | `/api/v1/sessions/voice` | Create voice session |
| POST | `/api/v1/sessions/video` | Create video session |
| GET | `/api/v1/sessions/history` | Get session history |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [PRD](docs/prd.md) | Product requirements document |
| [Architecture](docs/architecture.md) | Technical architecture |
| [API Spec](docs/api-spec.md) | API specifications |
| [UI Architecture](docs/ui-architecture.md) | Frontend design system |
| [Crisis Protocol](docs/crisis-protocol.md) | Emergency handling |

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Keep PRs focused and atomic

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- 📧 **Email**: support@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/MADTRONS/GDG/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/MADTRONS/GDG/discussions)

---

<div align="center">

**Built with ❤️ for college students everywhere**

⭐ Star this repo if you find it helpful!

</div>
