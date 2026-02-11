from fastapi import APIRouter

from warmhouse.ms_telemetry.api.telemetry import router

routers = APIRouter()
routers.include_router(router)
