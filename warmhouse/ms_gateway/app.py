from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from api import routers

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "device": os.getenv("DEVICE_SERVICE_URL", "http://device-service:8002"),
    "device_manager": os.getenv("DEVICE_MANAGER_URL", "http://device-manager:8003"),
    "telemetry": os.getenv("TELEMETRY_SERVICE_URL", "http://telemetry-service:8004"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8005"),
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart House API Gateway",
    description="Основной шлюз для системы умного дома",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(routers)
