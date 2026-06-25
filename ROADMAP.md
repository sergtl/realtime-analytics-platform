# Analytics Platform Roadmap

This roadmap is meant to be a practical product plan, not a vague wishlist.
It tracks where the project is now, what should come next, and what the later
phases likely look like across backend, frontend, SDK, data, infra, and
operations.

## 1. Current Stage

The platform is in a strong early-product phase:

- backend foundation is real
- auth and access control are real
- event ingestion exists
- query APIs exist
- the dashboard has its first usable flows
- integration tests cover the core backend behavior

The biggest gap is no longer backend capability. The biggest gap is completing
the user journey from "I created a project" to "I integrated tracking and can
trust what I see in the dashboard."

## 2. Current Capabilities

### Backend

- user registration, login, logout, `auth/me`
- session-based dashboard auth with HTTP-only cookies
- project membership and project-scoped access checks
- project creation, listing, and single-project fetch
- project event query endpoints
- metrics overview endpoint
- metrics timeseries endpoint
- project API key create/list/revoke endpoints
- `/track` event ingestion authenticated by API key
- Redis-backed worker that persists events to Postgres
- Alembic migrations and Docker-based local/test setup
- integration tests for auth, projects, metrics, API keys, ingestion, and worker

### Frontend

- auth pages
- protected dashboard app shell
- sidebar navigation
- project list page
- create-project flow
- project detail shell
- overview cards backed by real API data

### What is still missing from the product loop

- API key management UI
- first-event onboarding
- events explorer
- timeseries chart
- event type summaries
- better project settings and management
- docs/SDK that make integration fast

## 3. Product Goal

The shortest convincing loop for this product is:

1. user registers
2. user creates a project
3. user creates an API key
4. user integrates tracking
5. first event arrives
6. user sees raw events
7. user sees metrics and trends
8. user trusts the platform enough to keep using it

Everything in the roadmap should help complete or strengthen that loop.

## 4. Recommended Milestone Plan

## Milestone A: Complete the first usable dashboard

This is the highest-priority near-term milestone.

### Frontend

- API key management UI
  - list keys
  - create key
  - show raw key once
  - copy key
  - revoke key with confirmation
- project onboarding panel
  - project created
  - API key created
  - first event received
- events explorer
  - table of recent events
  - pagination/cursor support
  - basic loading and empty states
- overview improvements
  - timeseries chart
  - event types summary
  - recent activity preview
- project settings page or section
  - rename project
  - show slug/project id

### Backend

Mostly already ready, but likely additions:

- project update endpoint
- maybe project archive/delete later
- maybe richer query filters for events
- maybe recent-events summary endpoint if UI composition needs it

### Definition of done

A user can:

- create a project
- create an API key
- send events
- see those events
- see project metrics
- manage the project without touching the database or raw API manually

## Milestone B: Make analytics views feel credible

Once the first loop works, the next step is improving the quality of insight.

### Frontend

- better charting and visual hierarchy
- date range controls
- interval selectors
- event-type breakdowns
- metrics cards with clearer comparisons
- maybe "last 24h / 7d / 30d" shortcuts

### Backend

- support date-range presets and stronger filtering
- support top event types over date ranges
- support comparison windows later if useful
- evaluate if overview endpoints should become more dashboard-oriented

### Data/analytics model

- decide what your first-class product metrics are
  - total events
  - unique event types
  - maybe unique users if identity is added
  - maybe sessions if identity/session concepts are added
- define event schema expectations more clearly

### Definition of done

The dashboard starts feeling like analytics software rather than just project
administration screens.

## Milestone C: Improve onboarding and integration

Once users can create projects and inspect data, the next job is making
integration much easier.

### SDK

#### First SDK version

- JavaScript/TypeScript SDK first
- initialize with API key + base URL
- `track(eventType, payload, options?)`
- typed event envelope
- optional retry behavior
- browser-safe defaults

#### Nice follow-ups

- Node SDK support if needed
- React helper wrapper later if it truly helps
- batching if throughput starts to matter

### Dashboard + docs

- copy-paste code snippet on project page
- integration instructions after key creation
- sample event payload examples
- "send test event" flow or simple curl examples

### Backend

- consider dedicated onboarding endpoint only if useful
- consider rate-limit behavior and messaging
- consider CORS/dev ergonomics if SDK will be browser-first

### Definition of done

A new user can integrate tracking from docs + dashboard without digging through
the backend codebase.

## Milestone D: Strengthen project and team management

After the single-user / first-project flow is solid, collaboration becomes the
next natural area.

### Backend

- invite user to project
- list project members
- update membership role
- remove member

### Frontend

- members section in project settings
- invite flow
- role badges and actions

### Auth/security

- decide if email verification matters
- password reset flow
- maybe change password flow
- session management page later

### Definition of done

The product supports teams, not just a single owner acting alone.

## Milestone E: Improve platform reliability and operations

This is where the system starts becoming safer to run and easier to debug.

### Backend / worker / ingestion

- clearer idempotency guarantees
- better handling for malformed events
- dead-letter or failure path strategy
- retry policy decisions
- worker health checks

### Observability

- structured logs
- request IDs / correlation IDs across ingestion and worker
- ingestion error logging
- worker processing metrics
- queue backlog visibility

### Infra

- deployment environments
  - local
  - preview/staging
  - production
- secrets management
- production-ready Redis/Postgres setup
- backup and restore strategy
- migration rollout process

### Definition of done

You can operate the platform with confidence and debug failures without guesswork.

## Milestone F: Performance and scale

This milestone is only worth serious investment once usage justifies it.

### Backend/data

- query performance review
- indexes for event queries and aggregations
- partitioning strategy if event volume grows
- materialized summaries or rollups if needed
- batched writes and worker throughput tuning

### SDK/ingestion

- batching support
- compression if payload volume matters
- ingestion throughput monitoring

### Infra

- horizontal scaling strategy
- background worker scaling
- DB sizing and retention planning

### Definition of done

The product handles meaningfully higher event volume without the architecture
fighting you.

## Milestone G: Security and compliance hardening

This becomes more important as the product becomes public-facing.

### Security

- secure cookie settings by environment
- auth/session expiration and rotation review
- rate limiting on auth and ingestion
- audit sensitive actions
- API key naming and visibility polish
- project-level permission review

### Compliance/privacy

- decide what user/event payload rules are allowed
- define PII handling expectations
- retention rules
- deletion/export stories if needed

### Definition of done

The product has a clear security posture and fewer obvious trust gaps.

## 5. Area-by-Area Feature Backlog

## Backend

### Near term

- `PATCH /projects/{project_id}` for rename/settings
- maybe richer event filters
- maybe project summary endpoint if UI composition benefits

### Mid term

- membership management APIs
- password reset/email verification flows
- better operational endpoints or internal health surfaces

### Later

- rollups/summary tables
- retention and archival controls
- audit trails

## Frontend

### Near term

- API key management UI
- events explorer
- charted metrics
- event type summary
- onboarding checklist
- better not-found/error/loading states

### Mid term

- project settings
- project member management
- account settings
- stronger navigation/breadcrumbs

### Later

- more polished dashboard views
- saved filters/date presets
- comparison views
- maybe alerting surfaces

## SDK

### Near term

- first JS/TS SDK
- docs/examples
- browser integration story

### Mid term

- batching/retries
- framework examples
- sample app

### Later

- additional languages only if demand exists

## Infra / DevEx

### Near term

- cleaner environment docs
- staging/prod deployment plan
- consistent local bootstrap docs

### Mid term

- CI polish across web + api
- preview environment story
- secrets management

### Later

- backups
- restore drills
- capacity planning

## Testing / Quality

### Near term

- add missing single-project endpoint integration tests
- frontend test strategy for auth and projects
- lint/build/test commands documented in one place

### Mid term

- browser-level tests for core dashboard flows
- SDK integration tests

### Later

- performance/load testing for ingestion path

## 6. Suggested Order After Your Current UI Checklist

Once you finish:

- API key management UI
- onboarding
- events UI
- timeseries chart
- event types
- project settings

then I would do this next:

1. JS/TS SDK
2. integration docs + copy-paste snippets
3. project member management
4. password reset / account management
5. staging/deployment hardening
6. operational visibility for worker and ingestion
7. performance/indexing/rollups as real usage appears

That order keeps the roadmap user-centered:

- first complete the dashboard
- then make integration easy
- then make collaboration possible
- then make operations reliable
- then optimize scale

## 7. Priority Matrix

## Now

- API key management UI
- onboarding states
- events explorer
- timeseries chart
- event type summary
- project settings

## Next

- first SDK
- integration docs
- project members
- account management
- better frontend test coverage

## Later

- operational dashboards
- scale/performance work
- deeper security/compliance features
- additional SDK languages

## 8. Progress Checklist

### Core platform

- [x] session auth
- [x] API key auth for ingestion
- [x] project access control
- [x] project CRUD basics
- [x] event ingestion endpoint
- [x] worker persistence
- [x] metrics endpoints
- [x] single-project fetch

### Dashboard basics

- [x] login/register
- [x] protected app shell
- [x] project list
- [x] project creation
- [x] project detail shell
- [x] overview cards
- [ ] API key management UI
- [ ] onboarding flow
- [ ] events explorer
- [ ] timeseries chart
- [ ] event type summary
- [ ] project settings

### Integration story

- [ ] copy-paste snippet
- [ ] first SDK
- [ ] integration docs
- [ ] sample app/example

### Team/product maturity

- [ ] membership management
- [ ] account settings
- [ ] password reset
- [ ] project settings maturity

### Operations

- [ ] worker/ingestion visibility
- [ ] staging/prod deployment story
- [ ] structured logs and observability
- [ ] backup/restore plan
- [ ] scale/performance plan

## 9. Strategic Notes

- Right now the frontend is the constraint, not the backend.
- The next most valuable work is exposing existing backend capability in the UI.
- The first SDK should happen soon after the dashboard becomes usable, not far
  later.
- Avoid solving scaling problems too early; do enough to keep the path clean,
  but stay focused on the user loop first.
- If a new feature does not help users integrate, inspect, trust, or manage
  their analytics, it is probably not the highest-priority feature yet.
