import numpy as np
from typing import Dict

class RetirementSimulator:
    """
    Monte Carlo simulator for long-term asset survival probability.
    """
    
    def __init__(self, initial_assets: float, monthly_income: float, monthly_expense: float):
        self.initial_assets = initial_assets
        self.monthly_income = monthly_income
        self.monthly_expense = monthly_expense
        self.years = 30
        self.sim_count = 5000

    def run_simulation(self, portfolio_weights: Dict[str, float]) -> Dict:
        """
        Run 5,000 simulations and return survival and final asset distribution.
        """
        returns_map = {
            "real_estate": 0.045,
            "domestic_stock": 0.07,
            "global_stock": 0.09,
            "bond": 0.035,
            "cash": 0.02
        }
        vol_map = {
            "real_estate": 0.15,
            "domestic_stock": 0.25,
            "global_stock": 0.22,
            "bond": 0.05,
            "cash": 0.01
        }
        
        p_return = sum(weight * returns_map.get(asset, 0.02) for asset, weight in portfolio_weights.items())
        p_vol = np.sqrt(sum((weight * vol_map.get(asset, 0.01)) ** 2 for asset, weight in portfolio_weights.items()))
        m_return = p_return / 12
        m_vol = p_vol / np.sqrt(12)
        
        results = []
        survival_count = 0
        
        for _ in range(self.sim_count):
            balance = self.initial_assets
            failed = False
            
            for _ in range(self.years * 12):
                current_ret = np.random.normal(m_return, m_vol)
                balance = balance * (1 + current_ret) + (self.monthly_income - self.monthly_expense)
                
                if balance <= 0:
                    balance = 0
                    failed = True
                    break
                
            if not failed:
                survival_count += 1
            results.append(balance)
            
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
