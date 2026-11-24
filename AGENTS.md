# Instructions for all developers and coding agents

This is the native Android migration of CPA Quota. Use the selected plan in [PR #9](https://github.com/rinmashiro0529/cpa-quota-Android/pull/9); [README.md](README.md) links its pinned revision. Start with the plan index, then read the task card, its dependencies and the agent playbook. Use the selected plan's work-item IDs rather than the retired issue queue.

## Before a task
1. Identify the GitHub issue and acceptance criteria.
2. Read relevant iOS source, tests and fixtures. Re-check source main SHA.
3. Record exact source evidence and behavior being migrated.
4. Check dependencies and ADRs.
5. If ambiguous, security-sensitive or conflicting, stop and ask; never invent behavior.

## Implementation rules
- Kotlin-first native Android; Compose for new UI.
- Follow architecture dependency direction.
- Domain must not import Android, Compose, Retrofit, Room or Hilt types.
- UI must not call HTTP clients or DAOs directly.
- Separate wire DTOs, domain entities and UI state.
- Use structured concurrency and propagate cancellation.
- Inject Clock and dispatchers for deterministic tests.
- Preserve nullability, units, timestamps, provenance, error scope, retry/cooldown and state machine semantics.
- Do not swallow CancellationException; no GlobalScope, unmanaged scopes, blocking main-thread I/O or network work in Composable bodies.
- No trust-all TLS, cleartext fallback, cross-origin credential forwarding or silent auth escalation.
- No plaintext secrets in Room, DataStore, files, logs, fixtures, analytics, crash reports or commits.
- Never add production credentials, real account IDs, private configs, signing keys or tokens.
- Pin dependencies centrally and justify new libraries.
- Do not weaken tests to make CI green.
- Do not use high-frequency polling or foreground services to evade Android background limits.
- Do not claim iOS feature equivalence without documenting Android implementation and limits.

## PR workflow
One cohesive issue per PR. Include issue, source evidence, scope/non-goals, architecture impact, tests, security/privacy impact, relevant screenshots, known limitations and exact environment. Add ADR for module, data, auth, retry, monitor, persistence, background, min SDK or major dependency changes. Update docs and parity matrix. Do not merge own PR unless repository policy explicitly allows and independent review is not required.

## Definition of Done
- All acceptance criteria met.
- Appropriate unit, contract, concurrency/cancellation, UI and instrumentation tests pass.
- Lint/static analysis pass.
- No sensitive-data exposure.
- Accessibility/localization considered.
- Docs and parity evidence updated.
- CI passes on exact PR head SHA.
- Limitations explicit; no unverified claims of complete, secure or production-ready.

## Handoff
Report changed files, source revision, behavior, tests/commands/results, PR/commit SHA, unresolved questions and next unblocked task. Do not mark dependent tasks ready while contracts remain unresolved.
