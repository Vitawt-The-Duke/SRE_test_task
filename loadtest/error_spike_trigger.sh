#!/bin/bash

for i in $(seq 1 500); do
  curl -s -o /dev/null -w "%{http_code}\n" \
  "http://127.0.0.1:8080/work?latencyMs=200&failRatePct=50" &
  sleep 0.05
done
wait
