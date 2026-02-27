#!/usr/bin/env pwsh
# EKA-AI v7.0 - Complete Setup & Verification

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EKA-AI v7.0 - Setup & Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Seed MG Engine Data
Write-Host "`n[1/4] Seeding MG Engine Data..." -ForegroundColor Yellow
python scripts/seed_mg_engine.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: MG seeding had issues" -ForegroundColor Yellow
}

# 2. Run Database Migrations
Write-Host "`n[2/4] Running Database Migrations..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Migration failed" -ForegroundColor Red
    exit 1
}

# 3. Run Verification
Write-Host "`n[3/4] Running Verification Checks..." -ForegroundColor Yellow
python scripts/verify_requirements.py
$verifyResult = $LASTEXITCODE

# 4. Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($verifyResult -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Start backend: uvicorn app.main:app --reload --port 8000" -ForegroundColor White
    Write-Host "  2. Start frontend: cd frontend && npm run dev" -ForegroundColor White
    Write-Host "  3. Access: http://localhost:3000" -ForegroundColor White
} else {
    Write-Host "⚠️  Some checks failed. Review output above." -ForegroundColor Yellow
}

exit $verifyResult
