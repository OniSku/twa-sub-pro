from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Boolean, Float
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    telegram_id: int = Column(Integer, unique=True, index=True)
    username: Optional[str] = Column(String, nullable=True)
    first_name: str = Column(String)
    last_name: Optional[str] = Column(String, nullable=True)
    is_premium: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, index=True)
    plan_name: str = Column(String)
    price: float = Column(Float)
    duration_days: int = Column(Integer)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    expires_at: datetime = Column(DateTime(timezone=True))


class Plan(Base):
    __tablename__ = "plans"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, index=True)
    description: str = Column(String)
    price: float = Column(Float)
    duration_days: int = Column(Integer)
    features: str = Column(String)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
