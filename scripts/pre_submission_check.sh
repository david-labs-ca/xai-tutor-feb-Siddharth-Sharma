#!/usr/bin/env bash
# Pre-submission check: ensure app runs with docker-compose and core endpoints respond.
# Usage: ./scripts/pre_submission_check.sh

set -e
echo "=== Pre-submission check ==="
echo ""

echo "1. Building and starting with docker-compose..."
docker compose down 2>/dev/null || true
docker compose up -d --build
echo "   Waiting for server to be ready..."
sleep 8
echo ""

echo "2. Testing core endpoints..."
BASE="http://localhost:8000"
FAIL=0

# Health
if curl -sf "$BASE/health" > /dev/null; then
  echo "   [OK] GET /health"
else
  echo "   [FAIL] GET /health"
  FAIL=1
fi

# Register
REG=$(curl -sf -X POST "$BASE/auth/register" -H "Content-Type: application/json" -d '{"email":"check@example.com","password":"pass123"}')
if echo "$REG" | grep -q '"id"'; then
  echo "   [OK] POST /auth/register"
else
  echo "   [FAIL] POST /auth/register"
  FAIL=1
fi

# Login
LOGIN=$(curl -sf -X POST "$BASE/auth/login" -H "Content-Type: application/json" -d '{"email":"check@example.com","password":"pass123"}')
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
if [ -n "$TOKEN" ]; then
  echo "   [OK] POST /auth/login"
else
  echo "   [FAIL] POST /auth/login"
  FAIL=1
fi

# Products
if curl -sf "$BASE/products" | grep -q '"id"'; then
  echo "   [OK] GET /products"
else
  echo "   [FAIL] GET /products"
  FAIL=1
fi

# Cart (protected)
if [ -n "$TOKEN" ] && curl -sf -H "Authorization: Bearer $TOKEN" "$BASE/cart" | grep -q '"items"'; then
  echo "   [OK] GET /cart (with JWT)"
else
  echo "   [FAIL] GET /cart (with JWT)"
  FAIL=1
fi

echo ""
if [ $FAIL -eq 0 ]; then
  echo "=== All checks passed. Ready for submission. ==="
  docker compose down 2>/dev/null || true
  exit 0
else
  echo "=== Some checks failed. Fix before submission. ==="
  docker compose down 2>/dev/null || true
  exit 1
fi
