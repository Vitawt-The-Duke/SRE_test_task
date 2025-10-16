#!/bin/bash

for i in $(seq 1 1000); do
  LAT=$((RANDOM % 500 + 50))
  FAIL=$((RANDOM % 10))
  curl -s -o /dev/null \
  "http://127.0.0.1:8080/work?latencyMs=${LAT}&failRatePct=${FAIL}" &
  sleep 0.02
done
wait
