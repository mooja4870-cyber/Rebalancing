import sqlite3
import uuid
import random
from datetime import date

def seed_advanced_data():
    conn = sqlite3.connect('asset_balance.db')
    cursor = conn.cursor()

    print("📊 보충 작업 1: 금융상품 100종 적재 중...")
    categories = ["예금", "적금", "채권", "국내주식", "해외주식", "ETF", "연금"]
    providers = ["신한은행", "국민은행", "미래에셋증권", "삼성증권", "한국투자증권"]
    
    for i in range(100):
        cursor.execute("""
            INSERT INTO financial_products (product_id, product_name, category, provider, risk_level, expected_return, is_tax_benefit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            f"자산균형_{random.choice(categories)}_{i+1}호",
            random.choice(categories),
            random.choice(providers),
            random.randint(1, 10),
            round(random.uniform(2.0, 15.0), 2),
            random.choice([True, False])
        ))

    print("🗺️ 보충 작업 2: 전국 250개 시군구 마스터 데이터 확장 중...")
    # 실제 법정동 코드 체계를 모사한 대량 데이터 적재
    for code_prefix in range(11, 51): # 전국 시도 코드 시뮬레이션
        for sub_code in range(100, 110): # 시군구 코드 시뮬레이션
            region_code = f"{code_prefix}{sub_code}000000"
            cursor.execute("INSERT OR IGNORE INTO region_master (region_code, region_name, level) VALUES (?, ?, ?)",
                         (region_code, f"가상지역_{region_code}", 2))
            
            # 지역 특성 매칭
            cursor.execute("INSERT OR IGNORE INTO region_characteristics (region_code, category, development_stage, infrastructure_score, growth_potential, investment_recommendation) VALUES (?, ?, ?, ?, ?, ?)",
                         (region_code, "주거중심", "성숙기", random.randint(60, 95), random.randint(40, 90), "중립"))

    conn.commit()
    conn.close()
    print("✅ 데이터 보충 완료!")

if __name__ == "__main__":
    seed_advanced_data()
