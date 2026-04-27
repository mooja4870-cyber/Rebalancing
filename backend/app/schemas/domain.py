from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    birth_date: date
    gender: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: str
    created_at: datetime
    class Config:
        orm_mode = True

class AssetBase(BaseModel):
    asset_type: str
    asset_subtype: Optional[str] = None
    asset_name: Optional[str] = None
    region_code: Optional[str] = None
    current_value: float
    debt_amount: float = 0.0
    debt_interest_rate: Optional[float] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    asset_id: str
    class Config:
        orm_mode = True

class AnalysisAssetInput(AssetBase):
    pass

class AnalysisInputRequest(BaseModel):
    user_id: Optional[str] = None
    name: str = "User"
    age: int = Field(40, ge=19, le=100)
    region_code: str = "1168000000"
    monthly_income: float = Field(0.0, ge=0)
    monthly_expense: float = Field(0.0, ge=0)
    loan_balance: float = Field(0.0, ge=0)
    monthly_loan_interest: float = Field(0.0, ge=0)
    family_count: int = Field(1, ge=1, le=20)
    family_ages: List[int] = Field(default_factory=list)
    retirement_goal: str = "Stable retirement cashflow"
    risk_tolerance: int = Field(5, ge=1, le=10)
    financial_goal: Optional[str] = None
    assets: List[AnalysisAssetInput]
