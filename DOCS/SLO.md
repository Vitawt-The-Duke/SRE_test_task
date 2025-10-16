# SLOs & SLIs — SRE Mini-Challenge

## Service & Context
- **Service:** test-app (Flask HTTP API) + backing PostgreSQL (simulated).
- **Recent issue:** intermittent 5xx and latency spikes during bursts.

## SLIs
1) **Availability (success ratio)**  
   `availability = 1 - (5xx / all_requests)`  
   *We exclude 4xx from errors as user-caused.*

2) **Latency**  
   p99 of HTTP request duration for `/work` (application latency).

## SLO Targets
- **Availability:** 99.9% succeed over 7 days  
  → Error budget **0.1%** (~10m 5s per 7d).
- **Latency:** 99% of requests **≤ 300 ms** over 24 hours  
  → Tail-tolerant but user-friendly.

## Metrics (Prometheus)
- `http_requests_total{method,path,status}` — Counter
- `http_request_duration_seconds_bucket{le,method,path}` — Histogram
- `http_inprogress_requests{method,path}` — Gauge

## PromQL (examples)
- **RPS**  
  `sum by (method, path) (rate(http_requests_total[1m]))`
- **Error ratio**  
  `sum(rate(http_requests_total{status=~"5.."}[1m])) / sum(rate(http_requests_total[1m]))`
- **Latency p50/p90/p99**  
  `histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{path="/work"}[1m])))`

## Rationale
- Availability SLO protects core reliability; 99.9% aligns with small API.
- Latency SLO uses p99 to capture tail behavior during bursts.
- Histogram + labels (`method`, `path`, `status`) keep cardinality safe.

## Error Budget Policy (summary)
- **Fast burn** → page & consider rollback.  
- **Slow burn** → ticket, mitigation (throttle, circuit breaker), root-cause.
