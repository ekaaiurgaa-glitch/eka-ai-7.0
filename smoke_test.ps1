$BASE_URL = "http://localhost:8000"
$TOKEN = "fake-super-secret-token"

Write-Host "`n=== EKA-AI Smoke Test ===" -ForegroundColor Cyan

# Test 1: Root endpoint
Write-Host "`n[1/6] Testing root endpoint..." -ForegroundColor Yellow
$response = curl.exe -s $BASE_URL
Write-Host "Response: $response" -ForegroundColor Green

# Test 2: Chat endpoint
Write-Host "`n[2/6] Testing chat endpoint..." -ForegroundColor Yellow
$chatPayload = '{"query":"Brake grinding noise","vehicle":{"make":"Maruti","model":"Swift","year":2019,"fuel":"petrol"},"tenant_id":"tenant_123"}'
$response = curl.exe -s -X POST "$BASE_URL/api/v1/chat/query" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d $chatPayload
Write-Host "Response: $response" -ForegroundColor Green

# Test 3: Job cards creation
Write-Host "`n[3/6] Testing job cards creation..." -ForegroundColor Yellow
$jobPayload = '{"vehicle_id":1,"vehicle_number":"MH12AB1234","customer_name":"Test User","customer_phone":"9876543210","complaint":"Brake issue","tenant_id":"tenant_123"}'
$response = curl.exe -s -X POST "$BASE_URL/api/v1/job-cards" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d $jobPayload
Write-Host "Response: $response" -ForegroundColor Green

# Test 4: MG calculation
Write-Host "`n[4/6] Testing MG calculation..." -ForegroundColor Yellow
$mgPayload = '{"make":"Maruti","model":"Swift","year":2019,"fuel_type":"petrol","city":"Mumbai","monthly_km":1000,"warranty_status":"out_of_warranty","usage_type":"personal","tenant_id":"tenant_123"}'
$response = curl.exe -s -X POST "$BASE_URL/api/v1/mg/calculate" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d $mgPayload
Write-Host "Response: $response" -ForegroundColor Green

# Test 5: Operator execute
Write-Host "`n[5/6] Testing operator execute..." -ForegroundColor Yellow
$opPayload = '{"intent":"create_job_card","args":{},"tenant_id":"tenant_123","actor_id":"user_456"}'
$response = curl.exe -s -X POST "$BASE_URL/api/v1/operator/execute" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d $opPayload
Write-Host "Response: $response" -ForegroundColor Green

# Test 6: Dashboard metrics
Write-Host "`n[6/6] Testing dashboard metrics..." -ForegroundColor Yellow
$response = curl.exe -s "$BASE_URL/api/v1/dashboard/metrics?dashboard_type=overview" -H "Authorization: Bearer $TOKEN"
Write-Host "Response: $response" -ForegroundColor Green

Write-Host "`n=== Smoke Test Complete ===" -ForegroundColor Cyan
