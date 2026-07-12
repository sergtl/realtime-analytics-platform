# Analytics Platform

An event analytics platform for collecting product events, storing them by
project, and exposing authenticated dashboard APIs for querying activity,
metrics, and API key management.

The repo is currently focused on the backend foundation and the first dashboard
UI: event ingestion, project-scoped API keys, user authentication, project
access control, query APIs, and integration tests.

## Project Structure

```text
apps/
  api/        FastAPI backend, worker, database models, migrations, tests
  web/        Next.js dashboard UI
```

Backend layout:

```text
apps/api/
  main.py                 FastAPI app setup, lifespan, middleware, routers
  routers/                HTTP endpoints grouped by product area
  dependencies/           Request-level auth/access dependencies
  repositories/           Database and Redis operations
  schemas/                Pydantic request/response contracts
  db/                     SQLAlchemy models and session setup
  core/                   Config, security helpers, small shared utilities
  alembic/                Database migrations
  worker.py               Redis stream consumer that persists events
  tests/integration/      Docker-backed integration tests
```

Frontend layout:

```text
apps/web/
  app/                    Next.js App Router pages and layouts
  app/(app)/              Authenticated dashboard route group
  components/             Reusable UI and form components
  hooks/                  TanStack Query hooks
  lib/api/                Plain API request functions
  proxy.ts                Optimistic route guard based on session cookie
```

## Product Architecture

The platform has three product surfaces:

- **Backend:** receives events, stores data, enforces auth/access, and exposes
  dashboard APIs.
- **Dashboard UI:** lets users register, log in, manage projects/API keys, and
  view analytics.
- **Client SDK:** future package that users install in their own product to
  send events to `POST /track`.

## Backend Architecture

The backend separates HTTP concerns from persistence:

- **Routers** define endpoint behavior, HTTP status codes, request parameters,
  and response models.
- **Dependencies** enforce cross-cutting access rules such as session auth,
  API-key auth, and project membership.
- **Repositories** perform database/Redis operations and return ORM objects,
  primitives, lists, or `None`. They do not raise `HTTPException`.
- **Schemas** define external API contracts with Pydantic.

## Event Flow

Event ingestion uses producer API keys:

1. A client sends `POST /track` with `Authorization: Bearer <api_key>`.
2. The API hashes the raw key and resolves it to a project.
3. The event is validated and pushed to Redis Streams.
4. `worker.py` consumes Redis messages and persists events to Postgres.
5. Event persistence is project-scoped and idempotent by `(project_id, event_id)`.

Dashboard query APIs use user sessions, not producer API keys.

## Auth And Access Model

There are two auth paths by design:

- **Producer auth:** API keys for event ingestion.
- **Dashboard auth:** user sessions stored in HTTP-only cookies.

Users can belong to projects through `project_memberships`. Project dashboard
routes require a valid session plus membership. Sensitive operations, such as
creating or revoking project API keys, require an owner/admin membership.

Session tokens and API keys are only stored as hashes in the database. Raw API
keys are returned once when created.

The dashboard frontend uses an optimistic Next.js `proxy.ts` guard for page
navigation, but the FastAPI backend remains the source of truth for session and
project authorization.

## Main API Areas

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `POST /track`
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}/events`
- `GET /projects/{project_id}/event-types`
- `GET /projects/{project_id}/metrics/overview`
- `GET /projects/{project_id}/metrics/timeseries`
- `GET /projects/{project_id}/api-keys`
- `POST /projects/{project_id}/api-keys`
- `POST /projects/{project_id}/api-keys/{api_key_id}/revoke`

## Development

Start backend dependencies:

```bash
cd apps/api
docker compose up -d
```

Run the API:

```bash
pnpm dev:api
```

Run the web app:

```bash
pnpm dev:web
```

Run tests:

```bash
pnpm test:api:unit
pnpm test:api:integration
pnpm test:api
```

Run backend linting:

```bash
cd apps/api
uv run ruff check .
```

## Testing

Integration tests use `apps/api/docker-compose.test.yml` to start isolated
Postgres and Redis containers, apply Alembic migrations, run tests, and clean up
volumes.

The integration suite covers:

- auth registration, login, session lookup, logout
- project creation/listing/access control
- event query and metric endpoints
- API key creation/listing/revocation
- `/track` ingestion and Redis enqueueing
- worker persistence and idempotency

## Current Status

Done:

- [x] User registration, login, logout, and session lookup
- [x] Session-cookie dashboard auth
- [x] Project creation and project listing
- [x] Project membership access checks
- [x] Project API key create/list/revoke APIs
- [x] API-key UI for list/create/copy/revoke
- [x] `POST /track` event ingestion
- [x] Redis stream enqueueing
- [x] Worker persistence to Postgres
- [x] Idempotent event storage by `(project_id, event_id)`
- [x] Event query API
- [x] Event type summary API
- [x] Metrics overview API
- [x] Metrics timeseries API
- [x] Alembic migrations
- [x] Docker-backed API integration tests
- [x] API and web CI workflows

Not done:

- [ ] Events explorer UI
- [ ] Timeseries chart UI
- [ ] Event type summary UI
- [ ] First-event onboarding
- [ ] Client SDK
- [ ] Production Dockerfiles
- [ ] Staging/production deployment config
- [ ] Worker failure handling and dead-letter strategy
- [ ] Rate limiting
- [ ] Team/member management

## Product Goal

Target user flow:

- [ ] User registers
- [ ] User creates a project
- [ ] User creates an API key
- [ ] User sends the first event
- [ ] User sees raw events
- [ ] User sees charts and event summaries
- [ ] User can manage project settings

## Roadmap

### 1. Dashboard

- [ ] Build events explorer table
- [ ] Add event cursor pagination
- [ ] Add event date range filter
- [ ] Add event type filter
- [ ] Add expandable JSON payload view
- [ ] Add events loading state
- [ ] Add events empty state
- [ ] Add events error state
- [ ] Add timeseries chart to project overview
- [ ] Add top event types to project overview
- [ ] Add recent activity preview
- [ ] Add date presets: `24h`, `7d`, `30d`
- [ ] Add custom date range controls
- [ ] Add first-event onboarding checklist
- [ ] Add curl integration snippet
- [ ] Add JavaScript integration snippet

### 2. Backend

- [ ] Add `event_type` filter to `GET /projects/{project_id}/events`
- [ ] Add improved pagination metadata to event pages
- [ ] Add default dashboard date range behavior
- [ ] Add project rename endpoint
- [ ] Add project settings schema
- [ ] Add dashboard aggregation endpoint if frontend request count becomes high
- [ ] Add top event types over selected date range if current endpoint is not enough
- [ ] Add payload field filtering
- [ ] Add comparison-window metrics

### 3. SDK And Docs

- [ ] Add TypeScript SDK package
- [ ] Add SDK `init({ apiKey, baseUrl })`
- [ ] Add SDK `track(eventType, payload, options?)`
- [ ] Generate event IDs by default
- [ ] Generate timestamps by default
- [ ] Generate correlation IDs by default
- [ ] Add retry behavior for transient failures
- [ ] Add browser-safe defaults
- [ ] Add SDK README
- [ ] Add event schema documentation
- [ ] Add API key handling guidance
- [ ] Add sample event payloads

### 4. Ingestion And Worker Reliability

- [ ] Enforce max request body size
- [ ] Add API-key or project-level rate limits
- [ ] Add structured API logs
- [ ] Add structured worker logs
- [ ] Prevent worker crash on one failed message
- [ ] Add retry/backoff policy
- [ ] Add dead-letter stream or failure table
- [ ] Add worker health signal
- [ ] Add Redis stream backlog metric
- [ ] Add worker processed/failed message metrics

### 5. Infrastructure

- [ ] Add API Dockerfile
- [ ] Add worker Dockerfile
- [ ] Define local environment config
- [ ] Define staging environment config
- [ ] Define production environment config
- [ ] Document required environment variables
- [ ] Document secret management approach
- [ ] Add migration rollout process
- [ ] Add Postgres backup/restore plan
- [ ] Add API error monitoring
- [ ] Add worker failure monitoring
- [ ] Add Redis backlog monitoring
- [ ] Add database latency monitoring
- [ ] Add web `typecheck` script
- [ ] Add web typecheck to CI
- [ ] Add migration check to CI
- [ ] Add staging deploy workflow

### 6. Project And Team Management

- [ ] Add project settings page
- [ ] Add project rename UI
- [ ] Add project archive/delete support
- [ ] Add member invite API
- [ ] Add member list API
- [ ] Add member role update API
- [ ] Add member removal API
- [ ] Add members settings UI
- [ ] Add password reset
- [ ] Add change password
- [ ] Add session management UI
