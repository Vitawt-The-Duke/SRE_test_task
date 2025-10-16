#!/usr/bin/env bash
# add to cron for tests
# * * * * * root /projects/loadtest/run_one_per_minute.sh

set -euo pipefail

DIR="/projects/loadtest"
LOG="/var/log/loadtest.log"
STATE="/var/run/nunchi-loadtest.index"
LOCK="/var/run/nunchi-loadtest.lock"

# List your scripts here in the order you want them to run
SCRIPTS=(
  "continious_light.load.sh"
  "error_spike_trigger.sh"
  "error_spike.sh"
  "latency_spike.sh"
  "load.sh"
  "mixed_burst.sh"
)

mkdir -p /var/run

# Prevent overlap if a previous minute is still running
exec 9>"$LOCK"
flock -n 9 || exit 0

# Figure out which script to run this minute
idx=0
if [[ -f "$STATE" ]]; then
  read -r idx < "$STATE" || idx=0
fi
[[ "$idx" =~ ^[0-9]+$ ]] || idx=0

count=${#SCRIPTS[@]}
script="${SCRIPTS[$((idx % count))]}"

# Store next index for the following minute
echo $(( (idx + 1) % count )) > "$STATE"

# Run it
cd "$DIR"
chmod +x "$script" || true
echo "[$(date -Is)] Running: $script" >> "$LOG"
bash "$script" >> "$LOG" 2>&1 || echo "[$(date -Is)] $script exited non-zero" >> "$LOG"
