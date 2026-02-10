from fastapi import APIRouter
from auth import router as a_router
from devices import router as d_router
from scenarios import router as s_router
from telemetry import router as t_router

routers = APIRouter()
routers.include_router(a_router)
routers.include_router(d_router)
routers.include_router(s_router)
routers.include_router(t_router)
