#!/usr/bin/env bash
# Smoke test for the API. Run with the server at http://localhost:8000 (or set BASE_URL).

set -e
BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Testing API at $BASE_URL"
echo ""

# Health
echo "1. GET /health"
curl -s "$BASE_URL/health" | head -c 200
echo -e "\n"

# Register
echo "2. POST /auth/register"
REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"secret123"}')
echo "$REGISTER"
USER_ID=$(echo "$REGISTER" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

# Login
echo ""
echo "3. POST /auth/login"
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"secret123"}')
echo "$LOGIN"
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

# Login with wrong password (expect 401)
echo ""
echo "4. POST /auth/login (wrong password - expect 401)"
curl -s -w "\nHTTP %{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"wrong"}'
echo -e "\n"

if [ -n "$TOKEN" ]; then
  echo "5. Example: use token for protected route (if cart exists)"
  curl -s -w "\nHTTP %{http_code}" -X GET "$BASE_URL/cart" \
    -H "Authorization: Bearer $TOKEN"
  echo -e "\n"
fi

echo "Done."
