#!/bin/bash
# Chain Of Record - API Testing Script
# Tests all major API endpoints to validate functionality

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
VERBOSE="${VERBOSE:-false}"

# Statistics
TESTS_PASSED=0
TESTS_FAILED=0

echo "=================================================================="
echo "CHAIN OF RECORD - API TESTING"
echo "=================================================================="
echo "API URL: $API_URL"
echo "Time: $(date)"
echo "=================================================================="
echo ""

# Function to print test result
print_result() {
    local test_name=$1
    local status=$2
    local message=$3
    
    if [ "$status" == "PASS" ]; then
        echo -e "${GREEN}✓${NC} PASS: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} FAIL: $test_name"
        echo -e "  ${RED}Error: $message${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to test an endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4
    local data=$5
    
    echo -e "${BLUE}Testing:${NC} $name"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract status code (last line) and body (everything else)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$VERBOSE" == "true" ]; then
        echo "Response: $body"
        echo "Status Code: $status_code"
    fi
    
    # Check status code
    if [ "$status_code" == "$expected_status" ]; then
        # Validate JSON if jq is available
        if command -v jq &> /dev/null; then
            if echo "$body" | jq empty 2>/dev/null; then
                print_result "$name" "PASS" ""
            else
                print_result "$name" "FAIL" "Invalid JSON response"
            fi
        else
            print_result "$name" "PASS" ""
        fi
    else
        print_result "$name" "FAIL" "Expected status $expected_status, got $status_code"
    fi
    
    echo ""
}

# Function to test an endpoint and extract ID from response
test_endpoint_with_id() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4
    local data=$5
    local id_field=$6
    
    echo -e "${BLUE}Testing:${NC} $name"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract status code and body
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$VERBOSE" == "true" ]; then
        echo "Response: $body"
        echo "Status Code: $status_code"
    fi
    
    # Check status code and extract ID
    if [ "$status_code" == "$expected_status" ]; then
        if command -v jq &> /dev/null; then
            if echo "$body" | jq empty 2>/dev/null; then
                entity_id=$(echo "$body" | jq -r ".$id_field")
                print_result "$name" "PASS" ""
                echo "$entity_id"
                return 0
            else
                print_result "$name" "FAIL" "Invalid JSON response"
            fi
        else
            print_result "$name" "PASS" ""
            # Try to extract ID without jq (basic parsing)
            entity_id=$(echo "$body" | grep -oP "\"$id_field\":\s*\K\d+")
            echo "$entity_id"
            return 0
        fi
    else
        print_result "$name" "FAIL" "Expected status $expected_status, got $status_code"
    fi
    
    echo ""
    echo "0"
}

echo "==================================================================="
echo "HEALTH CHECK TESTS"
echo "==================================================================="

test_endpoint "Health Check" "GET" "/health" "200"
test_endpoint "API Docs Available" "GET" "/docs" "200"
test_endpoint "OpenAPI Schema" "GET" "/openapi.json" "200"

echo "==================================================================="
echo "ENTITY ENDPOINT TESTS"
echo "==================================================================="

test_endpoint "List Entities" "GET" "/api/v1/entities" "200"
test_endpoint "List Entities with Pagination" "GET" "/api/v1/entities?skip=0&limit=10" "200"
test_endpoint "Search Entities by Name" "GET" "/api/v1/entities?name=TEST" "200"
test_endpoint "Filter Entities by Type" "GET" "/api/v1/entities?entity_type=LLC" "200"
test_endpoint "Filter Entities by Jurisdiction" "GET" "/api/v1/entities?jurisdiction=FL" "200"

# Test getting a specific entity (assuming ID 1 exists after init_db.py)
test_endpoint "Get Entity by ID" "GET" "/api/v1/entities/1" "200"

# Test entity relationships
test_endpoint "Get Entity Relationships" "GET" "/api/v1/entities/1/relationships" "200"

echo "==================================================================="
echo "PROPERTY ENDPOINT TESTS"
echo "==================================================================="

test_endpoint "List Properties" "GET" "/api/v1/properties" "200"
test_endpoint "List Properties with Pagination" "GET" "/api/v1/properties?skip=0&limit=10" "200"
test_endpoint "Filter Properties by County" "GET" "/api/v1/properties?county=Travis" "200"
test_endpoint "Get Property by ID" "GET" "/api/v1/properties/1" "200"
test_endpoint "Search Properties by Parcel ID" "GET" "/api/v1/properties?parcel_id=PARCEL" "200"

echo "==================================================================="
echo "RISK SCORING ENDPOINT TESTS"
echo "==================================================================="

test_endpoint "Get Entity Risk Score" "GET" "/api/v1/scores/entity/1" "200"
test_endpoint "List High Risk Entities" "GET" "/api/v1/scores/high-risk" "200"
test_endpoint "Filter by Risk Grade" "GET" "/api/v1/scores/high-risk?grade=B" "200"

# Test batch scoring (if endpoint exists)
echo -e "${BLUE}Testing:${NC} Batch Score Entities"
batch_response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/v1/scores/batch" \
    -H "Content-Type: application/json" \
    -d '{"entity_ids": [1]}' 2>/dev/null || echo "404")

if [ "$batch_response" == "200" ] || [ "$batch_response" == "201" ]; then
    print_result "Batch Score Entities" "PASS" ""
elif [ "$batch_response" == "404" ]; then
    echo -e "${YELLOW}⚠${NC} SKIP: Batch scoring endpoint not found (optional)"
else
    print_result "Batch Score Entities" "FAIL" "Unexpected status code: $batch_response"
fi
echo ""

echo "==================================================================="
echo "SEARCH AND FILTER TESTS"
echo "==================================================================="

test_endpoint "Full-text Search" "GET" "/api/v1/entities?q=company" "200"
test_endpoint "Complex Filter Query" "GET" "/api/v1/entities?jurisdiction=FL&entity_type=LLC&status=ACTIVE" "200"
test_endpoint "Date Range Filter" "GET" "/api/v1/properties?min_sale_date=2020-01-01" "200"

echo "==================================================================="
echo "ERROR HANDLING TESTS"
echo "==================================================================="

test_endpoint "Invalid Entity ID (404)" "GET" "/api/v1/entities/999999999" "404"
test_endpoint "Invalid Property ID (404)" "GET" "/api/v1/properties/999999999" "404"
test_endpoint "Invalid Score ID (404)" "GET" "/api/v1/scores/entity/999999999" "404"

echo "==================================================================="
echo "TEST SUMMARY"
echo "==================================================================="
echo ""
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
