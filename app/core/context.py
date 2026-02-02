from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AppContext:
    settings: Any
    logger: Any
    redis: Any
    chat_redis: Any
    kafka_logger: Any
    config: Dict[str, Any] = field(default_factory=dict)
