# Runbook: High p99 latency

**Trigger:** “HighLatencyP99” — p99 latency > 300ms (sustained 15m).

**Triage (2–3 min)**
- Grafana: compare **p50 vs p99**; a big gap = tail issues. Check **In-flight** and container **CPU/memory**; correlate with load/deploy.

**Stabilize (5–10 min)**
- Enforce **timeouts + 1 retry with jitter** OR enable **circuit breaker** (fast-fail to protect tail). Consider a small cache for hot reads.
- Re-test and confirm p99 < 300ms; ensure error ratio remains within SLO.

**Aftercare**
- Investigate slow path (DB query, N+1, lock/GC). Create follow-up task and add observability (traces/markers).

