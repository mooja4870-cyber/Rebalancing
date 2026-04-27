from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from .core.database import engine, Base, get_db
from .models import domain as models
from .schemas import domain as schemas
from .services.recommendation import RebalancingEngine
from .services.data_collector import collector
from .api import analysis
import uvicorn
import uuid
from datetime import date

# Database table bootstrap (Harness)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asset Balance AI Platform", description="Integrated asset rebalancing engine")

app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

# Initial seed data (Harness)
def seed_data():
    db = next(get_db())
    if db.query(models.RegionMaster).count() == 0:
        regions = [
            models.RegionMaster(region_code="1168000000", region_name="Seoul Gangnam-gu", level=2, is_metropolitan=True),
            models.RegionMaster(region_code="4159000000", region_name="Gyeonggi Hwaseong-si", level=2, is_metropolitan=True),
            models.RegionMaster(region_code="2635000000", region_name="Busan Haeundae-gu", level=2, is_metropolitan=False)
        ]
        db.add_all(regions)
        db.commit()

seed_data()

def _estimate_life_stage(age: int) -> str:
    if age < 35:
        return "early_career"
    if age < 45:
        return "family_growth"
    if age < 55:
        return "asset_accumulation"
    if age < 65:
        return "retirement_transition"
    return "retirement"

def _asset_rows_to_dicts(assets):
    return [
        {
            "asset_type": a.asset_type,
            "current_value": a.current_value,
            "debt_amount": a.debt_amount or 0,
            "debt_interest_rate": a.debt_interest_rate or 0
        } for a in assets
    ]

def _build_recommendation(user_id: str, db: Session, allow_sample: bool = True):
    assets = db.query(models.UserAsset).filter(models.UserAsset.user_id == user_id).all()
    financial = db.query(models.UserFinancialSnapshot).filter(models.UserFinancialSnapshot.user_id == user_id).first()
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()

    if not assets and not allow_sample:
        raise HTTPException(status_code=400, detail="No asset input found for analysis.")

    if not assets:
        current_assets = [
            {"asset_type": "real_estate", "current_value": 1600000000, "debt_amount": 300000000, "debt_interest_rate": 4.5},
            {"asset_type": "real_estate", "current_value": 800000000, "debt_amount": 200000000, "debt_interest_rate": 5.8},
            {"asset_type": "finance", "current_value": 150000000, "debt_amount": 0}
        ]
        source = "sample"
    else:
        current_assets = _asset_rows_to_dicts(assets)
        source = "user_input"

    monthly_income = financial.monthly_income if financial else 3500000
    monthly_expense = financial.monthly_expense if financial else 3200000
    user_profile = {
        "life_stage": profile.life_stage if profile else "retirement_transition",
        "risk_tolerance": financial.risk_tolerance if financial else 4,
        "region_code": profile.region_code if profile else "1168000000"
    }

    engine = RebalancingEngine(user_id, db, user_profile)
    report = engine.generate_report(current_assets, monthly_income, monthly_expense)
    report["source"] = source
    report["user_id"] = user_id
    return report

@app.get("/health")
def health_check():
    return {"status": "online", "engine": "AIGravity-v1"}

@app.get("/api/v1/recommendations/{user_id}")
def get_recommendation(user_id: str, db: Session = Depends(get_db)):
    return _build_recommendation(user_id, db, allow_sample=True)

@app.post("/api/v1/users/analysis-input")
def save_analysis_input(payload: schemas.AnalysisInputRequest, db: Session = Depends(get_db)):
    if not payload.assets:
        raise HTTPException(status_code=400, detail="Enter at least one asset.")

    uid = payload.user_id or str(uuid.uuid4())
    user = db.query(models.User).filter(models.User.user_id == uid).first()
    if not user:
        birth_year = max(1900, date.today().year - payload.age)
        user = models.User(
            user_id=uid,
            email=f"user_{uid[:8]}@asset-balance.local",
            password_hash="input_flow",
            name=payload.name,
            birth_date=date.fromisoformat(f"{birth_year}-01-01")
        )
        db.add(user)
    else:
        user.name = payload.name

    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == uid).first()
    if not profile:
        profile = models.UserProfile(user_id=uid, region_code=payload.region_code)
        db.add(profile)
    profile.region_code = payload.region_code
    profile.annual_income = payload.monthly_income * 12
    profile.life_stage = _estimate_life_stage(payload.age)
    profile.risk_tolerance = payload.risk_tolerance

    financial = db.query(models.UserFinancialSnapshot).filter(models.UserFinancialSnapshot.user_id == uid).first()
    if not financial:
        financial = models.UserFinancialSnapshot(user_id=uid)
        db.add(financial)
    financial.monthly_income = payload.monthly_income
    financial.monthly_expense = payload.monthly_expense
    financial.risk_tolerance = payload.risk_tolerance
    financial.financial_goal = payload.retirement_goal or payload.financial_goal

    db.query(models.UserAsset).filter(models.UserAsset.user_id == uid).delete()
    debt_attached = False
    for index, asset in enumerate(payload.assets):
        debt_amount = asset.debt_amount
        debt_interest_rate = asset.debt_interest_rate
        if payload.loan_balance and not debt_attached and (asset.asset_type == "real_estate" or index == 0):
            debt_amount = payload.loan_balance
            debt_interest_rate = payload.loan_interest_rate
            debt_attached = True
        db.add(models.UserAsset(
            user_id=uid,
            asset_type=asset.asset_type,
            asset_subtype=asset.asset_subtype,
            asset_name=asset.asset_name,
            region_code=asset.region_code or payload.region_code,
            current_value=asset.current_value,
            debt_amount=debt_amount,
            debt_interest_rate=debt_interest_rate
        ))

    db.commit()
    report = _build_recommendation(uid, db, allow_sample=False)
    report["summary"]["family_count"] = payload.family_count
    report["summary"]["family_ages"] = payload.family_ages
    report["summary"]["retirement_goal"] = payload.retirement_goal
    engine = RebalancingEngine(uid, db, {
        "life_stage": _estimate_life_stage(payload.age),
        "risk_tolerance": payload.risk_tolerance,
        "region_code": payload.region_code
    })
    current_assets = _asset_rows_to_dicts(db.query(models.UserAsset).filter(models.UserAsset.user_id == uid).all())
    report = engine.generate_report(
        current_assets,
        payload.monthly_income,
        payload.monthly_expense,
        payload.family_count,
        payload.family_ages,
        payload.retirement_goal
    )
    report["source"] = "user_input"
    report["user_id"] = uid
    return report

@app.post("/api/v1/users/sample")
def create_sample_user(db: Session = Depends(get_db)):
    uid = str(uuid.uuid4())
    new_user = models.User(
        user_id=uid,
        email=f"test_{uid[:8]}@example.com",
        password_hash="hashed_pw",
        name="Sample User",
        birth_date=date.fromisoformat("1963-05-15")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": uid, "message": "sample user created"}

# Frontend static mount must stay after API routes.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
