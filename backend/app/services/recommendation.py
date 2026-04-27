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

    def generate_report(self, current_assets: List[Dict], monthly_income: float = 3500000, monthly_expense: float = 3200000, family_count: int = 1, family_ages: List[int] = None, retirement_goal: str = None) -> Dict:
        """
        Build one report from actual user inputs.
        """
        ai = AIEngine(self.user_profile)
        health_score = ai.calculate_health_score(current_assets)
        total_val = sum(a['current_value'] for a in current_assets)
        total_debt = sum(a.get('debt_amount', 0) for a in current_assets)
        asset_breakdown = self._build_asset_breakdown(current_assets, total_val)
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
                "monthly_cashflow": monthly_income - monthly_expense,
                "family_count": family_count,
                "family_ages": family_ages or [],
                "retirement_goal": retirement_goal,
                "asset_breakdown": asset_breakdown
            },
            "analysis_report": self._build_analysis_report(
                health_score,
                total_val,
                total_debt,
                monthly_income,
                monthly_expense,
                family_count,
                family_ages or [],
                retirement_goal,
                asset_breakdown
            ),
            "recommendation": {
                "target_allocation": target_allocation,
                "action_plan": action_plan
            },
            "simulation": sim_results
        }

    def _is_real_estate(self, asset_type: str) -> bool:
        return asset_type in ["real_estate", "부동산"]

    def _build_asset_breakdown(self, current: List[Dict], total: float) -> Dict:
        labels = {
            "real_estate": "부동산",
            "deposit": "예금",
            "stock": "주식",
            "gold_silver": "금/은",
            "pension": "연금",
            "crypto_asset": "가상자산",
            "finance": "금융자산",
            "cash": "현금"
        }
        breakdown = {}
        for asset in current:
            key = asset.get("asset_type", "etc")
            label = labels.get(key, key)
            value = asset.get("current_value", 0)
            if label not in breakdown:
                breakdown[label] = {"value": 0, "ratio": 0}
            breakdown[label]["value"] += value

        for label in breakdown:
            breakdown[label]["ratio"] = round(breakdown[label]["value"] / total * 100, 1) if total else 0
        return breakdown

    def _fmt_number(self, value: float) -> str:
        return f"{value:,.1f}"

    def _fmt_won(self, value: float) -> str:
        return f"{self._fmt_number(value)}원"

    def _build_analysis_report(self, score: int, total: float, debt: float, monthly_income: float, monthly_expense: float, family_count: int, family_ages: List[int], retirement_goal: str, asset_breakdown: Dict) -> Dict:
        cashflow = monthly_income - monthly_expense
        debt_ratio = debt / total if total else 0
        largest_asset = max(asset_breakdown.items(), key=lambda item: item[1]["value"])[0] if asset_breakdown else "없음"
        family_note = f"{family_count}명 가족"
        if family_ages:
            family_note += f" / 나이 {', '.join(str(age) for age in family_ages)}"

        risk_flags = []
        if debt_ratio > 0.4:
            risk_flags.append("대출 비중이 높습니다.")
        if cashflow < 0:
            risk_flags.append("월 지출이 월수입보다 큽니다.")
        if asset_breakdown.get("부동산", {}).get("ratio", 0) > 70:
            risk_flags.append("부동산 집중도가 높습니다.")
        if not risk_flags:
            risk_flags.append("현재 입력 기준의 핵심 위험은 관리 가능한 수준입니다.")

        return {
            "headline": "입력한 자산/수입/지출 기준 맞춤 분석보고서",
            "status": "주의" if score < 70 else "양호",
            "asset_comment": f"총자산은 {self._fmt_won(total)}이며, 가장 큰 비중은 {largest_asset}입니다.",
            "cashflow_comment": f"월수입 {self._fmt_won(monthly_income)}, 월지출 {self._fmt_won(monthly_expense)}, 월 현금흐름 {self._fmt_won(cashflow)}입니다.",
            "debt_comment": f"대출잔액은 {self._fmt_won(debt)}이고 총자산 대비 {self._fmt_number(debt_ratio*100)}%입니다.",
            "family_comment": family_note,
            "retirement_goal_comment": retirement_goal or "은퇴목표가 입력되지 않았습니다.",
            "risk_flags": risk_flags
        }

    def _create_action_plan(self, current: List[Dict], target: Dict, total: float, monthly_income: float, monthly_expense: float) -> List[str]:
        plan = []
        if total <= 0:
            return ["Enter at least one asset before analysis."]

        current_re = sum(a['current_value'] for a in current if self._is_real_estate(a['asset_type'])) / total
        if current_re > target["real_estate"]:
            excess = (current_re - target["real_estate"]) * total
            plan.append(f"Reduce real estate concentration by about {self._fmt_won(excess)} over time.")
        
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
