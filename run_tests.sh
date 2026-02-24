#!/bin/bash
# EKA-AI v7.0 Test Runner
# Runs all tests with coverage reporting

echo -e "\033[36mEKA-AI v7.0 - Running Test Suite\033[0m"
echo -e "\033[36m=================================\033[0m"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "\033[31mERROR: pytest not found. Installing test dependencies...\033[0m"
    pip install pytest pytest-asyncio pytest-cov httpx
fi

echo -e "\033[33mRunning tests with coverage...\033[0m"
pytest -v --cov=app --cov-report=term-missing --cov-report=html

if [ $? -eq 0 ]; then
    echo ""
    echo -e "\033[32m✓ All tests passed!\033[0m"
    echo ""
    echo -e "\033[36mCoverage report generated in htmlcov/index.html\033[0m"
else
    echo ""
    echo -e "\033[31m✗ Some tests failed. Check output above.\033[0m"
    exit 1
fi
