import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from warmhouse.ms_gateway.api import routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart House API Gateway", description="Основной шлюз для системы умного дома", version="1.0.0")

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
