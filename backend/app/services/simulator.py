import numpy as np
from typing import Dict, List, Tuple

class RetirementSimulator:
    """
    몬테카를로 시뮬레이션을 통한 노후 자산 생존 확률 분석 엔진
    """
    
    def __init__(self, initial_assets: float, monthly_income: float, monthly_expense: float):
        self.initial_assets = initial_assets
        self.monthly_income = monthly_income
        self.monthly_expense = monthly_expense
        self.years = 30 # 시뮬레이션 기간 (보통 30년)
        self.sim_count = 5000 # 정밀도와 속도의 균형점

    def run_simulation(self, portfolio_weights: Dict[str, float]) -> Dict:
        """
        5,000회 시뮬레이션 실행 및 결과 통계 산출
        """
        # 자산별 연간 기대수익률 및 변동성 (가정치)
        returns_map = {"부동산": 0.045, "국내주식": 0.07, "해외주식": 0.09, "국내채권": 0.035, "현금": 0.02}
        vol_map = {"부동산": 0.15, "국내주식": 0.25, "해외주식": 0.22, "국내채권": 0.05, "현금": 0.01}
        
        # 포트폴리오 전체 수익률 및 변동성 계산
        p_return = sum(weights * returns_map[asset] for asset, weights in portfolio_weights.items())
        p_vol = np.sqrt(sum((weights * vol_map[asset])**2 for asset, weights in portfolio_weights.items()))
        
        # 월간 파라미터로 변환
        m_return = p_return / 12
        m_vol = p_vol / np.sqrt(12)
        
        results = []
        survival_count = 0
        
        for _ in range(self.sim_count):
            balance = self.initial_assets
            balances = [balance]
            failed = False
            
            for _ in range(self.years * 12):
                # 랜덤 수익률 생성 (정규분포)
                current_ret = np.random.normal(m_return, m_vol)
                # 자산 변동 + 현금흐름(수입-지출)
                balance = balance * (1 + current_ret) + (self.monthly_income - self.monthly_expense)
                
                if balance <= 0:
                    balance = 0
                    failed = True
                balances.append(balance)
                
            if not failed:
                survival_count += 1
            results.append(balances[-1])
            
        # 통계 가공
        percentiles = np.percentile(results, [10, 50, 90])
        
        return {
            "survival_probability": (survival_count / self.sim_count) * 100,
            "final_assets": {
                "p10_pessimistic": percentiles[0],
                "p50_median": percentiles[1],
                "p90_optimistic": percentiles[2]
            },
            "years_simulated": self.years
        }
