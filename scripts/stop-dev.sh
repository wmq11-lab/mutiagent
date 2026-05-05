#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "[stop-dev] Stopping mutiagent dev server..."

# 1) Try to stop by command line signature first.
if pgrep -f "uvicorn mutiagent.api.main:app" >/dev/null 2>&1; then
  pkill -INT -f "uvicorn mutiagent.api.main:app" || true
  sleep 1
  pkill -TERM -f "uvicorn mutiagent.api.main:app" || true
fi

# 2) Fallback: any process still listening on port 8000.
PIDS="$(lsof -ti tcp:8000 || true)"
if [[ -n "${PIDS}" ]]; then
  echo "[stop-dev] Force killing port 8000 pids: ${PIDS}"
  kill -9 ${PIDS} || true
fi

if pgrep -f "uvicorn mutiagent.api.main:app" >/dev/null 2>&1; then
  echo "[stop-dev] WARNING: Some processes may still be running."
  exit 1
fi

echo "[stop-dev] Done."
