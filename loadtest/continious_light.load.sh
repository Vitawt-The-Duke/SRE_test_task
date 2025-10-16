#!/bin/bash

while true; do;curl -s -o /dev/null "http://127.0.0.1:8080/work?latencyMs=100&failRatePct=0";sleep 0.1;done