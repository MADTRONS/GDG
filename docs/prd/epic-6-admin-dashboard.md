# Epic 6: Admin Dashboard & Counselor Management

**Version:** 1.0  
**Date:** December 19, 2025  
**Status:** Draft

---

## Epic Goal

Create an administrative dashboard that enables authorized staff to manage counselor configurations, monitor system health, and view aggregated usage analytics without accessing individual student data. This epic delivers essential administrative capabilities for maintaining and optimizing the counseling platform while ensuring FERPA compliance.

---

## Expanded Goal

Establish a comprehensive admin interface that allows campus administrators and technical staff to configure counselor categories, update AI prompts, monitor session metrics, and troubleshoot system issues. The admin dashboard provides visibility into platform usage patterns, connection quality trends, and counselor category popularity while maintaining strict separation from student-identifiable session data. By the end of this epic, administrators can independently manage counselor configurations, respond to system alerts, and make data-driven decisions about resource allocation and platform improvements.

---

## Existing System Context

**Current Relevant Functionality:**
- 6 counselor categories (Health, Career, Academic, Financial, Social, Personal Development) with static configurations
- Student-facing authentication and session management
- Session logging with transcripts stored for 90 days
- PostgreSQL database with User, Session, and CounselorCategory tables

**Technology Stack:**
- Backend: FastAPI (Python 3.11+), SQLAlchemy async
- Frontend: Next.js 14 (App Router), React 18, TypeScript
- Database: PostgreSQL 16.1
- Authentication: JWT in httpOnly cookies

**Integration Points:**
- New admin routes will extend existing FastAPI backend
- Admin UI will be separate section within Next.js app
- Will query existing Session and CounselorCategory tables
- Requires new admin user model and permission system

---

## Enhancement Details

**What's Being Added:**

1. **Admin Authentication System**
   - Separate admin user model with role-based permissions
   - Admin login flow distinct from student authentication
   - Permission levels: Super Admin, System Monitor, Content Manager

2. **Counselor Configuration Management**
   - CRUD interface for counselor categories
   - Live editing of system prompts and descriptions
   - Enable/disable counselor categories without database access
   - Preview changes before publishing

3. **System Monitoring Dashboard**
   - Real-time session count and connection quality metrics
   - Aggregated usage statistics by counselor category
   - Error rate tracking and alert notifications
   - System health indicators (API response times, database connections)

4. **Analytics & Reporting**
   - Session volume trends over time (daily, weekly, monthly)
   - Average session duration by category
   - Connection quality distribution
   - Peak usage time analysis
   - Export reports as CSV

**How It Integrates:**
- Admin routes namespace: `/api/admin/*` with authentication middleware
- Admin UI routes: `/admin/*` with protected route guards
- Reuses existing database models, adds Admin and AuditLog tables
- Analytics queries existing Session table with aggregation only (no PII access)

**Success Criteria:**
- ✅ Admins can create/update/disable counselor categories via UI
- ✅ System prompts editable without code deployment
- ✅ Real-time session metrics visible within 30 seconds of activity
- ✅ Weekly usage reports exportable with <5 second generation time
- ✅ All admin actions logged for audit trail
- ✅ No student PII accessible through admin interface

---

## User Stories

### Story 6.1: Admin User Model and Authentication

**As a** system administrator,  
**I want** a secure admin login system separate from student authentication,  
**so that** I can access administrative functions with appropriate permissions.

**Acceptance Criteria:**

1. Admin table created in database with fields: id (UUID), email (unique), password_hash, role (enum: SUPER_ADMIN, SYSTEM_MONITOR, CONTENT_MANAGER), is_active (boolean), created_at, updated_at
2. POST /api/admin/auth/login endpoint accepts email and password, returns JWT with admin claims
3. Admin JWT tokens include role and permissions in claims, expire in 8 hours
4. Admin authentication middleware verifies JWT and checks role permissions for protected routes
5. Admins cannot access student authentication endpoints and vice versa
6. Admin login page at /admin/login with email/password form (separate from student login)
7. Initial seed script creates default super admin account with environment-configured credentials
8. Unit tests cover admin authentication, authorization, and role-based access control

---

### Story 6.2: Counselor Category Management Interface

**As a** content manager,  
**I want** to create, edit, and disable counselor categories through an admin UI,  
**so that** I can adjust available counseling options without developer assistance.

**Acceptance Criteria:**

1. GET /api/admin/counselors/categories endpoint returns all categories including disabled ones (admins only)
2. POST /api/admin/counselors/categories endpoint creates new category with validation
3. PUT /api/admin/counselors/categories/{id} endpoint updates existing category
4. DELETE /api/admin/counselors/categories/{id} soft deletes category (sets enabled=false)
5. Admin UI page at /admin/counselors displays table of all categories with edit/disable actions
6. Create/Edit modal form includes fields: name, description, icon_name, system_prompt, enabled toggle
7. System prompt field includes syntax highlighting and validation for length limits
8. Changes to enabled status immediately reflected in student dashboard (cached data refreshed)
9. Audit log entry created for every category modification with admin user ID and timestamp
10. Frontend displays success/error toast notifications for all CRUD operations

---

### Story 6.3: System Monitoring Dashboard

**As a** system monitor,  
**I want** real-time visibility into active sessions and system health metrics,  
**so that** I can quickly identify and respond to issues affecting students.

**Acceptance Criteria:**

1. GET /api/admin/metrics/current endpoint returns: active_sessions_count, avg_connection_quality, error_rate_last_hour, api_response_time_p95
2. GET /api/admin/metrics/sessions endpoint returns aggregated session counts by counselor category (no PII)
3. Admin dashboard at /admin/dashboard displays metrics in card layout with auto-refresh every 30 seconds
4. Connection quality gauge shows distribution (excellent/good/fair/poor percentages)
5. Active sessions counter updates in real-time via WebSocket or polling
6. System health indicators: green (all systems operational), yellow (degraded performance), red (critical issues)
7. Error rate chart shows trend over last 24 hours with threshold alerts
8. Database connection pool status visible (active connections, pool size, wait times)
9. External service status indicators for Daily.co, LiveKit, Beyond Presence APIs
10. Dashboard accessible by SYSTEM_MONITOR and SUPER_ADMIN roles only

---

### Story 6.4: Usage Analytics and Reporting

**As a** super admin,  
**I want** aggregated usage reports showing counseling session trends,  
**so that** I can make data-driven decisions about resource allocation and platform improvements.

**Acceptance Criteria:**

1. GET /api/admin/analytics/sessions endpoint accepts date range and returns: total_sessions, avg_duration, sessions_by_category, sessions_by_mode (voice/video), peak_usage_hours
2. Analytics page at /admin/analytics displays date range selector (preset options: last 7 days, last 30 days, custom range)
3. Bar chart visualization shows session volume by counselor category
4. Line chart shows session count trend over time (daily granularity)
5. Pie chart displays voice vs video mode distribution
6. Peak usage times heatmap shows hourly session distribution (helps identify capacity planning needs)
7. Average session duration by category displayed in table format
8. Export button generates CSV report with all aggregated metrics (no PII included)
9. CSV export completes within 5 seconds for 90-day date ranges
10. All analytics queries use database indexes and aggregation to avoid PII exposure
11. Analytics page accessible by SUPER_ADMIN role only

---

### Story 6.5: Audit Logging and Admin Activity Tracking

**As a** super admin,  
**I want** all administrative actions logged with timestamps and user identification,  
**so that** we maintain accountability and can audit system changes for compliance.

**Acceptance Criteria:**

1. AuditLog table created with fields: id (UUID), admin_user_id (FK to Admin), action (enum: CREATE, UPDATE, DELETE, LOGIN, LOGOUT), resource_type (string), resource_id (UUID nullable), details (JSON), ip_address, timestamp
2. Middleware automatically logs all admin API requests with action details
3. GET /api/admin/audit-log endpoint returns paginated audit log entries with filtering by admin user, date range, action type
4. Audit log page at /admin/audit-log displays table of all actions with columns: timestamp, admin email, action, resource, details
5. Search and filter functionality for audit log (filter by admin user, date range, action type)
6. Sensitive actions (counselor category changes, admin user creation) highlighted in UI
7. Audit log entries immutable (cannot be deleted or modified)
8. Automatic retention policy keeps audit logs for minimum 1 year (configurable)
9. Export audit log as CSV for external compliance reporting
10. Unit tests verify audit log creation for all admin actions

---

### Story 6.6: Admin Permissions and Role Management

**As a** super admin,  
**I want** to create admin accounts with specific roles and permissions,  
**so that** I can grant appropriate access levels to different team members.

**Acceptance Criteria:**

1. GET /api/admin/users endpoint returns list of all admin users (SUPER_ADMIN only)
2. POST /api/admin/users endpoint creates new admin user with email, initial password, and role (SUPER_ADMIN only)
3. PUT /api/admin/users/{id} endpoint updates admin user role or active status (SUPER_ADMIN only)
4. DELETE /api/admin/users/{id} soft deletes admin user (sets is_active=false, SUPER_ADMIN only)
5. Admin user management page at /admin/users displays table of admins with email, role, status, last login
6. Create admin form includes email validation, role dropdown, and temporary password generation
7. Password reset functionality allows admins to reset their own password
8. Super admins can force password reset for other admin users
9. Role-based access control enforced: CONTENT_MANAGER can only edit counselor categories, SYSTEM_MONITOR is read-only for metrics, SUPER_ADMIN has full access
10. Attempting unauthorized action returns 403 Forbidden with clear error message
11. Unit tests verify permission enforcement for all role combinations

---

## Compatibility Requirements

- [x] Existing student authentication APIs remain unchanged
- [x] Student-facing dashboard and session flows unaffected by admin features
- [x] Database schema changes are backward compatible (new tables added, existing tables unchanged)
- [x] Admin routes use separate namespace (`/api/admin/*`) to avoid conflicts
- [x] Performance impact minimal - admin queries do not affect student-facing endpoints
- [x] Analytics queries use read replicas or separate connection pools to avoid contention
- [x] No breaking changes to existing CounselorCategory model (only adds optional admin-visible fields)

---

## Risk Mitigation

### Primary Risks

1. **Unauthorized Access to Admin Panel**
   - **Mitigation:** Strong authentication, role-based permissions, audit logging, rate limiting on login attempts, IP whitelisting option
   - **Rollback Plan:** Disable admin routes via feature flag, revert database migrations if needed

2. **Analytics Queries Impacting Student-Facing Performance**
   - **Mitigation:** Database indexes on Session table (counselor_category, started_at, mode), query timeouts, separate connection pool for admin queries
   - **Rollback Plan:** Disable analytics endpoints if database CPU exceeds threshold

3. **Accidental PII Exposure Through Analytics**
   - **Mitigation:** Aggregation-only queries, code review checklist for PII prevention, automated tests verifying no user_id or transcript data in admin responses
   - **Rollback Plan:** Immediate takedown of affected endpoint, audit log review to identify exposed data

4. **Admin Account Compromise**
   - **Mitigation:** Strong password requirements, session timeout after 8 hours, audit logging of all actions, multi-factor authentication (future enhancement)
   - **Rollback Plan:** Immediate account deactivation, forced password reset for all admins, audit log review

---

## Definition of Done

- [x] All 6 stories completed with acceptance criteria met
- [x] Existing student authentication and session functionality verified through regression testing
- [x] Integration points (admin routes, admin UI, database) working correctly
- [x] Admin dashboard accessible and displays real-time metrics
- [x] Counselor category changes via admin UI immediately reflected in student dashboard
- [x] Analytics reports generate successfully for 90-day date ranges
- [x] Audit log captures all admin actions
- [x] Role-based access control enforced and tested
- [x] No PII accessible through admin interface (verified through automated tests)
- [x] Documentation updated: admin user guide, API documentation, database schema diagrams
- [x] Security review completed for authentication and authorization implementation
- [x] Performance testing confirms analytics queries do not degrade student-facing response times
- [x] No regression in existing features (student login, session creation, history)

---

## Dependencies

**External Dependencies:**
- None (purely internal administrative features)

**Internal Dependencies:**
- Epic 1: Foundation & Authentication (leverages existing authentication patterns)
- Epic 2: Counselor Dashboard (modifies counselor category management)
- Epic 5: Session Management & History (queries session data for analytics)

**Database Changes:**
- New tables: `admin_users`, `audit_log`
- Indexes: `sessions.counselor_category`, `sessions.started_at`, `sessions.mode`
- No changes to existing tables

---

## Testing Strategy

**Unit Tests:**
- Admin authentication and authorization logic
- Permission enforcement for role-based access control
- Counselor category CRUD operations
- Analytics aggregation queries (verify no PII leakage)
- Audit log creation for all admin actions

**Integration Tests:**
- Admin login flow end-to-end
- Counselor category changes reflected in student dashboard
- Analytics API endpoints with various date ranges
- Audit log querying and filtering
- Admin user management workflows

**Security Tests:**
- Unauthorized access attempts to admin endpoints
- SQL injection prevention in analytics queries
- XSS prevention in admin UI inputs
- CSRF token validation for admin forms
- Session hijacking prevention

**Performance Tests:**
- Analytics query execution time for 90-day ranges (<5 seconds)
- Dashboard metrics refresh time (<30 seconds)
- Impact of admin queries on student-facing API response times
- Concurrent admin users (10+ simultaneous sessions)

**Manual Testing:**
- Admin UI usability testing (create/edit counselor categories)
- Dashboard real-time updates verification
- CSV export file validation
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile responsive design for admin dashboard

---

## Timeline Estimate

**Story Duration Estimates:**
- Story 6.1 (Admin Auth): 3 days
- Story 6.2 (Category Management): 4 days
- Story 6.3 (Monitoring Dashboard): 5 days
- Story 6.4 (Analytics): 5 days
- Story 6.5 (Audit Logging): 3 days
- Story 6.6 (User Management): 4 days

**Total Estimated Duration:** 24 days (~5 weeks for 1 developer, ~2.5 weeks for 2 developers working in parallel)

**Parallelization Opportunities:**
- Stories 6.1 and 6.5 can be developed in parallel (backend focus)
- Stories 6.2 and 6.3 can be developed in parallel (frontend/backend split)
- Story 6.4 depends on 6.1 (auth required) but independent of others
- Story 6.6 depends on 6.1 (admin model) but can overlap with 6.2-6.4

---

## Success Metrics

**Functional Metrics:**
- ✅ 100% of counselor category changes via admin UI reflected in student dashboard within 5 seconds
- ✅ Analytics reports generated for 90-day ranges in <5 seconds
- ✅ 0 PII exposures through admin interface (verified through automated tests)
- ✅ 100% of admin actions logged in audit trail

**Performance Metrics:**
- ✅ Dashboard metrics refresh in <30 seconds
- ✅ Admin queries do not increase student API p95 response time by >50ms
- ✅ System supports 10+ concurrent admin users without degradation

**Security Metrics:**
- ✅ 0 unauthorized access incidents to admin panel
- ✅ 100% of security tests passing (OWASP Top 10 checks)
- ✅ Audit log retention meets compliance requirements (1+ year)

**Usability Metrics:**
- ✅ Content managers can update counselor categories without developer assistance (0 support tickets for basic changes)
- ✅ Admin onboarding time <30 minutes for new users (based on user testing)

---

## Future Enhancements (Out of Scope for This Epic)

- Multi-factor authentication (MFA) for admin accounts
- Advanced analytics: session sentiment analysis, conversation topic clustering
- Real-time alerts via email/Slack for critical system issues
- A/B testing framework for counselor prompt variations
- Admin mobile app for on-call monitoring
- Integration with campus SSO/LDAP for admin authentication
- Scheduled reports delivered via email
- Custom dashboard widgets and personalization
- Advanced RBAC with custom permission sets

---

## Stakeholder Sign-Off

**Product Owner:** _________________ Date: _________

**Technical Lead:** _________________ Date: _________

**Security Officer:** _________________ Date: _________

---

**Document Status:** Draft - Pending Review  
**Next Steps:** Review with stakeholders, prioritize stories, begin Story 6.1 development after Epic 1-5 completion
