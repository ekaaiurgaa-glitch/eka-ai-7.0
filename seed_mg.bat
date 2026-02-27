@echo off
REM EKA-AI v7.0 - Seed MG Engine Data
echo ========================================
echo EKA-AI v7.0 - MG Engine Data Seeding
echo ========================================

set PYTHONPATH=%CD%
python scripts\seed_mg_engine.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] MG Engine data seeded successfully
) else (
    echo.
    echo [ERROR] Seeding failed
)

pause
