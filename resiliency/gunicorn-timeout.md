# Resiliency: Gunicorn timeouts

**What:** Run `test-app` under Gunicorn with a small worker pool and server timeouts.

**Config (compose):**
```yaml
command:
  [
    "gunicorn","-w","2","-k","gthread","--threads","4",
    "--timeout","${GUNI_TIMEOUT:-2}","--graceful-timeout","${GUNI_GRTIMEOUT:-2}",
    "--bind","0.0.0.0:8080","main:app"
  ]
```

Why: Caps tail latency and prevents worker wedging during bursts/partial failures.
Trade-off: May convert very slow requests into fast 5xx, but p99 improves and service stays responsive.
Demo: Re-run curl bursts; observe p99 clipped ≤ ~2s, in-flight flatter, error ratio stable or slightly higher due to fast-fail.