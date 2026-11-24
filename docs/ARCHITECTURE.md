# Android Architecture Specification

**Status:** Proposed baseline; validate against source audit before production implementation.  
**Style:** Feature-oriented modular monolith + Clean Architecture + unidirectional UI state.

## 1. Goals

Native Kotlin Android, Compose UI, full iOS feature/behavior parity, one authoritative implementation per business rule, explicit DTO/domain/UI boundaries, deterministic tests, strict secret isolation and bounded background work. Avoid premature micro-modules.

## 2. Target module graph

- app
- core: common, model, domain, data, network, database, datastore, security, design, ui, testing
- feature: connections, dashboard, accounts, quota, capusage, chat, monitoring, settings, diagnostics
- platform: widget, notification, background, lifecycle

This is a target decomposition, not a requirement to create every module immediately. Create modules when there is a stable ownership boundary, independent testing need or platform/dependency isolation.

### Ownership
- app: composition root, manifest, navigation assembly, startup and build variants; no business rules.
- core: shared primitives, domain contracts, repository abstractions, network transport, persistence, secure storage, design system and test utilities.
- feature modules: feature-owned screens, ViewModels, UI state and cohesive feature implementation.
- platform modules: Android-specific widgets, notification, scheduling and lifecycle adapters.

## 3. Dependency rules

1. Domain depends only on Kotlin/JDK abstractions and core model/common.
2. Presentation depends on domain/use cases and design system; never directly on HTTP clients, DAOs or ciphertext.
3. Data implements domain interfaces and may depend on network/database/security.
4. Network DTOs never leak into domain or Compose.
5. Room entities never leak outside persistence/data boundaries.
6. Feature modules communicate through stable public contracts or app-level navigation; avoid feature-to-feature implementation dependencies.
7. Platform adapters depend inward; domain never imports Android APIs.
8. DI is wired at composition root; no service locator or global mutable singleton.
9. No circular dependencies; enforce boundaries with Gradle checks or architecture tests.
10. Use constructor injection and explicit scopes.

## 4. State and UI

Use unidirectional data flow:
- ViewModel exposes immutable StateFlow<UiState>.
- UI sends typed intents.
- UI collects lifecycle-aware state.
- One-off effects use an explicit event contract.
- Screen rendering is a function of state.
- No network requests in Composable bodies or recomposition callbacks.
- Refresh occurs under explicit lifecycle/user policy, not repeated composition.
- Loading, refreshing, partial success, stale data, unavailable capability, account failure and connection failure remain distinct.

## 5. Domain model rules

Model nullable values, typed units/timestamps, provenance, freshness, connection identity and credential types explicitly. Errors are sealed domain types, not user-facing strings. Formatting belongs to presentation. Account identity is scoped by server.

Candidate types (illustrative only; validate exact fields and constraints against Swift source):
- ServerId, AccountId
- ManagementKey, InferenceApiKey, MonitorBridgeToken as distinct sensitive value types
- SnapshotSource = PASSIVE | LIVE
- QuotaSnapshot with source, fetchedAt, observedAt, windows, metrics and optional credits

Do not freeze schema from examples before the source audit.

## 6. Network architecture

- Shared configured HTTP transport where appropriate; separate clients/interceptors per security principal and API family.
- HTTPS-only for CPA and monitor; no trust-all TLS or certificate-validation bypass.
- Reject unsafe URL components; preserve legitimate reverse-proxy prefixes.
- Explicit connect/read/write/call timeouts and response-size limits.
- Disable credential-bearing redirects unless source contract validates safe same-origin behavior; never forward Authorization across origins.
- Redact headers, query strings, bodies and exception messages before logging.
- Map transport and HTTP failures to typed domain errors.
- Retry only where explicitly permitted; obey Retry-After and shared cooldown.
- No generic retry interceptor for management calls.
- Bound management concurrency and coalesce same-account reads.
- Propagate coroutine cancellation to underlying network Call/stream.
- Inject clock and dispatchers for deterministic tests.

### SSE
Build an incremental parser handling CRLF/LF, multi-line data, comments, event/id fields if used, UTF-8 split boundaries, partial chunks, malformed frames, terminal events and cancellation. Never assume one network chunk equals one JSON event. Verify provider behavior first.

## 7. Persistence

- Room for structured durable data: conversations, messages, memory, skills and other source-verified durable records.
- DataStore for non-secret preferences and small metadata.
- Secrets only in a protected credential store; no plaintext in Room/DataStore.
- Quota snapshots remain in-memory unless source/product owner approves a change; current iOS contract says process-local cache.
- Test migrations from every supported prior schema.
- Define retention, deletion, export and backup for chat data.
- Exclude credentials/key material from Android Auto Backup; explicitly decide user-data backup policy.

## 8. Security

- AES-GCM data encryption key protected by Android Keystore; persist ciphertext, nonce and key alias only.
- Prefer hardware-backed keys when available but do not claim all devices are hardware-backed.
- Biometric/device-auth-bound keys require explicit UX/recovery ADR.
- No plaintext fallback if Keystore unavailable; surface secure-storage error.
- Separate credential types and namespaces.
- Redact secrets from logs, analytics and crash breadcrumbs.
- Review exported components, deep links, PendingIntent mutability and notification actions.
- Disable cleartext via network security config.
- Certificate pinning is not default unless rotation/recovery is designed.
- Review screenshots/recents, clipboard, notification privacy and backup.

## 9. Background and system integration

- WorkManager for deferrable work; periodic work is inexact. Never promise fixed-frequency quota polling.
- Foreground service only for eligible user-visible ongoing work; not a silent-polling workaround.
- Widget updates are best-effort and system-budgeted; show freshness and provide supported manual refresh.
- Separate server acceptance, push provider acceptance, device receipt and visible notification.
- Test Doze, app standby, force-stop, process death, reboot, permission revocation and OEM restrictions.
- One owner per background workflow; no duplicate schedulers.

## 10. AI chat

Feature-owned ModelCatalogRepository, streaming completion source, SSE parser, ChatEngine, Room ConversationRepository, MemoryRepository, SkillRepository, optional SearchProvider adapters and bounded background continuation coordinator. Tool execution must be bounded and permissioned. Never promise indefinite generation after process death.

## 11. Monitor

Reuse existing Go endpoints and versioned DTOs. MonitorRepository/SessionCoordinator owns UUID/revision/sequence/lease state. Reconcile uncertain outcomes with same UUID. Keep bridge token separate. Server cancellation tombstone is not local notification dismissal. Do not change Go protocol for client convenience without coordinated ADR. Do not port APNs-specific mechanics.

## 12. Testing

- Domain tests with fake clock/dispatchers.
- DTO serialization and fixture tests.
- MockWebServer for auth, headers, redirects, timeout, limits, Retry-After and cancellation.
- Concurrency tests for coalescing, bounded parallelism, cooldown and stale response races.
- Room migration/DAO tests.
- SSE parser boundary tests.
- Compose UI and accessibility tests.
- Emulator and physical-device instrumentation.
- Widget/background/notification tests across supported API levels.
- Security tests for redaction, storage, backup and exported components.

## 13. Package namespace

Proposed root package: com.rinspace.cpaquota. Provisional; confirm product/owner naming before release.

## 14. Architecture sign-off

- [ ] Every iOS feature and source subsystem has Android owner.
- [ ] Endpoint and DTO inventory source-verified.
- [ ] Critical state machines documented and tested.
- [ ] Module graph has no cycles.
- [ ] Secret lifecycle and backup approved.
- [ ] Background mapping is honest and policy-compliant.
- [ ] minSdk/targetSdk selected from current support requirements.
- [ ] Stable dependencies pinned centrally.
- [ ] CI verifies compile, lint, tests, scans and release assembly.
