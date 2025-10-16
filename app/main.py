# =============================================================================
# SRE Mini-Challenge — App instrumentation with Prometheus
#
# This Flask app exposes:
#   - /work    : a toy endpoint with controllable latency and failure rate
#   - /healthz : basic liveness check (always 200 OK)
#   - /metrics : Prometheus exposition format with our custom metrics
#
# What we measure (maps directly to the task requirements):
#   • Request count                -> Counter: http_requests_total{method,path,status}
#   • Error count / ratio          -> Derived from http_requests_total filtered by 5xx
#   • Latency distribution (p50/90/99) -> Histogram: http_request_duration_seconds_bucket
#   • In-flight requests           -> Gauge: http_inprogress_requests{method,path}
#
# With these metrics, we can compute:
#   - Availability SLI (success ratio)  = 1 - (5xx / all)
#   - Latency SLI (p99)                 via histogram_quantile on the latency histogram
# =============================================================================

from flask import Flask, request, jsonify
import random, time
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ----------------------------- Metric definitions ----------------------------
# A Counter only increases; perfect for counting requests over time.
# Labels let us slice/aggregate by HTTP method, logical path, and status code.
REQS = Counter(
    "http_requests_total",
    "Total number of HTTP responses, labeled by method/path/status.",
    ["method", "path", "status"]
)

# We keep a separate Gauge for "how many requests are currently being processed".
# This is useful to spot saturation/backlog during traffic bursts.
INPROG = Gauge(
    "http_inprogress_requests",
    "Number of in-progress HTTP requests.",
    ["method", "path"]
)

# A Histogram captures a latency **distribution** into buckets.
# It gives us _count, _sum, and _bucket series so Prometheus can calculate p50/p90/p99.
# Buckets are chosen to cover sub-10ms up to multi-second tails typical for web APIs.
LAT = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds.",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 2, 5, 10]
)

# ------------------------- Request lifecycle hooks ---------------------------
# We use Flask's before/after hooks to instrument **all** handlers consistently.
# This guarantees every request increments counters and observes latency
# without repeated code in each endpoint.

@app.before_request
def _before_request():
    """
    Runs before every request handler:
      - Record a start timestamp so we can compute duration later.
      - Increment the in-progress Gauge (labels: method + path).
    """
    # Save the monotonic start time on the request context (fast + per-request storage).
    request._t0 = time.time()

    # Important: label cardinality — we use the literal PATH here because our API surface
    # is tiny (/work, /healthz, /metrics). In large systems we would prefer *route templates*
    # (e.g., "/orders/:id") to avoid label explosion.
    INPROG.labels(request.method, request.path).inc()


@app.after_request
def _after_request(resp):
    """
    Runs after the handler produced a response:
      - Compute request duration and put it into the histogram.
      - Increment the total request counter, labeled with the final status code.
      - Decrement the in-progress Gauge so it returns to baseline.
    We use try/finally to ensure the Gauge is decremented even if something goes wrong.
    """
    try:
        # Compute elapsed time (seconds). If for any reason _t0 is missing,
        # fall back to zero-duration to avoid throwing in the metrics path.
        elapsed = max(0.0, time.time() - getattr(request, "_t0", time.time()))

        # Observe the latency with method/path labels — enables per-endpoint p99 in PromQL.
        LAT.labels(request.method, request.path).observe(elapsed)

        # Count this response; status is part of the label set so we can slice 5xx, 4xx, etc.
        REQS.labels(request.method, request.path, str(resp.status_code)).inc()
    finally:
        # Always decrement in-progress to avoid leaking the Gauge on exceptions/timeouts.
        INPROG.labels(request.method, request.path).dec()

    return resp

# ----------------------------- Metrics endpoint ------------------------------
# Prometheus scrapes this endpoint. We do NOT add additional instrumentation
# here to avoid self-observation skewing our SLI metrics.
@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

# ------------------------------ Health endpoint ------------------------------
# Very lightweight liveness probe; in a real system we might also add /ready
# to assert downstreams (DB, cache) are healthy before accepting traffic.
@app.route("/healthz")
def health():
    return "ok", 200

# --------------------------------- Workload ----------------------------------
# /work simulates:
#   - controllable latency: latencyMs query param (default 100ms)
#   - controllable failure rate: failRatePct query param (0..100, default 0)
# This lets us generate bursts and failures to validate the dashboard/SLIs.
@app.route("/work")
def work():
    # Parse latency (ms) and failure rate (%) from query params with safe defaults.
    latency_ms = int(request.args.get("latencyMs", 100))
    fail_rate_pct = int(request.args.get("failRatePct", 0))

    # Sleep to simulate server-side processing time.
    time.sleep(latency_ms / 1000.0)

    # Randomly fail according to the specified percentage.
    if random.randint(0, 100) < fail_rate_pct:
        # 500 maps to "server error" and will contribute to the error ratio SLI.
        return jsonify({"ok": False, "error": "simulated"}), 500

    # Successful response; contributes to the success portion of the SLI.
    return jsonify({"ok": True, "latencyMs": latency_ms, "failRatePct": fail_rate_pct}), 200

# --------------------------------- Bootstrap ---------------------------------
# Bind to 0.0.0.0 so Docker can publish the container port widely.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
