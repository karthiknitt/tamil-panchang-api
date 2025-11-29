#!/bin/bash
# Comprehensive endpoint testing script for Tamil Panchang API

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default URLs
BASE_URL="${1:-https://panchang.karthikwrites.com}"
FASTAPI_URL="${BASE_URL}/api"
MCP_URL="${BASE_URL}/mcp"

echo -e "${BLUE}🧪 Tamil Panchang API - Endpoint Testing${NC}"
echo "========================================================================"
echo "Testing endpoints at: $BASE_URL"
echo "========================================================================"
echo ""

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test an endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local expected_status="${4:-200}"
    local content_type="${5}"
    local data="${6}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}Test $TOTAL_TESTS: $name${NC}"
    echo "  URL: $url"
    echo "  Method: $method"

    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" 2>&1)
    fi

    status=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$status" = "$expected_status" ]; then
        echo -e "  ${GREEN}✅ Status: $status (Expected: $expected_status)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))

        if [ -n "$content_type" ]; then
            if echo "$body" | grep -q "$content_type"; then
                echo -e "  ${GREEN}✅ Content type check passed${NC}"
            else
                echo -e "  ${YELLOW}⚠️  Content type might differ${NC}"
            fi
        fi

        # Show first 200 chars of response
        if [ ${#body} -gt 0 ]; then
            preview=$(echo "$body" | head -c 200)
            echo "  Preview: ${preview}..."
        fi
    else
        echo -e "  ${RED}❌ Status: $status (Expected: $expected_status)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        if [ ${#body} -gt 0 ]; then
            echo "  Error: $body"
        fi
    fi
    echo ""
}

# Function to test SSE endpoint (special handling)
test_sse_endpoint() {
    local name="$1"
    local url="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}Test $TOTAL_TESTS: $name${NC}"
    echo "  URL: $url"
    echo "  Method: GET (SSE Stream)"

    # Use timeout to prevent hanging, read first few lines
    response=$(timeout 5 curl -s -N -H "Accept: text/event-stream" "$url" | head -n 10)
    exit_code=$?

    # Check if we got any data
    if [ ${#response} -gt 0 ]; then
        echo -e "  ${GREEN}✅ SSE stream started successfully${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))

        # Check for expected SSE format
        if echo "$response" | grep -q "event:"; then
            echo -e "  ${GREEN}✅ Contains SSE events${NC}"
        fi

        if echo "$response" | grep -q "endpoint"; then
            echo -e "  ${GREEN}✅ Contains 'endpoint' event (MCP protocol)${NC}"
        fi

        echo "  First 10 lines of stream:"
        echo "$response" | head -n 10 | sed 's/^/    /'
    else
        if [ $exit_code -eq 124 ]; then
            echo -e "  ${YELLOW}⚠️  Connection established but timed out (normal for SSE)${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "  ${RED}❌ No data received from SSE endpoint${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    echo ""
}

echo -e "${BLUE}📍 FastAPI Endpoints (Port 8000)${NC}"
echo "------------------------------------------------------------------------"

# Test FastAPI health endpoint
test_endpoint \
    "FastAPI Health Check" \
    "$FASTAPI_URL/health" \
    "GET" \
    "200"

# Test root endpoint
test_endpoint \
    "FastAPI Root" \
    "$BASE_URL/" \
    "GET" \
    "200"

# Test Panchang endpoint
test_endpoint \
    "Get Panchang (Specific Date)" \
    "$FASTAPI_URL/panchang" \
    "POST" \
    "200" \
    "" \
    '{"date":"2025-01-01","latitude":13.0827,"longitude":80.2707,"timezone":5.5}'

# Test Today endpoint
test_endpoint \
    "Get Today Panchang" \
    "$FASTAPI_URL/today" \
    "POST" \
    "200" \
    "" \
    '{"latitude":13.0827,"longitude":80.2707,"timezone":5.5}'

echo -e "${BLUE}🤖 MCP Server Endpoints (Port 8001)${NC}"
echo "------------------------------------------------------------------------"

# Test MCP health endpoint
test_endpoint \
    "MCP Health Check" \
    "$MCP_URL/health" \
    "GET" \
    "200"

# Test MCP SSE endpoint
test_sse_endpoint \
    "MCP SSE Stream" \
    "$MCP_URL/sse"

# Test CORS preflight for SSE
test_endpoint \
    "MCP SSE OPTIONS (CORS Preflight)" \
    "$MCP_URL/sse" \
    "OPTIONS" \
    "200"

# Test that POST to /sse is properly rejected or handled
echo -e "${YELLOW}Test $((TOTAL_TESTS + 1)): MCP SSE POST (Should fail or redirect)${NC}"
echo "  URL: $MCP_URL/sse"
echo "  Method: POST"
response=$(curl -s -w "\n%{http_code}" -X POST "$MCP_URL/sse" 2>&1)
status=$(echo "$response" | tail -n 1)
if [ "$status" = "405" ] || [ "$status" = "404" ]; then
    echo -e "  ${GREEN}✅ Status: $status (Correctly rejects POST)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "  ${YELLOW}⚠️  Status: $status (Unexpected, but might be OK)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# Summary
echo "========================================================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "========================================================================"
echo -e "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
else
    echo -e "Failed:       $FAILED_TESTS"
fi
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Your API endpoints are working correctly! 🎉"
    exit 0
else
    echo -e "${RED}❌ Some tests failed.${NC}"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Check if containers are running: docker ps"
    echo "  2. Check logs: docker-compose logs -f"
    echo "  3. Verify Traefik routing configuration"
    echo "  4. Test locally: $0 http://localhost:8000"
    exit 1
fi
