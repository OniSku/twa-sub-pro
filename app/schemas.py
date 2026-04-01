from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VerifyRequest(BaseModel):
    init_data: str


class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_premium: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanBase(BaseModel):
    name: str
    description: str
    price: float
    duration_days: int
    features: str


class PlanCreate(PlanBase):
    pass


class PlanResponse(PlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    user_id: int
    plan_name: str
    price: float
    duration_days: int


class SubscriptionCreate(SubscriptionBase):
    pass


class PurchaseRequest(BaseModel):
    user_id: int
    plan_id: int


class SubscriptionResponse(SubscriptionBase):
    id: int
    is_active: bool
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
