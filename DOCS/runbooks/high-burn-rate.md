# Runbook: High burn rate (availability)

**Trigger:** AvailabilityBudgetBurnFast / AvailabilityBudgetBurnSlow

**Triage (2–3 min)**
- Grafana: http://103.167.235.175:3000/d/test-sli → check **Error ratio** & **RPS**; break down by **path/status**.
- Check recent deploy/feature flag; if correlated → **rollback/disable**.

**Stabilize (5–10 min)**
- If saturation: scale out or shed load; consider enabling a **circuit breaker** on hot path.
- Verify Prometheus targets are **UP**; `/healthz` returns OK.

**Aftercare**
- Capture root cause (logs/traces, by path), open a ticket; add guardrails (deploy markers, alert tuning).
