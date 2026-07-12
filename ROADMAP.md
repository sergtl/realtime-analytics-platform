# Analytics Platform Roadmap

## Current Status

Done:

- [x] User registration, login, logout, and session lookup
- [x] Session-cookie dashboard auth
- [x] Project creation and project listing
- [x] Single-project fetch
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

## Next Build Order

- [ ] Build events explorer UI using `GET /projects/{project_id}/events`
- [ ] Add timeseries chart using `GET /projects/{project_id}/metrics/timeseries`
- [ ] Add event type summary using `GET /projects/{project_id}/event-types`
- [ ] Add first-event onboarding panel
- [ ] Add backend event filters, starting with `event_type`
- [ ] Add TypeScript SDK package
- [ ] Add worker logging, retry behavior, and dead-letter handling
- [ ] Add project settings and rename support
- [ ] Add production Dockerfiles and staging deployment
- [ ] Add rate limiting and ingestion abuse protection
- [ ] Add team/member management

## Dashboard

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

## Backend

- [ ] Add `event_type` filter to `GET /projects/{project_id}/events`
- [ ] Add improved pagination metadata to event pages
- [ ] Add default dashboard date range behavior
- [ ] Add project rename endpoint
- [ ] Add project settings schema
- [ ] Add dashboard aggregation endpoint if frontend request count becomes high
- [ ] Add top event types over selected date range if current endpoint is not enough
- [ ] Add payload field filtering
- [ ] Add comparison-window metrics

## SDK And Docs

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

## Ingestion And Worker Reliability

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

## Infrastructure

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

## Project And Team Management

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
