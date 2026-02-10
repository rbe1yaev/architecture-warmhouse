from fastapi import APIRouter
from warmhouse.ms_gateway.api.auth import router as a_router
from warmhouse.ms_gateway.api.devices import router as d_router
from warmhouse.ms_gateway.api.scenarios import router as s_router
from warmhouse.ms_gateway.api.telemetry import router as t_router

routers = APIRouter()
routers.include_router(a_router, tags=["Auth"])
routers.include_router(d_router, tags=["Device"])
routers.include_router(s_router, tags=["Scenarios"])
routers.include_router(t_router, tags=["Telemetry"])
