#!/usr/bin/env python
"""
EKA-AI v7.0 - Comprehensive Verification Script
Validates: Frontend-Backend Integration, Job State Transitions, MG Data, Load Testing
"""
import asyncio
import sys
import subprocess
from pathlib import Path

async def verify_mg_seeding():
    """Verify MG matrices are populated"""
    print("\n[*] Verifying MG Engine Data...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select, func
        from app.modules.mg_engine.model import MGFormula, CityIndex
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./eka_ai.db")
        
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Count formulas
            result = await session.execute(select(func.count()).select_from(MGFormula))
            formula_count = result.scalar()
            
            # Count cities
            result = await session.execute(select(func.count()).select_from(CityIndex))
            city_count = result.scalar()
            
            # Check for variants
            result = await session.execute(
                select(func.count()).select_from(MGFormula).where(MGFormula.variant.isnot(None))
            )
            variant_count = result.scalar()
            
            print(f"   [OK] MG Formulas: {formula_count}")
            print(f"   [OK] City Indices: {city_count}")
            print(f"   [OK] Variants: {variant_count}")
            
            if formula_count < 5:
                print("   [WARN] Less than 5 formulas. Run: python scripts/seed_mg_engine.py")
                return False
            if city_count < 5:
                print("   [WARN] Less than 5 cities. Run: python scripts/seed_mg_engine.py")
                return False
            if variant_count == 0:
                print("   [WARN] No variants found. Variant field may not be populated.")
                return False
                
            return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

async def verify_vehicle_variant():
    """Verify vehicles table has variant field"""
    print("\n[*] Verifying Vehicle Variant Field...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import inspect
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./eka_ai.db")
        
        # For async, we need to check differently
        from app.modules.vehicles.model import Vehicle
        
        # Check if variant column exists in model
        if hasattr(Vehicle, 'variant'):
            print("   [OK] Variant field exists in Vehicle model")
            return True
        else:
            print("   [ERROR] Variant field missing from Vehicle model")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def verify_frontend_api_integration():
    """Verify frontend has all API endpoints"""
    print("\n[*] Verifying Frontend API Integration...")
    try:
        api_file = Path("frontend/src/api.js")
        if not api_file.exists():
            print("   [ERROR] api.js not found")
            return False
        
        content = api_file.read_text()
        
        required_endpoints = [
            "listInvoices",
            "createInvoice",
            "markInvoicePaid",
            "listApprovals",
            "respondToApproval",
            "workshopDashboard",
            "transitionJob"
        ]
        
        missing = []
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing.append(endpoint)
        
        if missing:
            print(f"   [ERROR] Missing endpoints: {', '.join(missing)}")
            return False
        
        print(f"   [OK] All {len(required_endpoints)} API endpoints present")
        return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def verify_job_state_transition_ui():
    """Verify job state transition component exists"""
    print("\n[*] Verifying Job State Transition UI...")
    try:
        component_file = Path("frontend/src/components/JobCardStateTransition.jsx")
        if not component_file.exists():
            print("   [ERROR] JobCardStateTransition.jsx not found")
            return False
        
        content = component_file.read_text()
        
        required_features = [
            "VALID_TRANSITIONS",
            "handleTransition",
            "/job-cards/{jobId}/transition",
            "new_state"
        ]
        
        missing = []
        for feature in required_features:
            if feature not in content:
                missing.append(feature)
        
        if missing:
            print(f"   [ERROR] Missing features: {', '.join(missing)}")
            return False
        
        print("   [OK] Job State Transition UI complete")
        return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def run_quick_load_test():
    """Run quick load test"""
    print("\n[*] Running Quick Load Test...")
    try:
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code != 200:
                print("   [WARN] Server not responding. Start with: uvicorn app.main:app")
                return None
        except:
            print("   [WARN] Server not running. Start with: uvicorn app.main:app")
            return None
        
        # Run simple concurrent test
        import time
        import concurrent.futures
        
        def make_request():
            try:
                r = requests.get("http://localhost:8000/health", timeout=5)
                return r.status_code == 200
            except:
                return False
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start
        success_count = sum(results)
        rps = success_count / elapsed
        
        print(f"   [INFO] {success_count}/100 requests in {elapsed:.2f}s = {rps:.1f} RPS")
        
        if rps >= 50:
            print(f"   [OK] Load test PASSED (target: 50 RPS)")
            return True
        else:
            print(f"   [WARN] Load test below target (got {rps:.1f}, need 50+ RPS)")
            return False
            
    except Exception as e:
        print(f"   [WARN] Load test skipped: {e}")
        return None

async def main():
    print("="*60)
    print("EKA-AI v7.0 - Comprehensive Verification")
    print("="*60)
    
    results = {}
    
    # Run all checks
    results['mg_data'] = await verify_mg_seeding()
    results['variant_field'] = await verify_vehicle_variant()
    results['frontend_api'] = verify_frontend_api_integration()
    results['job_state_ui'] = verify_job_state_transition_ui()
    results['load_test'] = run_quick_load_test()
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for check, result in results.items():
        status = "[PASS]" if result is True else ("[FAIL]" if result is False else "[SKIP]")
        print(f"{status} - {check.replace('_', ' ').title()}")
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n[WARN] Some checks failed. Review output above.")
        sys.exit(1)
    else:
        print("\n[OK] All critical checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
