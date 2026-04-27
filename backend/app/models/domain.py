from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Boolean, CHAR, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(CHAR(1))
    phone = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    profile_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    region_code = Column(String, nullable=False)
    job_category = Column(String)
    annual_income = Column(Float)
    family_type = Column(String)
    life_stage = Column(String)
    risk_tolerance = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class RegionMaster(Base):
    __tablename__ = "region_master"
    region_code = Column(String, primary_key=True)
    region_name = Column(String, nullable=False)
    parent_code = Column(String)
    level = Column(Integer, nullable=False)
    population = Column(Integer)
    is_metropolitan = Column(Boolean, default=False)

class RegionRealEstateIndex(Base):
    __tablename__ = "region_real_estate_index"
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_code = Column(String, ForeignKey("region_master.region_code"))
    index_date = Column(Date, nullable=False)
    house_type = Column(String, nullable=False)
    avg_price_per_sqm = Column(Float)
    jeonse_to_sale_ratio = Column(Float)
    price_change_1y = Column(Float)

class RegionCharacteristics(Base):
    __tablename__ = "region_characteristics"
    region_code = Column(String, ForeignKey("region_master.region_code"), primary_key=True)
    category = Column(String)
    development_stage = Column(String)
    infrastructure_score = Column(Integer)
    growth_potential = Column(Integer)
    investment_recommendation = Column(String)

class UserAsset(Base):
    __tablename__ = "user_assets"
    asset_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    asset_type = Column(String, nullable=False)
    asset_subtype = Column(String)
    asset_name = Column(String)
    region_code = Column(String, ForeignKey("region_master.region_code"))
    current_value = Column(Float)
    debt_amount = Column(Float, default=0.0)
    debt_interest_rate = Column(Float)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
