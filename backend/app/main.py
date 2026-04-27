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

# 데이터베이스 테이블 자동 생성 (Harness)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="자산균형 AI 플랫폼", description="통합 자산 리밸런싱 엔진")

app.include_router(analysis.router, prefix="/api/v1", tags=["분석"])

# 프론트엔드 정적 파일 연결 (8000포트 전체 대응)
# API 라우트 뒤에 배치하여 경로가 겹치지 않게 함
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# 시스템 초기 데이터 시딩 (Harness)
def seed_data():
    db = next(get_db())
    if db.query(models.RegionMaster).count() == 0:
        regions = [
            models.RegionMaster(region_code="1168000000", region_name="서울 강남구", level=2, is_metropolitan=True),
            models.RegionMaster(region_code="4159000000", region_name="경기 화성시", level=2, is_metropolitan=True),
            models.RegionMaster(region_code="2635000000", region_name="부산 해운대구", level=2, is_metropolitan=False)
        ]
        db.add_all(regions)
        db.commit()

seed_data()

@app.get("/health")
def health_check():
    return {"status": "online", "engine": "AIGravity-v1"}

# 통합 리밸런싱 리포트 생성 API (Orchestration)
@app.get("/api/v1/recommendations/{user_id}")
def get_recommendation(user_id: str, db: Session = Depends(get_db)):
    # 1. 유저 자산 정보 조회 (없을 경우 샘플 데이터로 동작)
    assets = db.query(models.UserAsset).filter(models.UserAsset.user_id == user_id).all()
    
    # 샘플 데이터 생성 (테스트용)
    if not assets:
        sample_assets = [
            {"asset_type": "부동산", "current_value": 1600000000, "debt_amount": 300000000, "debt_interest_rate": 4.5},
            {"asset_type": "부동산", "current_value": 800000000, "debt_amount": 200000000, "debt_interest_rate": 5.8},
            {"asset_type": "금융", "current_value": 150000000, "debt_amount": 0}
        ]
    else:
        sample_assets = [
            {
                "asset_type": a.asset_type, 
                "current_value": a.current_value, 
                "debt_amount": a.debt_amount, 
                "debt_interest_rate": a.debt_interest_rate
            } for a in assets
        ]

    # 2. 통합 엔진 구동
    engine = RebalancingEngine(user_id, db)
    report = engine.generate_report(sample_assets)
    
    return report

# 서버 수동 구동 테스트를 위한 유저 생성 헬퍼
@app.post("/api/v1/users/sample")
def create_sample_user(db: Session = Depends(get_db)):
    from datetime import date
    uid = str(uuid.uuid4())
    new_user = models.User(
        user_id=uid,
        email=f"test_{uid[:8]}@example.com",
        password_hash="hashed_pw",
        name="홍길동",
        birth_date=date.fromisoformat("1963-05-15")
    )
    db.add(new_user)
    db.commit()
    return {"user_id": uid, "message": "샘플 유저가 생성되었습니다."}
