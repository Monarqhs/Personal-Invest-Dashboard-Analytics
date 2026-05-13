#!/usr/bin/env bash
# Regenerates TypeScript types from FastAPI's OpenAPI schema.
# Run: bash packages/shared/scripts/codegen.sh
# CI uses this to verify types are up-to-date; fails build on diff.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUT_DIR="$REPO_ROOT/packages/shared/typescript/src/generated"
API_DIR="$REPO_ROOT/apps/api"

mkdir -p "$OUT_DIR"

echo "Starting ephemeral FastAPI instance to dump OpenAPI schema..."
cd "$API_DIR"

# Start API in background, wait for readiness, dump schema, kill
uvicorn src.main:app --host 127.0.0.1 --port 18765 &
API_PID=$!

for i in {1..15}; do
  if curl -sf http://127.0.0.1:18765/openapi.json > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -sf http://127.0.0.1:18765/openapi.json > /tmp/openapi.json
kill $API_PID 2>/dev/null || true

echo "Generating TypeScript types from OpenAPI schema..."
cd "$REPO_ROOT"
pnpm exec openapi-typescript /tmp/openapi.json --output "$OUT_DIR/api.d.ts"

echo "Codegen complete: $OUT_DIR/api.d.ts"
