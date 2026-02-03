from fastapi import APIRouter

from .ac_switch import router as ac_switch_router
from .ai_switch import router as ai_switch_router
from .base import router as base_router
from .black_client_ip import router as black_ip_router
from .channel import router as channel_router
from .app import router as app_router
from .image import router as image_router
from .language import router as language_router
from .list_detail import router as list_detail_router
from .model_threshold import router as model_threshold_router
from .name_list import router as name_list_router
from .risk_type import router as risk_type_router
from .text import router as text_router

router = APIRouter()
router.include_router(text_router)
router.include_router(image_router)
router.include_router(app_router)
router.include_router(channel_router)
router.include_router(name_list_router)
router.include_router(list_detail_router)
router.include_router(risk_type_router)
router.include_router(language_router)
router.include_router(ai_switch_router)
router.include_router(ac_switch_router)
router.include_router(model_threshold_router)
router.include_router(black_ip_router)
router.include_router(base_router)
