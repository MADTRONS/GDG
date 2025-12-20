# College Student Counseling Platform

AI-powered college counseling platform providing instant access to specialized counselors through voice and video AI interactions.

## Project Overview

This platform connects college students with AI counselors across six specialized categories:
- Health & Wellness
- Career Development
- Academic Support
- Financial Aid
- Social Connection
- Personal Development

Built with Next.js 14, FastAPI, and cutting-edge AI services including PipeCat voice agents and Beyond Presence avatars.

## Tech Stack

**Frontend:**
- Next.js 14.2.0 (App Router)
- React 18.3.0
- TypeScript 5.3.3
- Tailwind CSS 3.4.1
- shadcn/ui components
- Zustand for state management

**Backend:**
- FastAPI 0.110.0
- Python 3.11+
- SQLAlchemy 2.0.27 (async)
- PostgreSQL 16.1
- Pydantic 2.6.0

**Infrastructure:**
- Monorepo with pnpm workspaces
- Turborepo for build orchestration
- Docker & Docker Compose
- PostgreSQL database

## Quick Start

### Prerequisites

- Node.js 20.11.0 LTS
- Python 3.11+
- pnpm 8.15.0
- Docker & Docker Compose (optional, for containerized setup)

### Installation

1. **Clone the repository:**
\\\ash
git clone <repository-url>
cd college-counseling-platform
\\\

2. **Install dependencies:**
\\\ash
# Install root and frontend dependencies
pnpm install

# Install backend dependencies
cd packages/backend
pip install -r requirements.txt -r requirements-dev.txt
cd ../..
\\\

3. **Environment setup:**
\\\ash
# Copy environment variables template
cp .env.example .env

# Edit .env with your configuration
\\\

### Running Locally

#### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
\\\ash
cd packages/backend
uvicorn app.main:app --reload --port 8000
\\\

**Terminal 2 - Frontend:**
\\\ash
cd packages/frontend
pnpm dev
\\\

**Terminal 3 - Database (if not using Docker):**
\\\ash
# Start PostgreSQL on localhost:5432
# Create database: counseling_platform
\\\

#### Option 2: Docker Compose

\\\ash
# Start all services (database, backend, frontend)
docker-compose up

# Stop all services
docker-compose down
\\\

### Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Development Workflow

### Frontend Development

\\\ash
cd packages/frontend

# Start dev server
pnpm dev

# Lint code
pnpm lint

# Format code
pnpm format

# Build for production
pnpm build
\\\

### Backend Development

\\\ash
cd packages/backend

# Start dev server
uvicorn app.main:app --reload

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy .

# Run tests
pytest
\\\

### Monorepo Commands

\\\ash
# Run all dev servers
pnpm dev

# Build all packages
pnpm build

# Lint all packages
pnpm lint

# Format all code
pnpm format
\\\

## Project Structure

\\\
college-counseling-platform/
 packages/
    frontend/              # Next.js application
       app/              # App Router pages
       components/       # React components
       lib/             # Utilities
       public/          # Static assets
   
    backend/              # FastAPI application
        app/
           main.py      # FastAPI entry point
           config.py    # Configuration
           routers/     # API routers
        tests/           # Test files

 docs/                     # Project documentation
 .github/                  # CI/CD workflows
 docker-compose.yml
 .env.example
 README.md
\\\

## Environment Variables

See .env.example for all required environment variables. Key variables:

- DATABASE_URL: PostgreSQL connection string
- JWT_SECRET_KEY: Secret key for JWT tokens
- DAILY_API_KEY: Daily.co API key for voice calls
- LIVEKIT_API_KEY: LiveKit API key for video calls
- BEYOND_PRESENCE_API_KEY: Avatar API key
- DEEPGRAM_API_KEY: Speech-to-text API key
- CARTESIA_API_KEY: Text-to-speech API key
- GOOGLE_API_KEY: Google Gemini API key
- OPENAI_API_KEY: OpenAI API key (fallback)
## CI/CD

This project uses GitHub Actions for continuous integration and deployment.

### GitHub Secrets Configuration

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

**Required for CI:**
- `DATABASE_URL_TEST`: PostgreSQL connection string for CI tests
  - Example: `postgresql://postgres:testpassword@localhost:5432/counseling_test`

**Required for Deployment:**
- `RAILWAY_TOKEN`: Railway deployment token (if using Railway)
- `JWT_SECRET_KEY`: Secret key for JWT signing in production

**Optional:**
- `DOCKER_USERNAME`: Docker registry username (if using Docker Hub)
- `DOCKER_PASSWORD`: Docker registry password

### CI Workflows

**Frontend CI** (`.github/workflows/ci-frontend.yml`):
- Runs on PRs affecting frontend code
- ESLint, TypeScript checking, tests
- Docker image build validation

**Backend CI** (`.github/workflows/ci-backend.yml`):
- Runs on PRs affecting backend code
- Ruff linting, mypy type checking, pytest with coverage
- PostgreSQL service container for integration tests
- Docker image build validation

**Deployment** (`.github/workflows/deploy.yml`):
- Runs on push to main branch
- Builds and pushes Docker images to GitHub Container Registry
- Triggers Railway deployment (if configured)

### Branch Protection

Recommended branch protection rules for `main`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (Frontend CI, Backend CI)
- ✅ Require branches to be up to date before merging
## Testing

\\\ash
# Frontend tests
cd packages/frontend
pnpm test

# Backend tests
cd packages/backend
pytest

# Run all tests
pnpm test
\\\

## Code Style

- **Frontend:** ESLint + Prettier with 100-character line length
- **Backend:** Ruff + mypy with 100-character line length
- **Formatting:** Automatic via pre-commit hooks (when configured)

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Run linting and formatting
5. Submit a pull request

## License

[Add license information]

## Support

For questions or issues, please contact the development team.
