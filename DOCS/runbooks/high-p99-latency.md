# Runbook: High p99 latency

**Trigger:** HighLatencyP99 (p99 > 300ms sustained 15m)

**Triage (2–3 min)**
- Compare **p50 vs p99**; big gap ⇒ tail issues. Check **In-flight**, CPU/mem; correlate with load/deploy.

**Stabilize (5–10 min)**
- Ensure **server timeouts** (Gunicorn) are active; consider **1 retry with jitter** for transient failures.
- If downstream flaky, enable **circuit breaker**; cache hot reads if applicable.

**Aftercare**
- Investigate hot path (DB query, N+1, lock/GC). Document, ticket, and add traces/markers.
