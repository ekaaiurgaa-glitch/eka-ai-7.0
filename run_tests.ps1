# EKA-AI v7.0 Test Runner
# Runs all tests with coverage reporting

Write-Host "EKA-AI v7.0 - Running Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
try {
    pytest --version | Out-Null
} catch {
    Write-Host "ERROR: pytest not found. Installing test dependencies..." -ForegroundColor Red
    pip install pytest pytest-asyncio pytest-cov httpx
}

Write-Host "Running tests with coverage..." -ForegroundColor Yellow
pytest -v --cov=app --cov-report=term-missing --cov-report=html

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Some tests failed. Check output above." -ForegroundColor Red
    exit 1
}
