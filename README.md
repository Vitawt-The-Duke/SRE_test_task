# SRE Mini-Challenge

## What's included
- **Instrumentation:** Prometheus metrics (/metrics) - requests, latency histogram, in-flight.
- **Dashboards:** Grafana auto-provisioned dashboard (RPS, error ratio, p50/p90/p99, in-flight).
- **Alerts:** Availability (multi-window burn rate) + sustained p99 latency; each links to a runbook and dashboard.
- **Resiliency:** Gunicorn server timeouts (2 s) to cap tail latency during bursts.
- **Runbooks:** Two concise docs for high burn rate and high p99 latency.

---

## Run locally

```bash
docker compose up --build -d
# App      – http://localhost:8080
# Prom     – http://localhost:9090
# Grafana  – http://localhost:3000  (admin / SuperPuperStrongPassword667-)
```
---

## Current test environment urls:
# App Metrics 
http://103.167.235.175:8080/metrics
# Alerts 
http://103.167.235.175:9090/alerts
# Dashboard 
http://103.167.235.175:3000/d/test-sli

---

## Load tests (curl only)

### Baseline
```bash
for i in $(seq 1 400); do
  curl -s -o /dev/null "http://localhost:8080/work?latencyMs=120&failRatePct=0" &
  sleep 0.05
done; wait
```

### Error burst
```bash
for i in $(seq 1 800); do
  curl -s -o /dev/null "http://localhost:8080/work?latencyMs=200&failRatePct=50" &
  sleep 0.02
done; wait
```

### Latency burst
```bash
for i in $(seq 1 800); do
  curl -s -o /dev/null "http://localhost:8080/work?latencyMs=800&failRatePct=0" &
  sleep 0.02
done; wait
```

---

## SLIs & SLOs
- **Availability:** `1 – (5xx / all)` �� ** SLO:* 99.9 % over 7 days *
** Latency:** p99 /work �** SLO:** 99 % – 300 ms over 24 h

---

## PromQL (dashboard)
```promql
# Request rate
sum by (method, path) (rate(http_requests_total[1m]))

# Error ratio
sum(rate(http_requests_total{status=|"5.."}[0m])) / sum(rate(http_requests_total[1m]))

# Latency quantiles
histogram_quantile(0.5, sum by (le) (rate(http_request_duration_seconds_bucket{path="/work"}[1m)))
histogram_quantile(0.9, sum by (le) (rate(http_request_duration_seconds_bucket{path="/work"}[1m)))
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{path="/work"}[1m])))
```

---

## Alerts
- `alerts/availability-burn.yml`
or 
- `alerts/latency-sustained.yml`

Glob rules along the fast burn rate and sustained p99 alerts.
Reload rules:

```bash
curl -X POST http://localhost:9090/-/reload
```

----

## Runbooks
- [High burn rate](./docs/runbooks/high-burn-rate.md)
- [High p99 latency](./docs/runbooks/high-p99-latency.md)

---

## Resiliency
- [Gunicorn timeout](./resiliency/gunicorn-timeout.md) caps tail latency; simple, no app-level code.

----
