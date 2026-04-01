import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base
from app.dependencies import engine

app = FastAPI(
    title="Telegram Mini App - Subscription Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """Создает таблицы БД при запуске приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown() -> None:
    """Закрывает соединение с БД при остановке приложения."""
    await engine.dispose()


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверка статуса приложения."""
    return {"status": "ok"}


from app.routes import auth, subscriptions

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
