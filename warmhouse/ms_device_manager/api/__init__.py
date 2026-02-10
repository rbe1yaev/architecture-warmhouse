from fastapi import APIRouter

from warmhouse.ms_device_manager.api.scenarios import router

routers = APIRouter()
routers.include_router(router)