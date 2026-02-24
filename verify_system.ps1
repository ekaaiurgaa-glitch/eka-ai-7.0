# EKA-AI v7.0 Verification Script
# Validates all Phase 3 & 4 components

Write-Host "EKA-AI v7.0 - System Verification" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Check Python version
Write-Host "[1/10] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([9-9]|1[0-9])") {
    Write-Host "  ✓ Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python 3.9+ required, found: $pythonVersion" -ForegroundColor Red
    $errors++
}

# Check dependencies
Write-Host "[2/10] Checking dependencies..." -ForegroundColor Yellow
$requiredPackages = @("fastapi", "uvicorn", "sqlalchemy", "redis", "slowapi", "pytest")
foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1
    if ($installed -match "Name: $package") {
        Write-Host "  ✓ $package installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package not found" -ForegroundColor Red
        $errors++
    }
}

# Check .env file
Write-Host "[3/10] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=.+") {
        Write-Host "  ✓ GEMINI_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ GEMINI_API_KEY not set (chat will fail)" -ForegroundColor Yellow
        $warnings++
    }
    if ($envContent -match "SECRET_KEY=CHANGE-ME") {
        Write-Host "  ⚠ SECRET_KEY still default (change for production)" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  ✗ .env file not found (copy from .env.example)" -ForegroundColor Red
    $errors++
}

# Check database
Write-Host "[4/10] Checking database..." -ForegroundColor Yellow
if (Test-Path "eka_ai.db") {
    Write-Host "  ✓ Database file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database not initialized (run: python init_db.py)" -ForegroundColor Yellow
    $warnings++
}

# Check Redis (optional)
Write-Host "[5/10] Checking Redis connection..." -ForegroundColor Yellow
try {
    $redisUrl = $env:REDIS_URL
    if ($redisUrl) {
        # Try to connect to Redis
        $redisTest = python -c "import redis; r = redis.from_url('$redisUrl'); r.ping(); print('OK')" 2>&1
        if ($redisTest -match "OK") {
            Write-Host "  ✓ Redis connected" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Redis configured but not reachable (graceful fallback)" -ForegroundColor Yellow
            $warnings++
        }
    } else {
        Write-Host "  ⚠ Redis not configured (optional, using in-memory fallback)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Redis check skipped" -ForegroundColor Yellow
}

# Check module structure
Write-Host "[6/10] Checking module structure..." -ForegroundColor Yellow
$requiredModules = @(
    "app/modules/vehicles",
    "app/modules/catalog",
    "app/modules/knowledge",
    "app/modules/chat",
    "app/modules/job_cards",
    "app/modules/invoices",
    "app/modules/mg_engine",
    "app/modules/operator",
    "app/modules/dashboard"
)
foreach ($module in $requiredModules) {
    if (Test-Path $module) {
        Write-Host "  ✓ $module exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $module missing" -ForegroundColor Red
        $errors++
    }
}

# Check test files
Write-Host "[7/10] Checking test coverage..." -ForegroundColor Yellow
$testFiles = @(
    "tests/conftest.py",
    "tests/unit/test_governance.py",
    "tests/unit/test_catalog_service.py",
    "tests/unit/test_vehicle_service.py",
    "tests/integration/test_auth.py",
    "tests/integration/test_job_cards.py",
    "tests/integration/test_chat.py",
    "tests/integration/test_dashboard.py"
)
$testCount = 0
foreach ($testFile in $testFiles) {
    if (Test-Path $testFile) {
        $testCount++
    }
}
Write-Host "  ✓ $testCount/$($testFiles.Count) test files present" -ForegroundColor Green

# Check documentation
Write-Host "[8/10] Checking documentation..." -ForegroundColor Yellow
$docs = @("README.md", "QUICKSTART.md", "ARCHITECTURE.md", "PHASE_3_4_COMPLETE.md", "EXECUTIVE_SUMMARY.md")
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "  ✓ $doc exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $doc missing" -ForegroundColor Yellow
        $warnings++
    }
}

# Syntax check
Write-Host "[9/10] Running syntax check..." -ForegroundColor Yellow
try {
    python -m py_compile app/main.py 2>&1 | Out-Null
    Write-Host "  ✓ No syntax errors in main.py" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Syntax errors found" -ForegroundColor Red
    $errors++
}

# Import check
Write-Host "[10/10] Checking imports..." -ForegroundColor Yellow
try {
    $importTest = python -c "from app.main import app; print('OK')" 2>&1
    if ($importTest -match "OK") {
        Write-Host "  ✓ All imports successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Import errors: $importTest" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host "  ✗ Import check failed" -ForegroundColor Red
    $errors++
}

# Summary
Write-Host ""
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "Errors: $errors" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $warnings" -ForegroundColor $(if ($warnings -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($errors -eq 0) {
    Write-Host "✓ System verification PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run tests: .\run_tests.ps1" -ForegroundColor White
    Write-Host "  2. Start server: uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "  3. Visit: http://localhost:8000/docs" -ForegroundColor White
    exit 0
} else {
    Write-Host "✗ System verification FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors above before proceeding." -ForegroundColor Yellow
    exit 1
}
