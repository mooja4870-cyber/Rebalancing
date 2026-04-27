from typing import Dict, List
from .ai_engine import AIEngine
from .simulator import RetirementSimulator

class RebalancingEngine:
    """
    Orchestrates diagnosis, allocation, simulation, and action plan generation.
    """
    
    def __init__(self, user_id: str, db_session, user_profile: Dict = None):
        self.user_id = user_id
        self.db = db_session
        self.user_profile = user_profile or {
            "life_stage": "retirement_transition",
            "risk_tolerance": 4,
            "region_code": "1168000000"
        }

    def generate_report(self, current_assets: List[Dict], monthly_income: float = 3500000, monthly_expense: float = 3200000) -> Dict:
        """
        Build one report from actual user inputs.
        """
        ai = AIEngine(self.user_profile)
        health_score = ai.calculate_health_score(current_assets)
        total_val = sum(a['current_value'] for a in current_assets)
        total_debt = sum(a.get('debt_amount', 0) for a in current_assets)
        market_trend = ai.predict_real_estate_trend(self.user_profile["region_code"])
        target_allocation = ai.optimize_portfolio()
        sim = RetirementSimulator(total_val, monthly_income, monthly_expense)
        sim_results = sim.run_simulation(target_allocation)
        action_plan = self._create_action_plan(current_assets, target_allocation, total_val, monthly_income, monthly_expense)
        
        return {
            "summary": {
                "health_score": health_score,
                "total_assets": total_val,
                "total_debt": total_debt,
                "debt_ratio": round(total_debt / total_val, 4) if total_val else 0,
                "market_view": market_trend["trend"],
                "monthly_income": monthly_income,
                "monthly_expense": monthly_expense,
                "monthly_cashflow": monthly_income - monthly_expense
            },
            "recommendation": {
                "target_allocation": target_allocation,
                "action_plan": action_plan
            },
            "simulation": sim_results
        }

    def _is_real_estate(self, asset_type: str) -> bool:
        return asset_type in ["real_estate", "부동산", "遺?숈궛"]

    def _create_action_plan(self, current: List[Dict], target: Dict, total: float, monthly_income: float, monthly_expense: float) -> List[str]:
        plan = []
        if total <= 0:
            return ["Enter at least one asset before analysis."]

        current_re = sum(a['current_value'] for a in current if self._is_real_estate(a['asset_type'])) / total
        if current_re > target["real_estate"]:
            excess = (current_re - target["real_estate"]) * total
            plan.append(f"Reduce real estate concentration by about {excess/100000000:.1f}eok KRW over time.")
        
        high_interest_debts = [a for a in current if a.get('debt_interest_rate', 0) > 5.0]
        if high_interest_debts:
            plan.append("Prioritize repayment or refinancing for loans above 5% interest.")

        if monthly_income < monthly_expense:
            plan.append("Monthly cashflow is negative. Cut expenses or secure income before adding risk assets.")
        elif monthly_income - monthly_expense > 0:
            plan.append("Use positive monthly cashflow for debt reduction and phased portfolio rebalancing.")

        if not plan:
            plan.append("Current balance is acceptable. Keep monitoring debt ratio and liquidity.")
            
        return plan
