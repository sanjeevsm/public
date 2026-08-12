#!/usr/bin/env bash
# Simple repo-level port auditor — reads ports.yml for numbers and reports listeners
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$ROOT_DIR/ports.yml"

if [ ! -f "$MANIFEST" ]; then
  echo "ports.yml not found at $MANIFEST"
  exit 1
fi

ports=$(grep -Eo "[0-9]{2,5}" "$MANIFEST" | sort -n | uniq)
echo "Scanning ports from $MANIFEST"
for p in $ports; do
  if command -v lsof >/dev/null 2>&1; then
    pid=$(lsof -t -iTCP:"$p" -sTCP:LISTEN 2>/dev/null || true)
  else
    pid=$(netstat -aon 2>/dev/null | grep ":$p " | sed -n 's/.* \([0-9]*\)$/\1/p' | head -n1 || true)
  fi
  if [ -n "$pid" ]; then
    cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
    echo "Port $p -> PID(s): $pid -> $cmd"
  fi
done

echo "Done."