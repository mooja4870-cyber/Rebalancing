from typing import Dict, List
from .data_collector import collector

class AIEngine:
    """
    Portfolio diagnosis and target allocation engine.
    """
    
    def __init__(self, user_profile: Dict):
        self.user = user_profile
        self.asset_classes = ["real_estate", "domestic_stock", "global_stock", "bond", "cash"]

    def predict_real_estate_trend(self, region_code: str) -> Dict:
        """
        Simulated real estate trend forecast.
        """
        market_data = collector.get_market_index(region_code)
        current_price = market_data["avg_price_per_sqm"]
        annual_change = market_data["price_change_1y"] / 100
        future_price = current_price * (1 + annual_change) ** 3
        
        return {
            "current_price": current_price,
            "future_price_3y": future_price,
            "expected_total_return": (future_price / current_price - 1) * 100,
            "trend": "up" if annual_change > 0.02 else "down" if annual_change < -0.02 else "flat"
        }

    def optimize_portfolio(self) -> Dict:
        """
        Heuristic target allocation by life stage and risk tolerance.
        """
        life_stage = self.user.get("life_stage", "asset_accumulation")
        
        base_allocations = {
            "early_career": [0.4, 0.3, 0.2, 0.0, 0.1],
            "family_growth": [0.6, 0.2, 0.1, 0.0, 0.1],
            "asset_accumulation": [0.5, 0.2, 0.1, 0.1, 0.1],
            "retirement_transition": [0.4, 0.1, 0.1, 0.2, 0.2],
            "retirement": [0.3, 0.0, 0.1, 0.3, 0.3]
        }
        
        target = list(base_allocations.get(life_stage, [0.5, 0.1, 0.1, 0.1, 0.2]))
        risk_tol = self.user.get("risk_tolerance", 5)
        risk_adjustment = (risk_tol - 5) * 0.02
        target[1] += risk_adjustment
        target[2] += risk_adjustment
        target[4] -= (risk_adjustment * 2)
        
        target = [max(0, x) for x in target]
        total = sum(target) or 1
        target = [round(x / total, 2) for x in target]
        
        return dict(zip(self.asset_classes, target))

    def calculate_health_score(self, current_assets: List[Dict]) -> int:
        """
        Asset health score from concentration and debt ratio.
        """
        total_val = sum(a['current_value'] for a in current_assets)
        if total_val == 0:
            return 0
        
        re_val = sum(a['current_value'] for a in current_assets if a['asset_type'] in ["real_estate", "부동산", "遺?숈궛"])
        debt_val = sum(a.get('debt_amount', 0) for a in current_assets)
        
        re_ratio = re_val / total_val
        debt_ratio = debt_val / total_val
        
        score = 100
        if re_ratio > 0.7:
            score -= 20
        if debt_ratio > 0.4:
            score -= 30
        if debt_ratio > 0.6:
            score -= 15
        
        return max(0, score)
