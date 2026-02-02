from __future__ import annotations

import os
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEPLOY_ENV_MAP = {
    "inlandOline": {"COUNTRY": "zh", "ENVIRONMENT": "production"},
    "inlandTest": {"COUNTRY": "zh", "ENVIRONMENT": "test"},
    "overseasOline": {"COUNTRY": "na", "ENVIRONMENT": "production"},
    "overseasTest": {"COUNTRY": "na", "ENVIRONMENT": "test"},
    "sjpOnline": {"COUNTRY": "xjp", "ENVIRONMENT": "production"},
    "sjpTest": {"COUNTRY": "xjp", "ENVIRONMENT": "test"},
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "test"
    COUNTRY: str = "zh"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./yuyan.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHAT_LOG_REDIS_URL: Optional[str] = None

    KAFKA_BROKERS: Optional[str] = None
    KAFKA_TOPIC: str = "plat_chatmsg"
    KAFKA_TOPIC_QUERY: str = "plat_chatmsg_query"
    KAFKA_TOPIC_JSON: str = "plat_chatmsg_json"
    KAFKA_TOPIC_IMG: str = "plat_chatmsg_img"
    KAFKA_LOG_DIR: str = "logs/kafka"

    LANGUAGE_CLS_URL: str = ""
    LANGUAGE_SWITCH: bool = False
    AD_DETECT_URL: str = ""

    TIME_SEED: int = 5
    BLACK_CLIENT_IP_FILE: str = "app/config/black_client_ip.txt"

    LOG: Dict[str, Any] = Field(
        default_factory=lambda: {
            "LEVEL": "INFO",
            "DIR": "logs/output",
            "SIZE_LIMIT": 1024 * 1024 * 50,
            "REQUEST_LOG": True,
            "FILE": True,
        }
    )
    ACCESS_KEY_FALLBACK: Dict[str, str] = Field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return self.model_dump() if hasattr(self, "model_dump") else self.dict()


def load_settings() -> Settings:
    settings = Settings()
    deploy_env = os.environ.get("deploy")
    if deploy_env and deploy_env in DEPLOY_ENV_MAP:
        settings = settings.model_copy(update=DEPLOY_ENV_MAP[deploy_env])
    return settings
