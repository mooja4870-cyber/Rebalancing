import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def run_smoke_test():
    print("[1/3] Smoke Test: Checking Service Availability...")
    endpoints = ["/", "/health", "/api/v1/recommendations/sample"]
    for ep in endpoints:
        try:
            res = requests.get(f"{BASE_URL}{ep}")
            if res.status_code == 200:
                print(f"  - {ep}: [PASS]")
            else:
                print(f"  - {ep}: [FAIL] Status {res.status_code}")
                return False
        except Exception as e:
            print(f"  - {ep}: [FAIL] Connection Error: {e}")
            return False
    return True

def run_dry_run_logic():
    print("[2/3] Dry Run: Validating AI Logic (No Side Effects)...")
    # AI 엔진의 핵심 계산 모듈이 정상 범주의 결과를 내는지 가상 유저 데이터로 테스트
    test_user_id = "dry-run-test-id"
    try:
        # 실제 DB 기록 없이 API 호출 결과의 논리적 타당성만 검사
        res = requests.get(f"{BASE_URL}/api/v1/recommendations/{test_user_id}")
        data = res.json()
        if "summary" in data and "health_score" in data:
            score = data["summary"]["health_score"]
            if 0 <= score <= 100:
                print(f"  - AI Engine Score Calculation: [PASS] (Score: {score})")
                return True
        print("  - AI Engine Output Validation: [FAIL]")
        return False
    except Exception as e:
        print(f"  - Dry Run Error: {e}")
        return False

def run_e2e_integration():
    print("[3/3] E2E Test: Full System Integration...")
    try:
        # 1. 유저 생성
        user_res = requests.post(f"{BASE_URL}/api/v1/users/sample")
        user_id = user_res.json()["user_id"]
        print(f"  - Step 1: User Registration: [PASS] (ID: {user_id})")
        
        # 2. 분석 및 추천 데이터 생성
        rec_res = requests.get(f"{BASE_URL}/api/v1/recommendations/{user_id}")
        if rec_res.status_code == 200:
            print("  - Step 2: AI Recommendation Pipeline: [PASS]")
        else:
            print(f"  - Step 2: [FAIL] Status {rec_res.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"  - E2E Error: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("SYSTEM COMPREHENSIVE AUDIT START")
    print("="*50)
    
    s1 = run_smoke_test()
    s2 = run_dry_run_logic()
    s3 = run_e2e_integration()
    
    print("="*50)
    if s1 and s2 and s3:
        print("FINAL RESULT: ALL TESTS PASSED (SUCCESS)")
        sys.exit(0)
    else:
        print("FINAL RESULT: TESTS FAILED (CHECK LOGS)")
        sys.exit(1)
