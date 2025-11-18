from fastapi import APIRouter
from .calls import router as call_router
from .reports import router as report_router

router = APIRouter()
router.include_router(call_router, prefix="/calls")
router.include_router(report_router, prefix="/reports")