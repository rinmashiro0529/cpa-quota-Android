# Architecture Decision Records

Create records as NNNN-short-title.md.

Each ADR includes status (proposed/accepted/superseded/rejected), context and constraints, source evidence and issues, decision and alternatives, consequences/risks, migration/rollback plan, required tests and review owners.

Required initial ADR topics:
1. minSdk, targetSdk and supported device policy.
2. Gradle module graph and package namespace.
3. Dependency injection.
4. HTTP stack, redirect, timeout and SSE transport.
5. Room/DataStore schema and chat retention.
6. Keystore credential encryption and backup exclusions.
7. WorkManager/foreground service policy.
8. Widget architecture and refresh policy.
9. Navigation and adaptive Compose design system.
10. Cross-platform contract fixture ownership.

Do not rubber-stamp an unreviewed choice. Proposed ADR is not accepted until architecture owner reviews it.
