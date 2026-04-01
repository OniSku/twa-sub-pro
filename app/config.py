from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    telegram_bot_token: str = ""
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
