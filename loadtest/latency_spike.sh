#!/bin/bash

for i in $(seq 1 500); do
  curl -s -o /dev/null \
  "http://127.0.0.1:8080/work?latencyMs=800&failRatePct=0" &
  sleep 0.05
done
wait
