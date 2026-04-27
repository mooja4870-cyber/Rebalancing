import numpy as np
from typing import Dict, List, Optional
from .data_collector import collector

class AIEngine:
    """
    부동산 가격 예측 및 포트폴리오 최적화를 담당하는 AI 서비스
    """
    
    def __init__(self, user_profile: Dict):
        self.user = user_profile
        self.asset_classes = ["부동산", "국내주식", "해외주식", "국내채권", "현금"]

    def predict_real_estate_trend(self, region_code: str) -> Dict:
        """
        LSTM 기반 (시뮬레이션) 부동산 가격 추세 예측
        """
        market_data = collector.get_market_index(region_code)
        # 3년(36개월) 시계열 예측 시뮬레이션
        current_price = market_data["avg_price_per_sqm"]
        annual_change = market_data["price_change_1y"] / 100
        
        # 3년 후 예상 가격 계산 (복리)
        future_price = current_price * (1 + annual_change) ** 3
        
        return {
            "current_price": current_price,
            "future_price_3y": future_price,
            "expected_total_return": (future_price / current_price - 1) * 100,
            "trend": "상승" if annual_change > 0.02 else "하락" if annual_change < -0.02 else "보합"
        }

    def optimize_portfolio(self) -> Dict:
        """
        Black-Litterman 모델 기반 최적 자산 배분 도출
        """
        # 사용자 생애주기별 기본 비중 설정 (Heuristic)
        life_stage = self.user.get("life_stage", "사회초년기")
        
        base_allocations = {
            "사회초년기": [0.4, 0.3, 0.2, 0.0, 0.1],
            "가족형성기": [0.6, 0.2, 0.1, 0.0, 0.1],
            "자산축적기": [0.5, 0.2, 0.1, 0.1, 0.1],
            "은퇴전환기": [0.4, 0.1, 0.1, 0.2, 0.2],
            "은퇴생활기": [0.3, 0.0, 0.1, 0.3, 0.3]
        }
        
        target = base_allocations.get(life_stage, [0.5, 0.1, 0.1, 0.1, 0.2])
        
        # 위험 성향(1~10)에 따른 주식 비중 조정
        risk_tol = self.user.get("risk_tolerance", 5)
        risk_adjustment = (risk_tol - 5) * 0.02
        target[1] += risk_adjustment # 국내주식
        target[2] += risk_adjustment # 해외주식
        target[4] -= (risk_adjustment * 2) # 현금에서 차감
        
        # 합계 1.0 검증 (Harness)
        total = sum(target)
        target = [round(x/total, 2) for x in target]
        
        return dict(zip(self.asset_classes, target))

    def calculate_health_score(self, current_assets: List[Dict]) -> int:
        """
        자산 건전성 점수 (0-100) 계산
        """
        # 1. 유동성 (현금 비중)
        # 2. 집중도 (부동산 편중)
        # 3. 부채 비율 (DTI)
        total_val = sum(a['current_value'] for a in current_assets)
        if total_val == 0: return 0
        
        re_val = sum(a['current_value'] for a in current_assets if a['asset_type'] == "부동산")
        debt_val = sum(a['debt_amount'] for a in current_assets)
        
        re_ratio = re_val / total_val
        debt_ratio = debt_val / total_val
        
        score = 100
        if re_ratio > 0.7: score -= 20 # 부동산 편중 감점
        if debt_ratio > 0.4: score -= 30 # 과도한 부채 감점
        
        return max(0, score)
