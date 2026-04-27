from typing import Dict, List
from .ai_engine import AIEngine
from .simulator import RetirementSimulator
from .data_collector import collector

class RebalancingEngine:
    """
    모든 AI 서비스를 통합하여 최종 액션 플랜을 도출하는 오케스트레이터
    """
    
    def __init__(self, user_id: str, db_session):
        self.user_id = user_id
        self.db = db_session
        # 실제 환경에서는 DB에서 유저 프로필과 자산을 가져옴
        # 여기서는 시뮬레이션을 위해 가상 데이터를 생성
        self.user_profile = {
            "life_stage": "은퇴전환기",
            "risk_tolerance": 4,
            "region_code": "1168000000" # 강남구
        }

    def generate_report(self, current_assets: List[Dict]) -> Dict:
        """
        종합 진단, 최적화 추천, 시뮬레이션, 액션 플랜 통합 생성
        """
        ai = AIEngine(self.user_profile)
        
        # 1. 현재 상태 진단
        health_score = ai.calculate_health_score(current_assets)
        total_val = sum(a['current_value'] for a in current_assets)
        
        # 2. 지역 시장 분석
        market_trend = ai.predict_real_estate_trend(self.user_profile["region_code"])
        
        # 3. 최적 포트폴리오 도출
        target_allocation = ai.optimize_portfolio()
        
        # 4. 시뮬레이션 실행
        # 수입/지출은 간소화를 위해 고정값 사용 (실제론 DB 연동)
        sim = RetirementSimulator(total_val, 3500000, 3200000)
        sim_results = sim.run_simulation(target_allocation)
        
        # 5. 구체적 액션 플랜 생성 (핵심 지능)
        action_plan = self._create_action_plan(current_assets, target_allocation, total_val)
        
        return {
            "summary": {
                "health_score": health_score,
                "total_assets": total_val,
                "market_view": market_trend["trend"]
            },
            "recommendation": {
                "target_allocation": target_allocation,
                "action_plan": action_plan
            },
            "simulation": sim_results
        }

    def _create_action_plan(self, current: List[Dict], target: Dict, total: float) -> List[str]:
        plan = []
        # 부동산 매도 여부 판단
        current_re = sum(a['current_value'] for a in current if a['asset_type'] == "부동산") / total
        if current_re > target["부동산"]:
            excess = (current_re - target["부동산"]) * total
            plan.append(f"🏠 부동산 비중이 높습니다. 약 {excess/100000000:.1f}억원을 현금화하여 자산을 분산하세요.")
        
        # 금융 자산 매수 추천
        if target["국내주식"] > 0.1:
            plan.append(f"📈 저평가된 우량주 또는 인덱스 펀드 비중을 {target['국내주식']*100:.0f}%까지 확대하세요.")
            
        # 부채 관리
        high_interest_debts = [a for a in current if a.get('debt_interest_rate', 0) > 5.0]
        if high_interest_debts:
            plan.append("⚠️ 5% 이상의 고금리 대출을 우선 상환하거나 저금리 대환 상품으로 전환하세요.")
            
        return plan
