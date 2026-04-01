from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth_utils import verify_telegram_init_data
from app.dependencies import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, VerifyRequest

router = APIRouter()


@router.post("/verify", response_model=UserResponse)
async def verify_user(
    request: VerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Проверяет Telegram initData и создает или возвращает пользователя."""
    user_data = await verify_telegram_init_data(request.init_data)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid initData")
    
    telegram_id = int(user_data.get("user", {}).get("id", 0))
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Missing user ID")
    
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        user_info = user_data.get("user", {})
        user = User(
            telegram_id=telegram_id,
            first_name=user_info.get("first_name", ""),
            last_name=user_info.get("last_name"),
            username=user_info.get("username"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.get("/user/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Получает пользователя по Telegram ID."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)
