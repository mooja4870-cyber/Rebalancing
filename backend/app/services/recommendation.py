from typing import Dict, List
from .ai_engine import AIEngine
from .simulator import RetirementSimulator

LIFE_STAGE_PROFILES = {
    "early_career": {"label": "사회초년기", "age": "20-34", "income": "중하", "asset": "소액", "goal": "자산형성"},
    "family_growth": {"label": "가족형성기", "age": "35-44", "income": "중상", "asset": "주택구입", "goal": "교육/주거"},
    "asset_accumulation": {"label": "자산축적기", "age": "45-54", "income": "고", "asset": "다변화", "goal": "은퇴준비"},
    "retirement_transition": {"label": "은퇴전환기", "age": "55-64", "income": "감소", "asset": "현금화", "goal": "안정적 인컴"},
    "retirement": {"label": "은퇴생활기", "age": "65+", "income": "연금의존", "asset": "보존", "goal": "물가헷지"}
}

REGION_CHARACTERISTICS = {
    "강남구": {
        "real_estate_profile": "고가주택밀집, 전세가율낮음",
        "rental_yield": 2.5,
        "population_growth": -0.5,
        "main_industry": "금융/IT",
        "strategy": "다운사이징 → 분산투자"
    },
    "대구 수성구": {
        "real_estate_profile": "학군중심, 안정적수요",
        "rental_yield": 4.2,
        "population_growth": -1.2,
        "main_industry": "교육/의료",
        "strategy": "소형평형 임대유지"
    },
    "대구_수성구": {
        "real_estate_profile": "학군중심, 안정적수요",
        "rental_yield": 4.2,
        "population_growth": -1.2,
        "main_industry": "교육/의료",
        "strategy": "소형평형 임대유지"
    },
    "세종시": {
        "real_estate_profile": "신도시, 공급과잉우려",
        "rental_yield": 3.8,
        "population_growth": 2.5,
        "main_industry": "공공기관",
        "strategy": "중장기 보유 후 매각"
    }
}

class RebalancingEngine:
    """
    Orchestrates cogui flow:
    user input -> region mapping -> life-stage analysis -> market data -> AI recommendation -> personalized report.
    """
    
    def __init__(self, user_id: str, db_session, user_profile: Dict = None):
        self.user_id = user_id
        self.db = db_session
        self.user_profile = user_profile or {
            "life_stage": "retirement_transition",
            "risk_tolerance": 4,
            "region_code": "1168000000"
        }

    def generate_report(self, current_assets: List[Dict], monthly_income: float = 3500000, monthly_expense: float = 3200000, family_count: int = 1, family_ages: List[int] = None, retirement_goal: str = None, profile_context: Dict = None) -> Dict:
        profile_context = profile_context or {}
        family_ages = family_ages or []
        ai = AIEngine(self.user_profile)
        total_val = sum(a['current_value'] for a in current_assets)
        total_debt = sum(a.get('debt_amount', 0) for a in current_assets)
        asset_breakdown = self._build_asset_breakdown(current_assets, total_val)
        monthly_loan_interest = profile_context.get("monthly_loan_interest", self._extract_monthly_loan_interest(current_assets))
        net_cashflow = monthly_income - monthly_expense - monthly_loan_interest
        life_stage = self.user_profile.get("life_stage", "retirement_transition")
        life_profile = LIFE_STAGE_PROFILES.get(life_stage, LIFE_STAGE_PROFILES["retirement_transition"])
        region_name = profile_context.get("residence_region", "강남구")
        region_analysis = self._build_region_analysis(region_name)
        market_trend = ai.predict_real_estate_trend(self.user_profile["region_code"])
        target_allocation = ai.optimize_portfolio()
        health_score = self._calculate_cogui_score(asset_breakdown, total_debt, total_val, net_cashflow)
        status = self._status_from_score(health_score)
        sim = RetirementSimulator(total_val, monthly_income, monthly_expense + monthly_loan_interest)
        sim_results = sim.run_simulation(target_allocation)
        action_plan = self._create_action_plan(current_assets, target_allocation, total_val, monthly_income, monthly_expense, monthly_loan_interest, region_analysis, life_profile)
        
        return {
            "pipeline": ["사용자 입력", "지역 특성 매핑", "생애주기 분석", "실시간 시장 데이터", "AI 추천 엔진", "개인화 리포트"],
            "summary": {
                "health_score": health_score,
                "status": status,
                "total_assets": total_val,
                "total_debt": total_debt,
                "debt_ratio": round(total_debt / total_val, 4) if total_val else 0,
                "market_view": market_trend["trend"],
                "monthly_income": monthly_income,
                "monthly_expense": monthly_expense,
                "monthly_loan_interest": monthly_loan_interest,
                "monthly_cashflow": monthly_income - monthly_expense,
                "net_monthly_cashflow": net_cashflow,
                "family_count": family_count,
                "family_ages": family_ages,
                "retirement_goal": retirement_goal,
                "asset_breakdown": asset_breakdown
            },
            "smart_diagnosis": {
                "basic_info": {
                    "age": profile_context.get("age"),
                    "gender": profile_context.get("gender"),
                    "residence_region": region_name,
                    "job_category": profile_context.get("job_category"),
                    "annual_income": profile_context.get("annual_income"),
                    "family_count": family_count,
                    "family_ages": family_ages
                },
                "real_estate": {
                    "type": profile_context.get("real_estate_type"),
                    "count": profile_context.get("real_estate_count"),
                    "market_value": profile_context.get("real_estate_market_value"),
                    "loan_balance": total_debt,
                    "monthly_loan_interest": monthly_loan_interest
                },
                "financial_assets": asset_breakdown,
                "financial_goals": {
                    "short_term": profile_context.get("short_term_goal"),
                    "mid_term": profile_context.get("mid_term_goal"),
                    "long_term": profile_context.get("long_term_goal"),
                    "retirement": retirement_goal
                }
            },
            "life_stage_profile": life_profile,
            "region_analysis": region_analysis,
            "market_data": {
                "source_status": "실시간 API 연동 전: 교체 가능한 시장데이터 인터페이스",
                "region_code": self.user_profile["region_code"],
                "current_price": market_trend.get("current_price"),
                "future_price_3y": market_trend.get("future_price_3y"),
                "expected_total_return": market_trend.get("expected_total_return"),
                "trend": market_trend.get("trend")
            },
            "analysis_report": self._build_analysis_report(
                health_score,
                status,
                total_val,
                total_debt,
                monthly_income,
                monthly_expense,
                monthly_loan_interest,
                family_count,
                family_ages,
                retirement_goal,
                asset_breakdown,
                life_profile,
                region_analysis
            ),
            "recommendation": {
                "target_allocation": target_allocation,
                "action_plan": action_plan
            },
            "simulation": sim_results
        }

    def _label_for_asset(self, asset_type: str) -> str:
        labels = {
            "real_estate": "부동산",
            "deposit": "예금",
            "installment_savings": "적금",
            "stock": "주식",
            "fund": "펀드",
            "gold_silver": "금/은",
            "pension_insurance": "연금/보험",
            "crypto_asset": "가상자산",
            "other_assets": "기타",
            "finance": "금융자산",
            "cash": "현금"
        }
        return labels.get(asset_type, asset_type)

    def _is_real_estate(self, asset_type: str) -> bool:
        return asset_type in ["real_estate", "부동산"]

    def _build_asset_breakdown(self, current: List[Dict], total: float) -> Dict:
        breakdown = {}
        for asset in current:
            label = self._label_for_asset(asset.get("asset_type", "etc"))
            value = asset.get("current_value", 0)
            if label not in breakdown:
                breakdown[label] = {"value": 0, "ratio": 0}
            breakdown[label]["value"] += value

        for label in breakdown:
            breakdown[label]["ratio"] = round(breakdown[label]["value"] / total * 100, 1) if total else 0
        return breakdown

    def _build_region_analysis(self, region_name: str) -> Dict:
        region = REGION_CHARACTERISTICS.get(region_name, REGION_CHARACTERISTICS["강남구"])
        return {
            "region_name": region_name if region_name in REGION_CHARACTERISTICS else "강남구",
            **region
        }

    def _extract_monthly_loan_interest(self, current: List[Dict]) -> float:
        return sum(a.get("monthly_loan_interest", 0) or a.get("debt_interest_rate", 0) or 0 for a in current if a.get("debt_amount", 0) > 0)

    def _calculate_cogui_score(self, asset_breakdown: Dict, total_debt: float, total: float, net_cashflow: float) -> int:
        real_estate_ratio = asset_breakdown.get("부동산", {}).get("ratio", 0)
        debt_ratio = total_debt / total if total else 0
        score = 100
        if real_estate_ratio > 90:
            score -= 35
        elif real_estate_ratio > 70:
            score -= 25
        if debt_ratio > 0.4:
            score -= 25
        elif debt_ratio > 0.2:
            score -= 10
        if net_cashflow < 0:
            score -= 20
        return max(0, min(100, score))

    def _status_from_score(self, score: int) -> str:
        if score < 60:
            return "위험"
        if score < 80:
            return "주의"
        return "양호"

    def _fmt_number(self, value: float) -> str:
        return f"{value:,.1f}"

    def _fmt_won(self, value: float) -> str:
        return f"{self._fmt_number(value)}원"

    def _build_analysis_report(self, score: int, status: str, total: float, debt: float, monthly_income: float, monthly_expense: float, monthly_loan_interest: float, family_count: int, family_ages: List[int], retirement_goal: str, asset_breakdown: Dict, life_profile: Dict, region_analysis: Dict) -> Dict:
        gross_cashflow = monthly_income - monthly_expense
        net_cashflow = gross_cashflow - monthly_loan_interest
        debt_ratio = debt / total if total else 0
        largest_asset = max(asset_breakdown.items(), key=lambda item: item[1]["value"])[0] if asset_breakdown else "없음"
        family_note = f"{family_count}명 가족"
        if family_ages:
            family_note += f" / 나이 {', '.join(str(age) for age in family_ages)}"

        risk_flags = []
        if debt_ratio > 0.4:
            risk_flags.append("대출 비중이 높습니다.")
        if net_cashflow < 0:
            risk_flags.append("월 대출이자를 반영하면 순현금흐름이 마이너스입니다.")
        if asset_breakdown.get("부동산", {}).get("ratio", 0) > 70:
            risk_flags.append("부동산 집중도가 높습니다.")
        if not risk_flags:
            risk_flags.append("현재 입력 기준의 핵심 위험은 관리 가능한 수준입니다.")

        return {
            "headline": "cogui 기준 개인화 리밸런싱 분석보고서",
            "status": status,
            "asset_comment": f"총자산은 {self._fmt_won(total)}이며, 가장 큰 비중은 {largest_asset}입니다.",
            "cashflow_comment": f"월수입 {self._fmt_won(monthly_income)}, 월지출 {self._fmt_won(monthly_expense)}, 월 대출이자 {self._fmt_won(monthly_loan_interest)}, 순현금흐름 {self._fmt_won(net_cashflow)}입니다.",
            "debt_comment": f"대출잔액은 {self._fmt_won(debt)}이고 총자산 대비 {self._fmt_number(debt_ratio*100)}%입니다.",
            "family_comment": family_note,
            "life_stage_comment": f"생애주기는 {life_profile['label']}이며, 핵심 목표는 {life_profile['goal']}입니다.",
            "region_comment": f"{region_analysis['region_name']}은 {region_analysis['real_estate_profile']} 지역이며 추천전략은 {region_analysis['strategy']}입니다.",
            "retirement_goal_comment": retirement_goal or "은퇴목표가 입력되지 않았습니다.",
            "risk_flags": risk_flags
        }

    def _create_action_plan(self, current: List[Dict], target: Dict, total: float, monthly_income: float, monthly_expense: float, monthly_loan_interest: float, region_analysis: Dict, life_profile: Dict) -> List[str]:
        plan = []
        if total <= 0:
            return ["자산 정보를 먼저 입력하세요."]

        current_re = sum(a['current_value'] for a in current if self._is_real_estate(a['asset_type'])) / total
        if current_re > target["real_estate"]:
            excess = (current_re - target["real_estate"]) * total
            plan.append(f"부동산 비중을 목표보다 높은 {self._fmt_won(excess)}만큼 단계적으로 낮추세요.")
        
        if monthly_loan_interest > 0:
            plan.append(f"월 대출이자 {self._fmt_won(monthly_loan_interest)}를 반영해 상환/대환 우선순위를 검토하세요.")

        net_cashflow = monthly_income - monthly_expense - monthly_loan_interest
        if net_cashflow < 0:
            plan.append("순현금흐름이 음수입니다. 추가 투자보다 지출 조정과 이자 부담 축소가 먼저입니다.")
        else:
            plan.append("순현금흐름이 양수입니다. 대출 감축과 금융자산 분산투자를 병행하세요.")

        plan.append(f"지역 특성상 '{region_analysis['strategy']}' 전략을 우선 검토하세요.")
        plan.append(f"{life_profile['label']} 단계이므로 '{life_profile['goal']}' 중심으로 실행 계획을 세우세요.")
        return plan
