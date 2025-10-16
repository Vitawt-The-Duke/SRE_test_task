#!/bin/bash

while true;do sleep 0.1;curl -I http://localhost:8080/work?latencyMs=200&failRatePct=5;done
