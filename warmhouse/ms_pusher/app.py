from fastapi import FastAPI
import os
import logging
from contextlib import asynccontextmanager
import asyncio

from warmhouse.ms_pusher.services.pusher import consume_notifications

PUSHER_CLUSTER = os.getenv("PUSHER_CLUSTER", "cluster1")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
PUSHER_APP_ID = os.getenv("PUSHER_APP_ID", "app_id")
PUSHER_KEY = os.getenv("PUSHER_KEY", "app_id")
PUSHER_SECRET = os.getenv("PUSHER_SECRET", "app_id")
FAKE_PUSHER = os.getenv("FAKE_PUSHER", True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск Kafka consumer
    kafka_consumer_task = asyncio.create_task(consume_notifications())
    yield
    kafka_consumer_task.cancel()


app = FastAPI(
    title="Notification Service",
    description="Сервис уведомлений и WebSocket соединений",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)