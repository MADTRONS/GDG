# College Student Counseling Platform - Documentation Hub

**Version:** 1.0  
**Last Updated:** December 19, 2025  
**Status:** Complete & Ready for Development

---

## 📚 Documentation Overview

This documentation suite provides complete specifications for building the College Student Counseling Platform - an AI-powered system delivering instant, 24/7 voice and video counseling to college students across multiple specialty areas.

---

## 🗂️ Document Index

### Core Documents

#### 1. [Product Requirements Document (PRD)](prd.md)
**Purpose:** Complete product specification with functional and non-functional requirements

**What's Inside:**
- Goals and background context
- Complete functional requirements (FR1-FR20)
- Non-functional requirements (NFR1-NFR15) including performance, security, and compliance
- UI design goals and branding guidelines
- Technical assumptions and tech stack decisions
- Epic breakdown with user stories

**Who Needs This:** Product managers, designers, developers (all team members)

**Key Sections:**
- [Requirements](prd.md#requirements) - All FR/NFR specifications
- [User Interface Design Goals](prd.md#user-interface-design-goals) - UX vision and branding
- [Technical Assumptions](prd.md#technical-assumptions) - Tech stack and testing strategy
- [Epic List](prd.md#epic-list) - 5 major epics with story breakdown

---

#### 2. [Backend Architecture](architecture.md)
**Purpose:** Complete backend system design, service architecture, and technical specifications

**What's Inside:**
- High-level architecture and service design
- Complete tech stack table with versions and rationale
- Data models (User, Session, CounselorCategory, TranscriptMessage, CrisisEvent)
- Service architecture and integration patterns
- Sequence diagrams for voice/video flows
- Real-time transcript transport via WebSocket
- Environment variables specification
- Database indexing strategy
- Circuit breaker configuration
- Deployment configuration (Docker, docker-compose)
- FERPA compliance checklist
- Performance monitoring SLAs

**Who Needs This:** Backend developers, DevOps, architects

**Key Sections:**
- [Tech Stack](architecture.md#tech-stack) - Definitive technology selections
- [Data Models](architecture.md#data-models) - Database schemas
- [Real-Time Transcript Transport](architecture.md#real-time-transcript-transport) - WebSocket architecture
- [Environment Variables](architecture.md#environment-variables-specification) - Complete .env specs
- [Deployment Configuration](architecture.md#deployment-configuration) - Docker setup

---

#### 3. [Frontend Architecture (UI Architecture)](ui-architecture.md)
**Purpose:** Complete frontend design, component structure, and client-side architecture

**What's Inside:**
- Next.js 14 App Router project structure
- Complete frontend tech stack
- Component standards and naming conventions
- State management strategy (Context vs Zustand)
- API integration patterns
- Authentication flow implementation
- WebRTC client integration (Daily.co, LiveKit)
- Testing strategy
- Accessibility requirements

**Who Needs This:** Frontend developers, UI/UX designers

**Key Sections:**
- [Project Structure](ui-architecture.md#project-structure) - Complete folder layout
- [Component Standards](ui-architecture.md#component-standards) - Templates and conventions
- [State Management](ui-architecture.md#state-management) - Context vs Zustand guidelines
- [API Integration](ui-architecture.md#api-integration) - Client implementation

---

#### 4. [Wireframes Specification](wireframes.md)
**Purpose:** Detailed UI/UX specifications for all screens with component measurements

**What's Inside:**
- Design system foundation (colors, typography, spacing, shadows)
- Screen-by-screen wireframe specifications:
  - Login Page
  - Main Dashboard
  - Voice Session View
  - Video Session View
  - Session History
- Component specifications with exact measurements
- Responsive design breakpoints
- Accessibility requirements

**Who Needs This:** UI/UX designers, frontend developers

**Key Sections:**
- [Design System Foundation](wireframes.md#design-system-foundation) - Colors, typography, spacing
- [Screen Wireframes](wireframes.md#screen-1-login-page) - All 5+ screen specifications

---

### API & Integration Documents

#### 5. [API Specification](api-spec.md)
**Purpose:** Complete REST API contract and WebSocket protocol

**What's Inside:**
- All REST API endpoints with request/response schemas
- Authentication endpoints (login, logout, me)
- Counselor endpoints (list categories)
- Session endpoints (create voice/video, end, history, transcript)
- WebSocket protocol for real-time transcript streaming
- Rate limiting specifications
- Error codes reference
- Health check endpoints

**Who Needs This:** Frontend developers, backend developers, QA engineers

**Key Sections:**
- [Authentication Endpoints](api-spec.md#authentication-endpoints) - Login/logout/me
- [Session Endpoints](api-spec.md#session-endpoints) - Voice/video creation and management
- [WebSocket Endpoint](api-spec.md#websocket-endpoint) - Real-time transcript protocol
- [Error Codes Reference](api-spec.md#error-codes-reference) - All error codes

---

### Safety & Configuration Documents

#### 6. [Crisis Detection Protocol](crisis-protocol.md)
**Purpose:** Critical safety feature for detecting students in distress

**What's Inside:**
- Two-tier crisis detection system (keyword + LLM semantic analysis)
- Complete crisis keyword dictionary
- False positive prevention strategies
- LLM semantic analysis prompt
- Emergency resources configuration (national + campus-specific)
- Crisis alert UI specifications
- Crisis event logging schema
- FERPA compliance and legal considerations
- Testing scenarios
- Performance metrics and monitoring

**Who Needs This:** ALL developers (safety-critical), product managers, legal/compliance

**Key Sections:**
- [Crisis Keyword Dictionary](crisis-protocol.md#crisis-keyword-dictionary) - Keywords and exclusions
- [Emergency Resources Configuration](crisis-protocol.md#emergency-resources-configuration) - Hotlines and resources
- [Crisis Alert UI Implementation](crisis-protocol.md#crisis-alert-ui-implementation) - Banner design
- [Compliance & Legal Considerations](crisis-protocol.md#compliance--legal-considerations) - FERPA and liability

---

#### 7. [Counselor Categories Seed Data](counselor-categories.json)
**Purpose:** Configuration data for all 6 counselor categories

**What's Inside:**
- Health & Wellness counselor configuration
- Career Counseling configuration
- Academic Success configuration
- Financial Guidance configuration
- Social & Relationships configuration
- Personal Growth configuration
- Avatar mapping for Beyond Presence
- System prompts for each counselor personality
- Color schemes and icons
- Deployment checklist

**Who Needs This:** Backend developers (database seeding), product managers, content writers

**Key Sections:**
- `categories` array - All 6 counselor configurations
- `avatar_mapping` - Beyond Presence avatar IDs
- `deployment_checklist` - Setup steps

---

## 🎯 Quick Start Guides

### For Project Managers / Product Owners
1. Start with [PRD](prd.md) - Understand product vision and requirements
2. Review [Crisis Protocol](crisis-protocol.md) - Understand safety features
3. Check [Wireframes](wireframes.md) - Visualize the user experience

### For Backend Developers
1. Read [Backend Architecture](architecture.md) - System design and tech stack
2. Review [API Specification](api-spec.md) - Endpoint contracts
3. Study [Crisis Protocol](crisis-protocol.md) - Implement crisis detection
4. Check [Counselor Categories](counselor-categories.json) - Seed data structure

### For Frontend Developers
1. Read [Frontend Architecture](ui-architecture.md) - Project structure and patterns
2. Review [Wireframes](wireframes.md) - UI specifications
3. Study [API Specification](api-spec.md) - API integration
4. Check [Crisis Protocol](crisis-protocol.md) - Crisis banner implementation

### For QA Engineers
1. Review [PRD](prd.md) - All requirements to test
2. Study [API Specification](api-spec.md) - API test cases
3. Read [Crisis Protocol](crisis-protocol.md) - Safety testing scenarios
4. Check [Backend Architecture](architecture.md#test-data-strategy) - Test data

### For DevOps / Platform Engineers
1. Review [Backend Architecture](architecture.md#deployment-configuration) - Docker setup
2. Check [Environment Variables](architecture.md#environment-variables-specification) - Config requirements
3. Study [Performance Monitoring](architecture.md#performance-monitoring-slas) - SLA targets
4. Review [API Specification](api-spec.md#health-check-endpoints) - Health checks

### For UI/UX Designers
1. Read [PRD - UI Design Goals](prd.md#user-interface-design-goals) - Design vision
2. Study [Wireframes](wireframes.md) - Complete UI specifications
3. Review [Frontend Architecture](ui-architecture.md#component-standards) - Component patterns

---

## 📋 Development Checklists

### Before Starting Development

- [ ] All team members have read the [PRD](prd.md)
- [ ] Backend team has reviewed [Backend Architecture](architecture.md)
- [ ] Frontend team has reviewed [Frontend Architecture](ui-architecture.md) and [Wireframes](wireframes.md)
- [ ] All developers understand [Crisis Protocol](crisis-protocol.md) (safety-critical)
- [ ] API contract ([API Spec](api-spec.md)) is agreed upon by frontend/backend teams
- [ ] Environment variables template created from [architecture doc](architecture.md#environment-variables-specification)
- [ ] Counselor seed data ([counselor-categories.json](counselor-categories.json)) reviewed with stakeholders

### Sprint 1 - Foundation & Authentication

**Backend:**
- [ ] Repository structure from [architecture doc](architecture.md#project-structure)
- [ ] Database schema with [data models](architecture.md#data-models)
- [ ] Authentication endpoints per [API spec](api-spec.md#authentication-endpoints)
- [ ] Seed counselor categories from [JSON file](counselor-categories.json)

**Frontend:**
- [ ] Next.js 14 project structure from [UI architecture](ui-architecture.md#project-structure)
- [ ] Design system from [wireframes](wireframes.md#design-system-foundation)
- [ ] Login page per [wireframes](wireframes.md#screen-1-login-page)
- [ ] Authentication flow per [UI architecture](ui-architecture.md#authentication-context)

### Sprint 2 - Dashboard & Counselor Selection

**Backend:**
- [ ] Counselor endpoints per [API spec](api-spec.md#counselor-endpoints)
- [ ] Session creation stubs

**Frontend:**
- [ ] Dashboard page per [wireframes](wireframes.md#screen-2-main-dashboard)
- [ ] Counselor cards with data from API
- [ ] Navigation flow

### Sprint 3 - Voice Calling Integration

**Backend:**
- [ ] Daily.co integration per [architecture](architecture.md#voice-session-service)
- [ ] PipeCat bot spawning
- [ ] WebSocket transcript streaming per [API spec](api-spec.md#websocket-endpoint)
- [ ] Crisis detection per [crisis protocol](crisis-protocol.md)

**Frontend:**
- [ ] Voice session page per [wireframes](wireframes.md#screen-3-voice-session-view)
- [ ] Daily.co client integration
- [ ] Real-time transcript display
- [ ] Crisis alert banner per [crisis protocol](crisis-protocol.md#crisis-alert-ui-implementation)

### Sprint 4 - Video Calling Integration

**Backend:**
- [ ] LiveKit integration per [architecture](architecture.md#video-session-service)
- [ ] Beyond Presence avatar integration
- [ ] Video quality degradation per [PRD NFR13](prd.md#non-functional-requirements)

**Frontend:**
- [ ] Video session page per [wireframes](wireframes.md#screen-4-video-session-view)
- [ ] LiveKit client integration
- [ ] Avatar player component
- [ ] Video controls

### Sprint 5 - Session History & Polish

**Backend:**
- [ ] Session history endpoint per [API spec](api-spec.md#get-sessionshistory)
- [ ] Transcript retrieval
- [ ] Data retention job (90-day purge)

**Frontend:**
- [ ] Session history page per [wireframes](wireframes.md#screen-5-session-history)
- [ ] Transcript view
- [ ] Filters and pagination
- [ ] Performance optimization

---

## 🔗 External References

### Third-Party Documentation
- [PipeCat Framework](https://github.com/pipecat-ai/pipecat) - Voice AI agent framework
- [Daily.co API Docs](https://docs.daily.co/) - WebRTC voice infrastructure
- [LiveKit Documentation](https://docs.livekit.io/) - Video streaming
- [Beyond Presence API](https://beyondpresence.ai/docs) - AI avatar service
- [Deepgram API](https://developers.deepgram.com/) - Speech-to-text
- [Cartesia API](https://cartesia.ai/docs) - Text-to-speech
- [Google Gemini API](https://ai.google.dev/docs) - LLM primary
- [OpenAI API](https://platform.openai.com/docs) - LLM fallback

### Framework Documentation
- [Next.js 14 Docs](https://nextjs.org/docs) - Frontend framework
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Backend framework
- [shadcn/ui Components](https://ui.shadcn.com/) - UI component library
- [Tailwind CSS](https://tailwindcss.com/docs) - Styling framework

---

## 📊 Document Status Matrix

| Document | Version | Status | Last Updated | Owner |
|----------|---------|--------|--------------|-------|
| [PRD](prd.md) | 1.0 | ✅ Complete | 2025-12-19 | Product Team |
| [Backend Architecture](architecture.md) | 1.0 | ✅ Complete | 2025-12-19 | Architecture Team |
| [Frontend Architecture](ui-architecture.md) | 1.0 | ✅ Complete | 2025-12-19 | Architecture Team |
| [Wireframes](wireframes.md) | 1.0 | ✅ Complete | 2025-12-19 | Design Team |
| [API Specification](api-spec.md) | 1.0 | ✅ Complete | 2025-12-19 | Architecture Team |
| [Crisis Protocol](crisis-protocol.md) | 1.0 | ✅ Complete | 2025-12-19 | Product/Safety Team |
| [Counselor Categories](counselor-categories.json) | 1.0 | ✅ Complete | 2025-12-19 | Product/Content Team |

---

## 🚨 Critical Safety Note

⚠️ **ALL DEVELOPERS MUST READ [crisis-protocol.md](crisis-protocol.md) BEFORE IMPLEMENTING ANY FEATURES**

The crisis detection system is a safety-critical feature. Incorrect implementation could put students at risk. The crisis protocol document provides:
- Exact keywords to detect
- False positive prevention strategies
- Emergency resources to display
- Legal compliance requirements

**DO NOT SKIP THIS DOCUMENT.**

---

## 📞 Team Contacts

**For Documentation Questions:**
- Architecture: Winston (Architect)
- Product Requirements: Mary (Business Analyst)
- Safety/Crisis Protocol: Product & Legal Teams
- API Contracts: Dev Leads (Frontend & Backend)

**For Technical Issues:**
- Backend: Backend Lead
- Frontend: Frontend Lead
- DevOps: Platform Team
- External Services: Integration Team

---

## 🔄 Document Update Process

1. **Propose Changes:** Open issue or PR with proposed changes
2. **Review:** Relevant team members review
3. **Approve:** Architecture team approves technical changes, product team approves requirements
4. **Update:** Make changes and update version numbers
5. **Communicate:** Notify all teams of significant changes

**Version Numbering:**
- Major (1.x): Significant architectural or requirement changes
- Minor (x.1): New sections, clarifications, non-breaking updates

---

## 📈 Project Readiness Status

**Overall Readiness:** 🟢 **95% - Ready for Development**

| Area | Status | Notes |
|------|--------|-------|
| Product Requirements | 🟢 Complete | All FR/NFR documented |
| Architecture Design | 🟢 Complete | Backend & frontend specs ready |
| API Contracts | 🟢 Complete | All endpoints specified |
| Safety Features | 🟢 Complete | Crisis protocol defined |
| UI/UX Design | 🟢 Complete | All screens wireframed |
| Environment Setup | 🟢 Complete | Docker configs & env vars ready |
| Test Strategy | 🟢 Complete | Test data & scenarios defined |
| Deployment Plan | 🟢 Complete | Docker & Railway configs ready |

**Remaining 5%:** External service account setup (Daily.co, LiveKit, Beyond Presence, etc.)

---

## 🎓 Learning Path for New Team Members

### Day 1: Product Understanding
- [ ] Read [PRD](prd.md) goals and background
- [ ] Review [PRD requirements](prd.md#requirements) (FR1-20, NFR1-15)
- [ ] Study [wireframes](wireframes.md) to understand user experience
- [ ] Read [crisis protocol](crisis-protocol.md) (mandatory)

### Day 2: Technical Architecture
- [ ] Read [Backend Architecture](architecture.md) high-level overview
- [ ] Read [Frontend Architecture](ui-architecture.md) high-level overview
- [ ] Review [API Specification](api-spec.md) endpoints
- [ ] Understand [counselor categories](counselor-categories.json) structure

### Day 3: Deep Dive (Role-Specific)
**Backend Developers:**
- [ ] Study [data models](architecture.md#data-models)
- [ ] Review [service architecture](architecture.md#service-architecture)
- [ ] Understand [WebSocket transport](architecture.md#real-time-transcript-transport)
- [ ] Check [deployment config](architecture.md#deployment-configuration)

**Frontend Developers:**
- [ ] Study [project structure](ui-architecture.md#project-structure)
- [ ] Review [component standards](ui-architecture.md#component-standards)
- [ ] Understand [state management](ui-architecture.md#state-management)
- [ ] Check [wireframe specs](wireframes.md) in detail

### Day 4: Setup & First Task
- [ ] Set up local development environment
- [ ] Run through "Before Starting Development" checklist above
- [ ] Pick first starter task from Sprint 1 backlog
- [ ] Ask questions in team channels

---

## 💡 Tips for Using This Documentation

1. **Use Ctrl+F (or Cmd+F):** Search for specific terms across documents
2. **Bookmark Frequently Used Sections:** Keep API spec and architecture docs handy
3. **Check Version Numbers:** Ensure you're referencing the latest version
4. **Cross-Reference:** Documents reference each other - follow the links
5. **Suggest Improvements:** Documentation is never perfect - suggest updates via PR

---

## 📜 License & Confidentiality

**Status:** Internal documentation - Confidential  
**Audience:** Development team and authorized stakeholders only  
**Distribution:** Do not share outside project team without approval

---

**Last Updated:** December 19, 2025  
**Documentation Version:** 1.0  
**Next Review Date:** After Sprint 1 completion

---

**Happy Building! 🚀**
