# Android Migration — Epic and Task Breakdown

Tasks are ordered by dependency. Convert active tasks into focused GitHub Issues. Every issue must identify source evidence, scope, non-goals, acceptance criteria, tests, dependencies and doc updates.

## EPIC A — Source audit and specification (P0)

### A0-01 — Source inventory and traceability
Inventory Swift targets/files/public types/screens/routes/resources/tests/entitlements/build settings; inventory Go monitor routes/DTOs/state/persistence/tests. Record exact source SHA. **Accept:** every user-visible feature and major subsystem maps to Android owner, source evidence, tests and target tasks; unknowns explicit.

### A0-02 — CPA API and quota contracts
Trace endpoints, auth, DTOs, account identity, windows/metrics/credits, errors, cooldown, retry and cancellation. **Accept:** verified route/method/auth/DTO/error matrix and fixtures for null/time/unit/cache/freshness semantics.

### A0-03 — CAP plugin contract
Trace routes, capability detection, auth modes, statistics windows and failure cases. **Accept:** anonymous vs management auth, plugin unavailable vs zero, supported stats fixture coverage.

### A0-04 — AI chat behavior
Trace model discovery, request format, SSE events, prompt assembly, reasoning policy, tools, memory, skills, persistence, search providers and background continuation. **Accept:** complete behavior inventory and testable streaming/persistence contract.

### A0-05 — Monitor service contract
Trace Go handlers, DTOs, auth, UUID/revision/sequence/lease/tombstone/detached session, persistence migration and retry. **Accept:** route matrix and lifecycle transition model backed by Go tests/fixtures; no server protocol change needed for Android.

### A0-06 — UX and accessibility inventory
Capture every screen, navigation path, action, empty/loading/error/stale state, copy, localization and accessibility identifier. **Accept:** screen/interaction matrix with Android adaptation and parity status.

### A0-07 — Security/privacy threat model
Inventory secrets, storage, transport, logs, backup, deep links, exported components, notifications, providers and retention. **Accept:** threat model and release checks approved.

## EPIC B — Architecture and foundation (P1)

### B1-01 — Architecture ADRs
Cover module boundaries, min/target SDK, DI, network stack, database, secure storage, background policy and navigation. **Accept:** reviewed decisions and consequences recorded.

### B1-02 — Reproducible Gradle project
Initialize Kotlin/Compose/Gradle Kotlin DSL/version catalog and minimal app. **Accept:** clean clone assembles debug; toolchain/dependencies centrally pinned; no local paths/secrets.

### B1-03 — CI quality gates
Compile, lint, static analysis, unit/contract tests, secret scan and release assembly. **Accept:** required checks run on PR and fail closed.

### B1-04 — Core primitives
Clock, dispatcher provider, typed result/error, safe logger, fixture/test utilities. **Accept:** deterministic tests; no Android dependency in domain primitives.

### B1-05 — Design system/navigation shell
Material 3 theme, adaptive layout, navigation, accessibility semantics and common states. **Accept:** app launches and navigates without mock data presented as production.

## EPIC C — Connections and CPA quota core (P2)

### C2-01 — Server address validation
**Accept:** HTTPS-only; reject userinfo/query/fragment/traversal/encoded separators; preserve valid proxy prefix per source.

### C2-02 — Secure credential lifecycle
**Accept:** management/inference keys distinct; Keystore-backed encryption; no plaintext fallback; save only after validation; replacement/deletion tests.

### C2-03 — CPA API and DTOs
**Accept:** all verified routes, headers, body limits, timeout, redirect policy and serialization tested.

### C2-04 — Connection validation and account discovery
**Accept:** multiple connections; server-scoped account IDs; management auth failure separated from account errors/capability warnings.

### C2-05 — Quota models and normalization
**Accept:** nullable/unknown, units, currency, windows, >100%, timestamps and passive/live provenance match source.

### C2-06 — Quota refresh coordinator
**Accept:** bounded concurrency, same-account coalescing, cancellation, cooldown and stale-response rejection proven with race tests.

### C2-07 — Cache and error retention
**Accept:** last success retained on failure; cache not reported as new success; persistence matches audited source contract.

### C2-08 — Account and quota UI
**Accept:** account list/detail, multiple windows, metrics, credits, freshness, per-account errors and manual refresh tested with fixtures and authorized service.

## EPIC D — Product UI/settings (P3)

### D3-01 — Dashboard/navigation: complete primary journeys; no mock production data.
### D3-02 — Connection UI: add/validate/switch/edit/forget; secrets never leak into UI state/logs.
### D3-03 — Settings/diagnostics: preferences, capability warnings and actionable safe diagnostics.
### D3-04 — Accessibility/localization/adaptive layouts: TalkBack, font scaling, contrast, touch targets, landscape/tablet/foldable and locales.

## EPIC E — CAP usage (P4)

### E4-01 — Capability discovery/client: read-only verified routes, explicit auth, no silent escalation.
### E4-02 — Statistics/domain/charts: correct windows/units/aggregation; empty, zero and unavailable distinct.
### E4-03 — Diagnostics: plugin missing, route unavailable, unauthorized and malformed response safely distinguished.

## EPIC F — AI workspace (P5)

### F5-01 — Model catalog/provider settings: model discovery, selection, auth separation.
### F5-02 — SSE parser: incremental UTF-8/frame parsing, partial chunks, terminal/malformed events and cancellation.
### F5-03 — Chat engine/prompt assembly: message/tool/reasoning semantics traced; tools bounded and permissioned.
### F5-04 — Conversation persistence: Room schema, transactions, ordering, partial generation recovery, deletion/migrations.
### F5-05 — Markdown rendering: streaming partial Markdown, code, tables and unsafe HTML handling.
### F5-06 — Memory/skills: source-compatible CRUD/import/export; untrusted content cannot override app security.
### F5-07 — Search providers: separate protected keys, consent, errors and source attribution.
### F5-08 — Background continuation: Android constraints, interruption/recovery/notification permission; no indefinite execution promise.

## EPIC G — Monitoring (P6)

### G6-01 — Bridge auth/capabilities: token isolated, schema and authorization verified.
### G6-02 — Session lifecycle: create/get/refresh/rotate/stop obey UUID/revision/sequence/lease contracts.
### G6-03 — Uncertain outcome: same-UUID reconciliation; 202/204 not overstated; tombstones prevent stale reactivation.
### G6-04 — Persistence/recovery: reconcile after process/reboot; secrets protected.
### G6-05 — Android notifications: separate notification state from service and delivery state.

## EPIC H — Android platform (P7)

### H7-01 — Widget data/privacy contract: snapshot, account selection, freshness, privacy and deep links.
### H7-02 — Glance/App Widget: sizes, configuration, refresh, process recreation and API coverage.
### H7-03 — Background scheduling: WorkManager uniqueness, constraints, cancellation, reboot; no high-frequency polling.
### H7-04 — Lifecycle hardening: Doze, standby, force-stop, process death, permission revocation and OEM behavior.

## EPIC I — Quality/release (P8)

### I8-01 — Cross-platform contract regression: Android fixtures with provenance/source SHA.
### I8-02 — Performance/battery: cold start, memory, scrolling, charts, SSE and background profiling.
### I8-03 — Security/privacy audit: secrets, dependencies, Keystore/backup, exported components, network and logs.
### I8-04 — Device/accessibility matrix: supported APIs, low-memory device, multiple OEMs, TalkBack, tablet/foldable.
### I8-05 — Signed release: reproducible AAB, versioning, privacy disclosures, release notes and rollback.

## Dependency graph

A0-01 enables A0-02..07. Gate A enables B1-01..05. B enables C2-01..08. C enables D3 and E4; F5 and G6 can proceed when their audited contracts and foundation are ready. G6/H7 depend on platform/background decisions. All feed I8.

## Parallelization

Safe after audit: UX inventory, CPA contract extraction, Go monitor contract extraction, chat/SSE audit and CI foundation. Do not parallel-edit shared models, credentials, connection identity, error/cooldown coordinator, monitor state machine or root Gradle configuration. One owner per shared contract.

## Issue status

Use phase labels, area labels, type labels, blocked and needs-decision. Never close based on code-only completion. Require exact PR SHA, tests, source evidence and parity update.
