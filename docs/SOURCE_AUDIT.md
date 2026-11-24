# iOS Source Audit — Baseline and Traceability

**Status:** Preliminary baseline; not an exhaustive file-by-file audit.  
**Reference:** https://github.com/rinmashiro0529/cpa-quota-ios  
**Observed main tree SHA:** 80beea9ed251a628307825cba99290b5f246575b  
**Observed README blob:** 5e1c5145f2996fa7f28c9764fbd2ef4c4630e425  
**Observed Package.swift blob:** 084fc123b87004b896b5e5241c140cf9c9200b9f

Re-check iOS main before implementation. If it moved, record new SHA and review drift.

## 1. Confirmed high-level structure

| iOS path/target | Responsibility | Android destination |
|---|---|---|
| Sources/CPAQuotaKit | CPA networking, quota, CAP, credentials and state | core domain/data/network/security + connection/quota |
| Sources/CPAQuotaChat | Chat engine, JSON persistence, search/workspace | feature:chat + network/database/security |
| Sources/CPAQuotaUI | SwiftUI interface | feature modules + design system |
| Sources/CPAQuotaActivity | Widget and Live Activity | platform:widget + notification |
| Sources/CPAQuotaApp | App composition and entry | app |
| Apple/CPAQuotaActivityExtension | Widget/Activity extension | Android widget/notification |
| Services/QuotaMonitor | Independent Go monitoring service | shared backend; Android client only |
| Tests | Contract/model tests and fixtures | Android unit/contract tests |
| Apple/CPAQuotaAppUITests | Native UI tests | Compose/instrumentation tests |
| tools/tests and ci | Tooling and validation | Android CI/repository tooling |

## 2. Confirmed README capabilities

- Read-only CPA client; no upstream OAuth login and no account/config/quota mutation.
- Existing accounts, quota windows, reset times and recent results; failed reads retain and label last success.
- CAP usage and account diagnostics depend on external cap-token-usage-tracker plugin.
- Widget sharing defaults off; Live Activity has bounded display semantics and does not promise background account rotation.
- AI: GET /v1/models; POST /v1/chat/completions; OpenAI-compatible SSE; inference key distinct from management key; management key may read server key list via documented management routes; local JSON conversations/memory/skills; optional third-party search keys; bounded background continuation and local notification.
- Optional independent Go monitor service with separate authorization and deployment.
- Swift 6, iOS 17+; Go service uses Go 1.26-compatible toolchain per README.

## 3. Package.swift dependency baseline

Observed manifest: Swift tools 6.0, Swift language mode 6; products CPAQuotaKit, CPAQuotaActivity, CPAQuotaChat, CPAQuotaUI, CPAQuotaProbe and CPAQuotaApp. Dependencies: AnyLanguageModel 1.3.0, swift-http-types 1.8.0, swift-markdown 0.7.3, SwiftStreamingMarkdown pinned to revision 5f7c04e0558df6146f90d482edb62cb456986bda. Android libraries must be selected from actual usage, maintenance, license and platform fit, not mechanically ported.

## 4. Confirmed frontend contract invariants

Reviewed docs/FRONTEND_INTEGRATION.md:
- HTTPS server; unsafe URL components rejected; valid reverse-proxy prefixes preserved.
- ManagementKey sensitive, non-Codable and redacted; non-secret server identifier associates credentials.
- Keychain default WhenUnlockedThisDeviceOnly; no plaintext fallback on unsupported platforms.
- Existing observations may publish before active refresh; each account result publishes independently.
- Same-store concurrent load/refresh coalesced; cancellation prevents late state overwrite.
- Live cache process-local; documented 60-second reuse path; quota cache is not persisted to disk.
- Default staleness 300 seconds; passive data uses own observedAt; missing observedAt is unknown/stale.
- Null windows/metrics/credits remain unknown; units/currency/duration preserved.
- Management 401/403 blocks management calls; upstream account 401 remains account-scoped.
- Management 429 honors Retry-After and conservative fallback; force/reload cannot shorten cooldown.
- No default automatic retry; max three concurrent management reads.
- Shared same-account request cancellation semantics are explicitly defined.

Verify exact values against current Swift source/tests before implementing.

## 5. Confirmed CAP boundary

Reviewed docs/CAP_USAGE_BACKEND.md:
- Read-only CAP Token Usage Tracker plugin API.
- Prefer deriving CAP client from active CPA session to reuse transport/coordinator.
- Anonymous and management-key auth are explicit.
- No automatic anonymous-to-management fallback.
- No full-mode capability, decryption or raw caller API key access.
- Reverse proxy/auth behavior needs deployment verification; do not infer from unrelated routes.

Exact routes and DTOs remain to be extracted.

## 6. Confirmed monitor boundary

Reviewed docs/MONITORING_SWIFT_BACKEND.md and Go service docs:
- Bridge token distinct from CPA management key.
- Capabilities endpoint and DTO are versioned.
- Caller generates and persists UUID before create; uncertain timeout reconciles same UUID.
- Revision is expected-current CAS; sequence is monotonic snapshot version.
- HTTP 202 means accepted/pending, not completed collection or device delivery.
- HTTP 204 stop means server accepted durable cancellation intent/receipt, not APNs/device UI completion.
- Detached sessions retain original client identity for safe reconciliation.
- Server lease does not extend on process restart.
- Android must not port APNs-specific behavior or imply Android notification delivery.

Go source/tests are authoritative for exact routes and transitions.

## 7. Required audit completion

### File inventory
- [ ] Complete recursive source tree and classify every Swift file.
- [ ] Read every file under CPAQuotaKit.
- [ ] Read every file under CPAQuotaChat.
- [ ] Read every file under CPAQuotaUI.
- [ ] Read CPAQuotaActivity and CPAQuotaApp files.
- [ ] Inspect entitlements, Info.plist, Xcode project settings and schemes.
- [ ] Inventory every test and fixture, including UI tests.
- [ ] Inventory Go handlers, DTOs, storage migrations, scheduler and tests.
- [ ] Inventory icons, images, fonts, localization, privacy disclosures and licenses.

### Endpoint matrix
For each request record feature, method/path, base URL/proxy prefix, auth type, request DTO, response DTO/nullability/units/timestamp units, errors, retry/cooldown, cancellation semantics and exact source/test/fixture evidence.

### Screen/interaction matrix
Record screen, entry route, actions, loading/empty/error/stale/partial states, accessibility labels, deep links, persistence and iOS evidence. Add Android UX adaptation and parity status.

### State machines
At minimum: connection/auth/cooldown; quota refresh; CAP capability; chat streaming/tool execution; monitor lifecycle; widget snapshot; background continuation.

### Test mapping
Map every relevant Swift and Go regression test to Android tests. Preserve adversarial cases, not only happy paths.

## 8. Open questions that block dependent work

- Complete CPA/CAP/AI/search endpoint and DTO inventory.
- Full SwiftUI screen/navigation/interaction and conditional feature inventory.
- Chat persistence schema, prompt/tool semantics and recovery behavior.
- Complete monitor routes, schema versions and current Go fixtures.
- Android minSdk/targetSdk and supported device matrix.
- Android substitute for each iOS-only capability.
- Asset reuse/license rights.
- Whether shared fixtures belong in this repo or a dedicated contracts repo. Initial recommendation: keep sanitized Android-consumed fixtures here until a shared source of truth is explicitly approved.

## 9. Sign-off

Audit completes only when checklists are finished, exact source SHA recorded, critical unknowns resolved or accepted by product owner, and every in-scope iOS capability maps to Android tasks and tests.
