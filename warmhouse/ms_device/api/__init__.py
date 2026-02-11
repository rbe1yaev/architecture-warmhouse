from fastapi import APIRouter

from warmhouse.ms_device.api.device import router

routers = APIRouter()
routers.include_router(router)
