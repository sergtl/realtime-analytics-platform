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

## Status

The backend currently provides authenticated project, event query, metrics, and
API key management APIs. It also includes event ingestion, Redis stream
enqueueing, worker persistence to Postgres, Alembic migrations, and
Docker-backed integration tests.

The frontend currently provides auth screens, a protected dashboard shell,
project list/create flows, project detail overview cards, and API-key
management UI.

See `ROADMAP.md` for planned next work.
