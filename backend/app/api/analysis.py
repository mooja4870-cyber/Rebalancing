from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import domain as models
from ..services.ai_engine import AIEngine
from datetime import date

router = APIRouter(prefix="/analysis", tags=["Diagnosis & Analysis"])

@router.get("/diagnose/{user_id}")
def diagnose_user(user_id: str, db: Session = Depends(get_db)):
    """
    사용자 스마트 진단 (Module 1)
    생애주기 판별 및 초기 건전성 분석
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 생애주기 판별 로직 (Heuristic)
    today = date.today()
    age = today.year - user.birth_date.year
    
    life_stage = "사회초년기"
    if 35 <= age < 45: life_stage = "가족형성기"
    elif 45 <= age < 55: life_stage = "자산축적기"
    elif 55 <= age < 65: life_stage = "은퇴전환기"
    elif age >= 65: life_stage = "은퇴생활기"
    
    # 자산 데이터 조회
    assets = db.query(models.UserAsset).filter(models.UserAsset.user_id == user_id).all()
    asset_list = [{"asset_type": a.asset_type, "current_value": a.current_value, "debt_amount": a.debt_amount} for a in assets]
    
    ai = AIEngine({"life_stage": life_stage})
    score = ai.calculate_health_score(asset_list)
    
    return {
        "user_name": user.name,
        "age": age,
        "life_stage": life_stage,
        "health_score": score,
        "recommendation": "부동산 비중 축소를 권장합니다." if score < 70 else "양호한 자산 배분 상태입니다."
    }

@router.get("/region/{region_code}")
def analyze_region(region_code: str, db: Session = Depends(get_db)):
    """
    지역 시장 상세 분석 (Module 2)
    """
    master = db.query(models.RegionMaster).filter(models.RegionMaster.region_code == region_code).first()
    char = db.query(models.RegionCharacteristics).filter(models.RegionCharacteristics.region_code == region_code).first()
    
    if not master or not char:
        raise HTTPException(status_code=404, detail="지역 데이터를 찾을 수 없습니다.")
    
    return {
        "region_name": master.region_name,
        "category": char.category,
        "development_stage": char.development_stage,
        "infrastructure_score": char.infrastructure_score,
        "growth_potential": char.growth_potential,
        "investment_recommendation": char.investment_recommendation
    }
