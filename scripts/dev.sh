#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${ROOT_DIR}/log/mutiagent.log"

cd "${ROOT_DIR}"
mkdir -p log
: > "${LOG_FILE}"

export MUTIAGENT_LOG_APPEND=1

exec uvicorn mutiagent.api.main:app \
  --reload \
  --port 8000 \
  --reload-dir "${ROOT_DIR}/src" \
  --reload-dir "${ROOT_DIR}/frontend" \
  --reload-exclude ".mutiagent/*" \
  --reload-exclude "external/*" \
  --reload-exclude "baseline/*" \
  --reload-exclude "log/*"
