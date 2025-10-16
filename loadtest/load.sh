#!/bin/bash

while true; do curl -s 'http://103.167.235.175:8080/work?latencyMs=200&failRatePct=5' >/dev/null; sleep 0.05; done
