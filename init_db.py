import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models import Plan


async def init_db() -> None:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        plans = [
            Plan(
                name="Basic",
                description="Perfect for getting started",
                price=4.99,
                duration_days=30,
                features="Basic features, Email support, 1 device",
            ),
            Plan(
                name="Pro",
                description="Best for power users",
                price=9.99,
                duration_days=30,
                features="All Basic features, Priority support, 5 devices, Advanced analytics",
            ),
            Plan(
                name="Premium",
                description="Ultimate experience",
                price=19.99,
                duration_days=30,
                features="All Pro features, 24/7 support, Unlimited devices, Custom integrations",
            ),
        ]

        for plan in plans:
            session.add(plan)

        await session.commit()

    await engine.dispose()


async def main() -> None:
    """Инициализирует БД с примерами планов."""
    await init_db()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
