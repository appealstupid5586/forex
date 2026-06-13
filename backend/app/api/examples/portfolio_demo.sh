#!/usr/bin/env bash
# Demo: gửi yêu cầu POST tới /api/v1/portfolio/analyze
# Chú ý: chạy server FastAPI trước:
#   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

set -euo pipefail

URL="http://localhost:8000/api/v1/portfolio/analyze"
DATA_FILE="backend/app/skills/portfolio_analysis/examples/healthy_portfolio.json"

if [ ! -f "$DATA_FILE" ]; then
  echo "Không tìm thấy $DATA_FILE"
  exit 1
fi

echo "Gửi request tới $URL với payload $DATA_FILE"
curl -sS -X POST "$URL" \
  -H "Content-Type: application/json" \
  --data-binary "@$DATA_FILE" | jq
