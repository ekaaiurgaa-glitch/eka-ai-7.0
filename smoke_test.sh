#!/bin/bash

BASE_URL="http://localhost:8000"
TOKEN="fake-super-secret-token"

echo -e "\n=== EKA-AI Smoke Test ==="

# Test 1: Root endpoint
echo -e "\n[1/6] Testing root endpoint..."
curl -s $BASE_URL | jq . 2>/dev/null || curl -s $BASE_URL

# Test 2: Chat endpoint
echo -e "\n[2/6] Testing chat endpoint..."
curl -s -X POST "$BASE_URL/api/v1/chat/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"Brake grinding noise","vehicle":{"make":"Maruti","model":"Swift","year":2019,"fuel":"petrol"},"tenant_id":"tenant_123"}' \
  | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/api/v1/chat/query" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"query":"Brake grinding noise","vehicle":{"make":"Maruti","model":"Swift","year":2019,"fuel":"petrol"},"tenant_id":"tenant_123"}'

# Test 3: Job cards creation
echo -e "\n[3/6] Testing job cards creation..."
curl -s -X POST "$BASE_URL/api/v1/job-cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"vehicle_id":1,"vehicle_number":"MH12AB1234","customer_name":"Test User","customer_phone":"9876543210","complaint":"Brake issue","tenant_id":"tenant_123"}' \
  | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/api/v1/job-cards" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"vehicle_id":1,"vehicle_number":"MH12AB1234","customer_name":"Test User","customer_phone":"9876543210","complaint":"Brake issue","tenant_id":"tenant_123"}'

# Test 4: MG calculation
echo -e "\n[4/6] Testing MG calculation..."
curl -s -X POST "$BASE_URL/api/v1/mg/calculate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"make":"Maruti","model":"Swift","year":2019,"fuel_type":"petrol","city":"Mumbai","monthly_km":1000,"warranty_status":"out_of_warranty","usage_type":"personal","tenant_id":"tenant_123"}' \
  | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/api/v1/mg/calculate" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"make":"Maruti","model":"Swift","year":2019,"fuel_type":"petrol","city":"Mumbai","monthly_km":1000,"warranty_status":"out_of_warranty","usage_type":"personal","tenant_id":"tenant_123"}'

# Test 5: Operator execute
echo -e "\n[5/6] Testing operator execute..."
curl -s -X POST "$BASE_URL/api/v1/operator/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"intent":"create_job_card","args":{},"tenant_id":"tenant_123","actor_id":"user_456"}' \
  | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/api/v1/operator/execute" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"intent":"create_job_card","args":{},"tenant_id":"tenant_123","actor_id":"user_456"}'

# Test 6: Dashboard metrics
echo -e "\n[6/6] Testing dashboard metrics..."
curl -s "$BASE_URL/api/v1/dashboard/metrics?dashboard_type=overview" \
  -H "Authorization: Bearer $TOKEN" \
  | jq . 2>/dev/null || curl -s "$BASE_URL/api/v1/dashboard/metrics?dashboard_type=overview" -H "Authorization: Bearer $TOKEN"

echo -e "\n=== Smoke Test Complete ==="
