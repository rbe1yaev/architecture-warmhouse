from fastapi import APIRouter

from warmhouse.ms_auth.api.auth import router

routers = APIRouter()
routers.include_router(router)
