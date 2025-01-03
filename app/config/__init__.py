from pydantic import BaseSettings
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv(dotenv_path="product.env")


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Default App")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    class Config:
        env_file = "product.env"


settings = Settings()
