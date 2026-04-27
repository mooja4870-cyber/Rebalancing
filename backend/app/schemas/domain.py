from pydantic import BaseModel, EmailStr
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
