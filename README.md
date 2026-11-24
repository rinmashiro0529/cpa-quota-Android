# CPA Quota for Android

> Native Android implementation of CPA Quota. This repository follows the product and business contracts of the iOS reference implementation while delivering a first-class Android experience.

## Project status

**Stage:** Planning / architecture baseline.  
**Target:** Complete functional migration of the iOS product to native Android.  
**Implementation:** Kotlin + Jetpack Compose.  
**Source of truth:** The approved project documents in this repository and the pinned iOS reference revision recorded in `docs/SOURCE_AUDIT.md`.

No production feature should be claimed complete until its implementation, tests, and platform acceptance evidence are recorded.

## Start here (required reading)

All developers and coding agents MUST read these documents before making changes:

1. [Project Constitution](PROJECT_CONSTITUTION.md) — product intent, non-negotiable principles, scope and decision authority.
2. [Architecture](docs/ARCHITECTURE.md) — module boundaries, dependency rules, data flow and platform design.
3. [Migration Plan](docs/MIGRATION_PLAN.md) — phases, sequencing, dependencies and exit criteria.
4. [Task Breakdown](docs/TASK_BREAKDOWN.md) — epics, tasks, acceptance criteria and dependency graph.
5. [Source Audit](docs/SOURCE_AUDIT.md) — audited iOS structure, source-of-truth boundaries and unresolved audit work.
6. [Agent Instructions](AGENTS.md) — mandatory workflow, coding constraints and definition of done.
7. [Architecture Decision Records](docs/adr/README.md) — decisions and how to propose changes.

## Product scope

The Android app is intended to cover the complete iOS feature set:

- CPA server connections, credential lifecycle and account discovery.
- Multi-account quota snapshots, windows, metrics, stale data, refresh, cancellation and error isolation.
- CAP Token Usage Tracker read-only statistics and diagnostics.
- AI model discovery and OpenAI-compatible streaming chat, persistence, memory, skills and optional search providers.
- Independent monitoring service integration, capabilities, session lifecycle, revisions, sequences, leases and cancellation reconciliation.
- Android home-screen widgets, notifications, background work and lifecycle recovery, implemented using Android-native capabilities and limitations.
- Settings, diagnostics, accessibility, localization, privacy and release operations.

“Complete migration” means feature and business-behavior parity where the platform supports it. It does **not** mean reproducing iOS-only APIs or promising impossible Android background guarantees.

## Technology baseline

- Kotlin; Gradle Kotlin DSL; version catalog.
- Jetpack Compose + Material 3.
- AndroidX ViewModel, Lifecycle, Navigation Compose.
- Kotlin Coroutines + Flow.
- OkHttp + Retrofit (or a justified equivalent) and Kotlin Serialization.
- Room for structured durable data; DataStore for non-secret preferences.
- Android Keystore-backed encryption for secrets.
- WorkManager for deferrable work; foreground services only when a user-visible, policy-compliant ongoing task truly requires one.
- Hilt for dependency injection, subject to an ADR and current Android compatibility.
- JUnit, coroutine test utilities, MockWebServer, Compose UI tests and instrumentation tests.

Versions must be selected from currently supported stable releases at implementation time and pinned centrally. Do not blindly copy versions from this planning document.

## Repository layout (target)

```text
app/
core/{common,model,domain,data,network,database,datastore,security,design,testing}/
feature/{dashboard,accounts,quota,capusage,chat,connections,monitoring,settings,diagnostics}/
platform/{widget,notification,background,lifecycle}/
docs/
  adr/
  contracts/
  plans/
```

The architecture document governs the actual module graph. Avoid creating modules without a clear ownership or dependency reason.

## Development rule

Work in small, reviewable PRs. Every behavior change must have tests. Every feature must satisfy its acceptance criteria. Never place secrets, real service credentials, private configuration, signing material or user data in this repository.

## Current next action

Complete Phase 0 source audit and architecture validation before implementing production feature logic. The initial engineering task is [A0-01: establish source inventory and traceability](https://github.com/rinmashiro0529/cpa-quota-Android/issues/1).

### Initial GitHub work queue

- [#1 A0-01 Source inventory and feature traceability](https://github.com/rinmashiro0529/cpa-quota-Android/issues/1)
- [#2 A0-02 CPA API and quota contract extraction](https://github.com/rinmashiro0529/cpa-quota-Android/issues/2)
- [#3 A0-03 CAP plugin contract extraction](https://github.com/rinmashiro0529/cpa-quota-Android/issues/3)
- [#4 A0-04 AI workspace behavior audit](https://github.com/rinmashiro0529/cpa-quota-Android/issues/4)
- [#5 A0-05 Go monitor service contract audit](https://github.com/rinmashiro0529/cpa-quota-Android/issues/5)
- [#6 A0-06 UX, navigation and accessibility inventory](https://github.com/rinmashiro0529/cpa-quota-Android/issues/6)
- [#7 A0-07 Security and privacy threat model](https://github.com/rinmashiro0529/cpa-quota-Android/issues/7)
- [#8 B1-01 Validate and approve Android architecture](https://github.com/rinmashiro0529/cpa-quota-Android/issues/8)

## Reference

- iOS source: https://github.com/rinmashiro0529/cpa-quota-ios
- Android repository: https://github.com/rinmashiro0529/cpa-quota-Android
