# Runbook: High burn rate (availability)

**Trigger:** “AvailabilityBudgetBurnFast/Slow” alerts — error ratio burning the 99.9% SLO budget.

**Triage (2–3 min)**
- Open Grafana dashboard: http://103.167.235.175:3000/d/nunchi-sli → check **Error ratio** and **RPS**; split by **path/status** to find the offender.
- Check recent deploy/changes. If correlated → **rollback** or **disable feature flag**.

**Stabilize (5–10 min)**
- If saturation: reduce traffic (scale out, add rate-limit/load-shed), or **open circuit breaker** on hot path; verify error ratio drops.
- Confirm Prometheus **Targets** are UP and app **/healthz** is OK.

**Aftercare**
- Capture root cause (logs/traces by path), open a ticket, add a deploy marker/guardrail for the next release.

