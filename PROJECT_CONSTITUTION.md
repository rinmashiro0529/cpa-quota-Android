# CPA Quota Android — Project Constitution

**Status:** Approved planning baseline; implementation details require source-audit validation.  
**Goal:** Complete functional migration of CPA Quota iOS into a first-class native Android application.  
**Reference:** https://github.com/rinmashiro0529/cpa-quota-ios

## 1. Product intent

CPA Quota is a read-only client for authorized CPA services. It lets users inspect existing accounts and quota windows, understand CAP token usage, converse with available models, manage connections, and optionally use an independent monitoring service. It does not perform upstream OAuth login or mutate upstream accounts, quotas or server configuration.

Android is not a reduced companion or prototype. All iOS user-facing capabilities are in scope. Preserve business behavior, data semantics, protocol contracts and security boundaries while adapting UX and system integration to Android. Pixel-identical UI is not required.

## 2. Non-negotiable principles

1. Native Android: Kotlin and Jetpack Compose. No Flutter, React Native, WebView-hosted app or cross-platform UI framework as the core product.
2. Behavior before visual imitation: preserve capabilities, business semantics, protocol contracts, failure behavior and security boundaries.
3. Source-derived truth: audit iOS source, tests, fixtures, Go service source and contracts. README prose alone is insufficient.
4. No invented contracts: never guess endpoints, DTOs, auth, units, time semantics, retries or state transitions. Mark unknowns and block dependent work.
5. No backend duplication: reuse the existing independent Go monitoring service. Android is a new client, not a reason to fork it.
6. Security by design: never store secrets in plaintext or log them. Fail closed; no silent security downgrade.
7. Explicit state semantics: unknown is not zero; stale is not fresh; cache is not a new success; server acceptance is not device delivery; cancellation intent is not confirmed termination.
8. Structured concurrency: bounded, owned and cancellable work. No unmanaged scopes, hidden infinite retries or unbounded concurrency.
9. Testable architecture: domain rules must be testable without Android UI or live services.
10. Evidence-based completion: exact candidate SHA, acceptance criteria and required tests must pass.
11. Small reversible changes: focused PRs; consequential choices require ADRs.
12. No false parity claims: map iOS-only features to honest Android equivalents and document OS limitations.

## 3. Complete feature scope

- CPA connections, HTTPS validation, multiple servers, credential lifecycle and account discovery.
- Quota snapshots, windows, metrics, credits, reset times, freshness, passive/live provenance, cache, refresh, cancellation and error isolation.
- CAP Token Usage Tracker integration, capability discovery, explicit auth modes, read-only statistics and diagnostics.
- AI model discovery, OpenAI-compatible chat completions, SSE streaming, cancellation, Markdown, conversations, persistence, memory, skills and optional search providers.
- Independent monitor bridge, capabilities, authorization, sessions, UUID/revision/sequence, snapshots, leases, cancellation tombstones and reconciliation.
- Android-native widgets, notifications, background work and lifecycle recovery.
- Settings, diagnostics, onboarding, localization, accessibility, privacy, build, signing and release.

The source audit may discover additional product capabilities; they remain in scope unless the product owner explicitly approves an exclusion.

## 4. Platform mapping

- SwiftUI → Jetpack Compose.
- Swift concurrency/actors → Kotlin Coroutines, Flow and explicit synchronization.
- Keychain → Android Keystore-backed encrypted credential storage.
- UserDefaults → DataStore for non-secret preferences.
- Codable → explicit Kotlin wire DTOs and domain models.
- WidgetKit → Android App Widgets / Glance.
- ActivityKit → Android-appropriate notification/system surfaces; no claim of equivalence.
- APNs → FCM only if an approved Android push contract requires it; never reuse APNs tokens/protocol.
- BackgroundTasks → WorkManager for deferrable work; foreground service only for eligible user-visible ongoing work.
- Existing Go monitor backend remains shared and server-authoritative.

## 5. Critical business invariants

### Quota and freshness
- Preserve nullable values. Missing is unknown, never zero, unlimited or exhausted.
- Preserve actual usage above 100%; clamp only presentation-specific remaining values where source contract requires it.
- Preserve units, currency, duration and window identity.
- Preserve passive/live provenance and fetched/observed timestamps separately.
- Passive data without observed time has unknown/stale freshness; never fabricate observed time from list refresh time.
- Failed refresh retains last successful snapshot and exposes failure separately.
- Cache hits are not new live successes.

### CPA connection and authentication
- HTTPS-only; reject unsafe URL components according to source contract; preserve valid reverse-proxy prefixes.
- Management key and inference/client API key are distinct credential types.
- Save credentials only after successful validation and only in protected storage.
- Management 401/403 is connection-level protection and blocks repeated management requests.
- Upstream account 401 is account-scoped; it must not delete management credentials or invalidate other accounts.
- Management 429 honors Retry-After; force/list reload/cache cannot bypass cooldown.
- Changed management credential creates a new connection/client/store context.

### Concurrency and cancellation
- Bound management reads to the source-defined maximum (currently documented as three).
- Coalesce same-account in-flight requests where the source contract requires.
- One account failure must not fail unrelated accounts.
- Cancellation is not quota exhaustion or connection failure.
- Late responses cannot overwrite newer state or another connection/session.
- No default automatic retry unless the source explicitly defines it.

### CAP
- CAP usage is supplied by the external cap-token-usage-tracker plugin; the app does not independently collect those tokens.
- Plugin missing/unavailable is not zero usage.
- Anonymous and management-key auth modes are explicit; never silently fall back to privileged auth.
- Never access or decrypt upstream users' raw API keys.

### Monitor
- Reuse the existing Go service and versioned contracts.
- Keep Monitor Bridge Token separate from CPA management and inference keys.
- Preserve UUID, revision, sequence, lease, tombstone and detached-session semantics.
- Reconcile uncertain outcomes with the same UUID; never blindly create a second session.
- HTTP 202 is pending, not completed collection or delivered push. HTTP 204 cancellation acceptance is not proof a device UI disappeared.
- APNs state is iOS-specific; Android push receipt and notification display must be modelled separately.

### AI chat
- Preserve OpenAI-compatible request/response and SSE semantics from source.
- Handle partial frames, UTF-8 boundaries, terminal events, malformed events, cancellation and process death.
- Preserve local conversation, memory and skills semantics.
- Provider keys are separately scoped and protected.

## 6. Architecture direction

Use feature-oriented Gradle modules with Clean Architecture:
- Presentation: Compose screens, ViewModels, UI state and navigation.
- Domain: platform-independent entities, value objects, repository contracts and use cases.
- Data: repositories, DTOs, mappers, persistence and source orchestration.
- Infrastructure/platform: HTTP, database, secure storage, widgets, notifications and background execution.

Dependencies point inward. Domain MUST NOT depend on Android, Compose, Retrofit, Room or DI types. See docs/ARCHITECTURE.md.

## 7. Quality gates

Every feature PR requires source traceability, domain tests, contract/fixture tests, cancellation/error tests where applicable, critical UI tests, security review, updated docs and passing CI on exact PR head. Release requires real-device, signed build, accessibility, performance, lifecycle, migration and security evidence.

## 8. Decision authority

This constitution is the product and engineering direction. Agents may propose changes but must not silently weaken scope, invariants, security or acceptance criteria.

Changes to architecture, persistence, auth, retries/cooldown, monitor protocol, background model, min SDK or major dependencies require an ADR. If source evidence conflicts, prefer executable source/tests at the pinned revision, then versioned contracts/fixtures, then current integration docs, then README/history. If still ambiguous, stop dependent work and request a decision.

## 9. First directive

Do not start by generating a dashboard or a large mock app. Complete source audit and traceability, validate contracts and architecture, then create the minimal compiling Android foundation. The first milestone is audit and architecture sign-off, not mock UI.
