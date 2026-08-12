#!/usr/bin/env bash
# Cross-platform POSIX stop-all script for iTransit+
set -euo pipefail

# Script location
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Stopping iTransit+ services (POSIX)"
echo "==============================="

ports=(9100 3002 3000)
stopped=()
for p in "${ports[@]}"; do
  # prefer lsof if available
  if command -v lsof >/dev/null 2>&1; then
    pid=$(lsof -t -iTCP:"$p" -sTCP:LISTEN 2>/dev/null || true)
  elif command -v ss >/dev/null 2>&1; then
    pid=$(ss -ltnp 2>/dev/null | grep ":$p" | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n1 || true)
  else
    pid=""
  fi

  if [ -n "$pid" ]; then
    echo "Stopping PID $pid listening on port $p"
    kill -9 $pid || true
    stopped+=("$p")
  else
    echo "No listener on port $p"
  fi
done

# kill node/python processes referencing project name
if command -v pgrep >/dev/null 2>&1; then
  pids=$(pgrep -f "itransit" || true)
  if [ -n "$pids" ]; then
    echo "Killing processes matching 'itransit': $pids"
    kill -9 $pids || true
  else
    echo "No process matched 'itransit'"
  fi
fi

echo
if [ ${#stopped[@]} -gt 0 ]; then
  echo "Stopped ports: ${stopped[*]}"
else
  echo "Nothing to stop; no iTransit+ listeners found."
fi

echo "Done."
