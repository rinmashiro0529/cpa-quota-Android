# Complete iOS → Android Migration Plan

## 1. Strategy

Audit all source areas first, then deliver in vertical, testable slices. Do not build every screen first and connect data later. Do not translate Swift line-by-line. Preserve product behavior and contracts while adopting Android-native APIs.

Reference: rinmashiro0529/cpa-quota-ios. Target: this repository. Scope: every user-facing iOS capability, with honest Android equivalents where OS APIs differ.

## 2. Workstreams

| Workstream | Output |
|---|---|
| A. Source audit/product spec | Traceability matrix and verified contracts |
| B. Foundation/architecture | Buildable modular app and CI |
| C. CPA core | Connections, accounts, quota, refresh |
| D. Product UI | Dashboard, accounts, quota, settings |
| E. CAP | Plugin capability, stats and diagnostics |
| F. AI workspace | Models, streaming chat, persistence, memory, skills, search |
| G. Monitoring | Go service client and lifecycle reconciliation |
| H. Android platform | Widgets, notifications, background/lifecycle |
| I. Quality/release | Device matrix, security, performance, signed release |

## 3. Phases and exit gates

### Phase 0 — Source audit (Gate 0)
Inventory all Swift targets/files/public types/tests/resources/entitlements/navigation/build settings; Go routes/DTOs/persistence versions/state transitions/fixtures/security; all endpoints/auth/DTO/errors/cooldowns; screen states/actions; storage and secret lifecycle; third-party licenses and Android replacements. Map every iOS test/fixture to Android tests.
**Exit:** exact source SHA recorded; feature traceability matrix complete; contracts and risks documented; critical unknowns resolved or explicitly blocked.

### Phase 1 — Architecture and foundation (Gate 1)
Approve ADRs for module graph, min/target SDK, DI, network, persistence, secure store, background policy and UI. Initialize Gradle Kotlin DSL, version catalog, Kotlin/Compose, core modules and CI. Add startup, navigation, design tokens, error/result primitives, clock/dispatcher and fixtures.
**Exit:** clean clone builds and launches; CI passes; architecture boundaries tested; no mock production behavior.

### Phase 2 — CPA connection and quota core (Gate 2)
Implement server URL validation; secure credential types/store; connection lifecycle; account discovery; quota DTO/domain mapping; refresh coordinator; concurrency/coalescing/cancellation/cooldown; typed errors; last-success retention.
**Exit:** fixtures and authorized integration tests pass; security review passes.

### Phase 3 — Core product experience (Gate 3)
Dashboard, account list/detail, quota windows, loading/refresh/empty/stale/error/partial states, manual refresh, settings, connection management, accessibility, localization, adaptive layouts.
**Exit:** core journeys pass Compose/device tests and parity matrix contains evidence.

### Phase 4 — CAP integration (Gate 4)
Capability discovery, explicit auth, read-only stats, windows/aggregation/charts/diagnostics and plugin unavailable/empty/zero distinctions.
**Exit:** fixture and authorized integration tests pass; no privileged fallback.

### Phase 5 — AI workspace (Gate 5)
Model catalog, OpenAI-compatible request/response, robust SSE, cancellation, ChatEngine/prompt/tool behavior, Markdown, Room persistence, memory, skills, search provider keys, bounded background continuation and notifications.
**Exit:** streaming, reconnect, process-death, persistence migration and security tests pass.

### Phase 6 — Monitor integration (Gate 6)
Monitor capabilities/auth, session CRUD/refresh/rotate/stop, UUID/revision/sequence/lease/tombstone/detached state machine, uncertain outcome reconciliation, Android notification/background policy.
**Exit:** Go contract fixtures and lifecycle/race tests pass; no unsubstantiated delivery claims.

### Phase 7 — Android platform features (Gate 7)
Glance/App Widget, configuration, snapshot/privacy/freshness, manual action, notification channels/permission/deep links, WorkManager scheduling, reboot recovery and justified foreground service.
**Exit:** supported API/OEM matrix validated; limitations documented.

### Phase 8 — Hardening and release (Gate 8)
Regression, performance/memory/battery profiling, accessibility/localization, security/dependency/backup audit, signed release build, metadata/privacy disclosures, rollback plan and crash diagnostics.
**Exit:** exact release-candidate SHA passes all gates; evidence and known limitations published.

## 4. Parallelization

After Gate 0, safe parallel audit work includes UX inventory, CPA contract extraction, Go monitor contract extraction, chat/SSE audit and CI foundation. Do not parallel-edit shared domain models, credentials, connection identity, error/cooldown coordinator, monitor state machine or root Gradle configuration. Assign one owner per shared contract.

## 5. Milestones

- M0 Audit baseline: source and requirements signed off.
- M1 Core Preview: CPA connection, accounts, quota, diagnostics and settings.
- M2 Feature Complete Beta: CAP, AI and monitoring integrated.
- M3 Platform Complete RC: widgets, notifications, lifecycle, accessibility and hardening.
- M4 1.0: release gates and operational readiness complete.

Dates are not committed until source audit and team capacity are known. Estimate individual tasks only after dependencies and test scope are verified.

## 6. Risk register

| Risk | Mitigation |
|---|---|
| Incomplete source audit | File/test/route traceability and Gate 0 |
| API drift | Fixtures, explicit contracts and integration tests |
| Wrong null/time/unit semantics | Typed values and adversarial fixtures |
| Management-key lockout | Connection circuit breaker and cooldown |
| Secret leakage | Keystore, redaction, scans and backup exclusions |
| Android background limits | WorkManager/foreground policy and honest UX |
| Monitor races | Server-authoritative UUID reconciliation |
| SSE chunk assumptions | Incremental parser boundary tests |
| Dependency churn | Central version catalog and reproducible builds |
| Agent overreach | Constitution, AGENTS, ADRs, small PRs |
| False completion claims | Evidence-based DoD on exact SHA |

## 7. Progress reporting

Every milestone report includes exact commit SHA/PR, completed acceptance criteria, commands/results, device/API environment, failures/retries, remaining risks/blocked dependencies and parity updates. A compiling app or screenshot alone is not completion.
