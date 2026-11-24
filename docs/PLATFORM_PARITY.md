# iOS ↔ Android Feature and Platform Parity Matrix

Parity means user-visible capability and business semantics, not identical implementation or identical OS guarantees. Mark complete only with implementation links, tests and platform evidence.

| iOS capability | Android target | Required parity | Status |
|---|---|---|---|
| SwiftUI shell/navigation | Compose + Navigation | Equivalent journeys and states | Not started |
| CPA connections | Native connections | Same validation/auth/lifecycle | Not started |
| Keychain | Keystore encrypted store | Protected at rest; no plaintext fallback | Not started |
| Account discovery | Accounts feature | Same account/error scope | Not started |
| Quota snapshots/windows | Kotlin domain | Same null/unit/time/provenance | Not started |
| Refresh/cancellation/cooldown | Coroutine coordinator | Same coalescing/bounds/cooldown | Not started |
| CAP usage | CAP feature | Same read-only auth/unavailable semantics | Not started |
| AI model catalog | Chat feature | Same model discovery | Not started |
| AI SSE chat | Streaming transport/ChatEngine | Same stream/tool semantics | Not started |
| Chat/memory/skills | Room/repositories | Same persistence/user operations | Not started |
| Third-party search | Provider adapters | Same optional integrations/key isolation | Not started |
| Background chat continuation | Bounded Android execution | Honest equivalent and OS limits | Not started |
| Go monitor bridge | MonitorRepository | Same server lifecycle contract | Not started |
| Live Activity | Ongoing notification/system surface | Similar information; no false equivalence | Not started |
| WidgetKit | Glance/App Widget | Equivalent summary/config/privacy | Not started |
| Preferences | DataStore | Same user-visible settings | Not started |
| Diagnostics | Diagnostics feature | Equivalent actionable diagnostics | Not started |
| Accessibility/localization | Android resources/Semantics | Supported locale and assistive UX | Not started |
| Build/sign/release | AAB/Android signing | Reproducible secure release | Not started |

## Status definitions

- Not started: no implementation.
- Auditing: source behavior being traced.
- In progress: implementation exists but acceptance incomplete.
- Implemented: code merged, not necessarily fully verified.
- Verified: acceptance evidence/tests pass on declared devices/services.
- Platform-limited: OS limitation and approved product behavior documented.
- Not applicable: product owner approved reasoned exclusion.

Compilation, mock screenshots, historical CI or a different commit are not sufficient for Verified.
