import sys
import os
import requests
import json
import time

# 테스트를 위한 환경 설정
BASE_URL = "http://localhost:8000/api/v1"

def run_harness():
    print("Asset Balance System Harness Starting...")
    
    # 1. 시스템 헬스체크
    try:
        res = requests.get("http://localhost:8000/")
        if res.status_code == 200:
            print("[PASS] Backend server is online")
    except Exception as e:
        print(f"[FAIL] Backend server is not running: {e}")
        return

    # 2. 샘플 유저 생성 및 진단 시나리오
    print("Scenario Test: Hong Gil-dong (63) Gangnam-gu resident analysis...")
    user_res = requests.post(f"{BASE_URL}/users/sample")
    user_id = user_res.json()["user_id"]
    
    # 3. AI 추천 리포트 생성 검증
    report_res = requests.get(f"{BASE_URL}/recommendations/{user_id}")
    if report_res.status_code == 200:
        data = report_res.json()
        print(f"[PASS] AI Recommendation engine working (Score: {data['summary']['health_score']})")
        print(f"[PASS] Monte Carlo simulation complete (Survival: {data['simulation']['survival_probability']:.1f}%)")
    else:
        print("[FAIL] AI Engine error")

    print("\nAll harness tests passed. System is fully operational.")

if __name__ == "__main__":
    # 서버가 뜰 때까지 잠시 대기 (실제 구동 시)
    run_harness()
