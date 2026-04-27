import requests
import sys

BASE_URL = "http://localhost:8000"

def run_smoke_test():
    print("[1/4] Smoke Test: Checking Service Availability...")
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
    print("[2/4] Dry Run: Validating AI Logic (No Side Effects)...")
    test_user_id = "dry-run-test-id"
    try:
        res = requests.get(f"{BASE_URL}/api/v1/recommendations/{test_user_id}")
        data = res.json()
        summary = data.get("summary", {})
        score = summary.get("health_score")
        if score is not None and 0 <= score <= 100:
            print(f"  - AI Engine Score Calculation: [PASS] (Score: {score})")
            return True
        print("  - AI Engine Output Validation: [FAIL]")
        return False
    except Exception as e:
        print(f"  - Dry Run Error: {e}")
        return False

def run_e2e_integration():
    print("[3/4] E2E Test: Full System Integration...")
    try:
        user_res = requests.post(f"{BASE_URL}/api/v1/users/sample")
        user_id = user_res.json()["user_id"]
        print(f"  - Step 1: User Registration: [PASS] (ID: {user_id})")
        
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

def run_input_analysis_flow():
    print("[4/4] Input Flow: Saving user assets and running personalized analysis...")
    payload = {
        "name": "Harness User",
        "age": 60,
        "gender": "male",
        "residence_region": "강남구",
        "job_category": "retired",
        "annual_income": 48000000,
        "monthly_income": 4000000,
        "monthly_expense": 3200000,
        "loan_balance": 300000000,
        "monthly_loan_interest": 1125000,
        "family_count": 3,
        "family_ages": [60, 58, 28],
        "real_estate_type": "apartment",
        "real_estate_count": 1,
        "real_estate_market_value": 1600000000,
        "short_term_goal": "reduce interest burden",
        "mid_term_goal": "rebalance assets",
        "long_term_goal": "stable retirement income",
        "retirement_goal": "monthly cashflow 4m KRW",
        "risk_tolerance": 5,
        "financial_goal": "retirement cashflow",
        "assets": [
            {
                "asset_type": "real_estate",
                "asset_name": "apartment",
                "current_value": 1600000000
            },
            {
                "asset_type": "deposit",
                "asset_name": "deposit",
                "current_value": 120000000
            },
            {
                "asset_type": "stock",
                "asset_name": "stock",
                "current_value": 60000000
            },
            {
                "asset_type": "gold_silver",
                "asset_name": "gold and silver",
                "current_value": 20000000
            },
            {
                "asset_type": "crypto_asset",
                "asset_name": "crypto asset",
                "current_value": 180000000
            }
        ]
    }
    try:
        res = requests.post(f"{BASE_URL}/api/v1/users/analysis-input", json=payload)
        if res.status_code != 200:
            print(f"  - Input Analysis API: [FAIL] Status {res.status_code}")
            return False

        data = res.json()
        summary = data.get("summary", {})
        if data.get("source") != "user_input":
            print("  - Input Analysis Source: [FAIL]")
            return False
        if summary.get("monthly_income") != payload["monthly_income"]:
            print("  - Monthly Income Binding: [FAIL]")
            return False
        if summary.get("total_debt") != 300000000:
            print("  - Debt Binding: [FAIL]")
            return False
        if summary.get("family_count") != payload["family_count"]:
            print("  - Family Binding: [FAIL]")
            return False
        if summary.get("retirement_goal") != payload["retirement_goal"]:
            print("  - Retirement Goal Binding: [FAIL]")
            return False
        if "analysis_report" not in data:
            print("  - Analysis Report: [FAIL]")
            return False
        if "life_stage_profile" not in data:
            print("  - Life Stage Profile: [FAIL]")
            return False
        if "region_analysis" not in data:
            print("  - Region Mapping: [FAIL]")
            return False
        if "pipeline" not in data or "지역 특성 매핑" not in data["pipeline"]:
            print("  - Cogui Pipeline: [FAIL]")
            return False
        if "simulation" not in data:
            print("  - Simulation Result: [FAIL]")
            return False

        print("  - Personalized Input Pipeline: [PASS]")
        return True
    except Exception as e:
        print(f"  - Input Flow Error: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("SYSTEM COMPREHENSIVE AUDIT START")
    print("="*50)
    
    s1 = run_smoke_test()
    s2 = run_dry_run_logic()
    s3 = run_e2e_integration()
    s4 = run_input_analysis_flow()
    
    print("="*50)
    if s1 and s2 and s3 and s4:
        print("FINAL RESULT: ALL TESTS PASSED (SUCCESS)")
        sys.exit(0)
    else:
        print("FINAL RESULT: TESTS FAILED (CHECK LOGS)")
        sys.exit(1)
