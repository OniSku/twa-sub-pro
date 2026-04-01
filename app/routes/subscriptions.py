from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.dependencies import get_db
from app.models import Plan, Subscription, User
from app.schemas import PlanResponse, SubscriptionResponse, SubscriptionCreate, PurchaseRequest

router = APIRouter()


@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)) -> List[PlanResponse]:
    """Получаем все доступные планы подписок."""
    stmt = select(Plan)
    result = await db.execute(stmt)
    plans = result.scalars().all()
    
    return [PlanResponse.from_orm(plan) for plan in plans]


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    """Получает конкретный план по ID."""
    stmt = select(Plan).where(Plan.id == plan_id)
    result = await db.execute(stmt)
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return PlanResponse.from_orm(plan)


@router.get("/user/{user_id}", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[SubscriptionResponse]:
    """Получает все подписки пользователя."""
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()
    
    return [SubscriptionResponse.from_orm(sub) for sub in subscriptions]


@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    """Создаем новую подписку для пользователя."""
    stmt = select(User).where(User.id == subscription.user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    expires_at = datetime.utcnow() + timedelta(days=subscription.duration_days)
    
    new_subscription = Subscription(
        user_id=subscription.user_id,
        plan_name=subscription.plan_name,
        price=subscription.price,
        duration_days=subscription.duration_days,
        expires_at=expires_at,
    )
    
    db.add(new_subscription)
    user.is_premium = True
    await db.commit()
    await db.refresh(new_subscription)
    
    return SubscriptionResponse.from_orm(new_subscription)


@router.get("/active/{user_id}", response_model=List[SubscriptionResponse])
async def get_active_subscriptions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[SubscriptionResponse]:
    """Получает активные подписки пользователя по дате истечения."""
    stmt = select(Subscription).where(
        (Subscription.user_id == user_id) & (Subscription.is_active == True)
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()
    
    return [SubscriptionResponse.from_orm(sub) for sub in subscriptions]


@router.post("/purchase", response_model=SubscriptionResponse)
async def purchase_subscription(
    request: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    """Обрабатывает покупку подписки и активирует премиум статус пользователя."""
    stmt = select(User).where(User.id == request.user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stmt = select(Plan).where(Plan.id == request.plan_id)
    result = await db.execute(stmt)
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    expires_at = datetime.utcnow() + timedelta(days=plan.duration_days)
    
    new_subscription = Subscription(
        user_id=request.user_id,
        plan_name=plan.name,
        price=plan.price,
        duration_days=plan.duration_days,
        expires_at=expires_at,
    )
    
    db.add(new_subscription)
    user.is_premium = True
    await db.commit()
    await db.refresh(new_subscription)
    
    return SubscriptionResponse.from_orm(new_subscription)
