# StockSteward AI Refactor Backlog

## Objective
Stabilize and productionize the platform for Indian trading workflows by consolidating duplicate runtime paths, enforcing security/compliance controls, and improving maintainability.

## Current Problems
- Multiple overlapping trading stacks (`agents`, `services`, `engines`) with duplicated logic.
- Unsafe defaults in auth/trade paths (implicit identities, broad CORS, demo auth behavior in runtime).
- Overloaded modules (`backend/app/main.py`, `frontend/src/services/api.js`).
- Mixed concerns in endpoints (seed/demo logic mixed with production paths).
- Inconsistent domain boundaries across backend and frontend.

## Refactor Principles
- Single source of truth per domain.
- Fail-safe behavior for identity, pricing, risk, and execution.
- Security-by-default for PROD.
- Modular monolith first, microservices only after boundary maturity.
- Test-driven migration with compatibility shims during cutover.

## Program Plan (12 Weeks)

### Sprint 1-2: Safety and Runtime Hardening
- [x] Remove implicit trade identity fallback in trade orchestration.
- [x] Enforce authenticated user on trade execution endpoints.
- [x] Remove mock execution price injection in trade endpoints.
- [x] Gate demo auto-provision login by explicit config.
- [x] Restrict CORS defaults from wildcard to explicit origins.
- [x] Disable silent dev-user fallback by default.
- [x] Remove paper execution fallback to `portfolio_id=1`.
- [x] Fix paper broker state methods to use DB-backed positions/PnL.
- [x] Replace plaintext default secret in environment templates and deployment configs.
- [x] Add startup guardrails for `CORS_ORIGINS=*` in PROD.
- [x] Add endpoint-level rate limits on auth and trade execution.
- [x] Add idempotency keys for order submission APIs.

Acceptance Criteria
- No execution path can proceed without authenticated `user_id`.
- No default trade price is auto-injected.
- PROD boot fails on invalid security settings.

### Sprint 3-4: Trading Core Consolidation
- [x] Define initial canonical trading application service (`TradeApplicationService`) for execute/list/daily-pnl.
- [x] Extend canonical service with:
  - [x] `TradeApplicationService.submit_order()`
  - [x] `TradeApplicationService.approve_order()`
  - [x] `TradeApplicationService.cancel_order()`
- [ ] Introduce canonical domain modules:
  - `app/domain/orders`
  - `app/domain/risk`
  - `app/domain/portfolio`
  - `app/domain/approvals`
  - `app/domain/execution`
- [ ] Convert `OrchestratorAgent` into an orchestration facade over domain services.
- [ ] Remove duplicate execution logic from `app/execution/engine.py` vs `app/engines/execution_engine.py`.
- [ ] Select one risk engine path; move other to deprecated.
- [x] Add migration adapters for old endpoints to call new service.
- [x] Add explicit order state transitions in application service and trade events (full DB-native state machine still pending).

Acceptance Criteria
- All trade endpoints use one service and one state machine.
- Legacy engines are not directly called by API runtime.

### Sprint 5-6: Data and Integration Layer Cleanup
- [x] Create `MarketDataProvider` interface and provider implementations:
  - [x] Yahoo
  - [x] Zerodha/Kite (placeholder adapter)
  - [x] TrueData (placeholder adapter)
- [ ] Centralize ticker normalization and symbol mapping.
- [ ] Build market data cache module with TTL and circuit breaker.
- [x] Move websocket feed logic out of `main.py` into `app/realtime` module.
- [ ] Add graceful degradation policy and provider health metrics.
- [ ] Remove dead providers and docs mismatch.

Acceptance Criteria
- One market data abstraction consumed by strategy/risk/execution.
- `main.py` reduced to app wiring and middleware only.

### Sprint 7-8: Auth/RBAC/KYC and Audit Compliance
- [x] Replace header-based identity (`X-User-Id`) for protected endpoints with JWT principal extraction (production enforced).
- [x] Keep `X-User-*` only for local test mode behind config flag.
- [x] Add permission matrix by role and endpoint.
- [ ] Standardize audit logging schema for:
  - order intent
  - risk decision
  - approval action
  - broker submission result
- [x] Add immutable event log table (`trade_events`).
- [x] Add KYC enforcement checkpoint before live-trading route.

Acceptance Criteria
- Production APIs rely on signed token identity only.
- Full order event history reconstructable from audit tables.

### Sprint 9-10: Frontend Domain Refactor
- [x] Start split of `frontend/src/services/api.js` into domain clients:
  - [x] `services/authApi.js`
  - [x] `services/tradesApi.js`
  - [x] `services/portfolioApi.js`
  - [x] `services/adminApi.js`
  - [x] `services/marketApi.js`
- [x] Add shared HTTP client module (timeout + auth header merge + socket bootstrap).
- [x] Add retry policy for transient HTTP/network failures to shared HTTP client.
- [ ] Add typed request/response contracts (TypeScript migration target).
- [ ] Introduce React Query (or equivalent) for caching and polling.
- [ ] Isolate websocket client and room subscriptions in `services/realtime`.
- [ ] Move route-level auth guards into reusable wrappers.

Acceptance Criteria
- No single frontend service file >250 lines.
- Query and mutation flows are domain-scoped and testable.

### Sprint 11-12: Test/Observability/Release Hardening
- [ ] Rationalize tests:
  - `tests/unit`
  - `tests/integration`
  - `tests/e2e`
  - archive experimental scripts
- [ ] Replace ad hoc scripts under `Testing Scripts/` with repeatable pytest/cypress jobs.
- [ ] Add contract tests for broker adapters and risk veto rules.
- [ ] Add SLO dashboards:
  - order submit latency
  - risk decision latency
  - execution success ratio
  - websocket feed freshness
- [ ] Add structured logs with `trace_id` across request lifecycle.
- [x] Add CI gates for lint/test/security scan in pipeline.

Acceptance Criteria
- CI produces deterministic quality gates.
- Runtime has traceable observability for core trading path.

## Target Backend Layout (Modular Monolith)

```text
backend/app/
  api/
    v1/
      endpoints/
  application/
    trading_service.py
    approval_service.py
    portfolio_service.py
  domain/
    orders/
    risk/
    execution/
    portfolio/
    approvals/
    market_data/
  infrastructure/
    db/
    brokers/
    market_data/
    messaging/
  realtime/
    socket_server.py
    market_feed.py
  observability/
  core/
```

## Target Frontend Layout

```text
frontend/src/
  app/
    routes/
    providers/
  features/
    trading/
    portfolio/
    reports/
    admin/
  services/
    http/
    realtime/
    authApi.js
    tradesApi.js
    portfolioApi.js
    marketApi.js
  shared/
    ui/
    utils/
```

## Deprecation Candidates
- `backend/app/engines/*` (retain only if wired to production path after consolidation review).
- `backend/app/execution/engine.py` if duplicate with selected canonical execution implementation.
- demo/seed endpoints from production API namespace.
- direct fallback behaviors that impersonate users or inject prices.

## Migration Strategy
- Step 1: Introduce new application service layer behind existing endpoints.
- Step 2: Route selected endpoints to new layer with feature flags.
- Step 3: Run shadow mode comparisons (old vs new decision outputs).
- Step 4: Cut over and remove old runtime paths.
- Step 5: Archive deprecated modules and update docs/tests.

## Risks
- Hidden coupling between agent outputs and UI assumptions.
- Legacy tests built on demo fallback behavior may fail.
- Environment misconfiguration during security tightening.

## Immediate Next Tasks
1. Convert placeholder market providers (Kite/TrueData) into active provider integrations.
2. Rationalize tests into `tests/unit`, `tests/integration`, and `tests/e2e`.
3. Consolidate duplicate runtime engines (`app/engines` vs active orchestration path).
4. Add typed frontend contracts and query-layer standardization.
