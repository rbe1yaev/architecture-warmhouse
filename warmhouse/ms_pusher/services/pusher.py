import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List

from aiokafka import AIOKafkaConsumer

from warmhouse.ms_pusher.settings import KAFKA_BROKERS, FAKE_PUSHER
if FAKE_PUSHER:
    from warmhouse.ms_pusher.clients.fake.pusher import trigger_event
else:
    from warmhouse.ms_pusher.clients.pusher import trigger_event
from warmhouse.ms_pusher.dto.pusher import NotificationCreate

logger = logging.getLogger(__name__)


async def consume_notifications():
    """Потребление уведомлений из Kafka"""
    try:
        consumer = AIOKafkaConsumer(
            'notifications',
            bootstrap_servers=KAFKA_BROKERS,
            group_id='notification-service'
        )

        await consumer.start()

        async for msg in consumer:
            try:
                notification_data = json.loads(msg.value.decode('utf-8'))
                await process_kafka_notification(notification_data)
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")
    except Exception as e:
        logger.error(f"Kafka consumer error: {e}")


async def process_kafka_notification(data: Dict):
    """Обработка уведомления из Kafka"""
    try:
        notification = NotificationCreate(
            user_id=data.get("user_id", "system"),
            title=data.get("title", "Notification"),
            message=data.get("message", ""),
            data=data.get("data")
        )
        # Отправляем через WebSocket если пользователь онлайн
        data = {
            "user_id": notification.user_id,
            "type": "notification",
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await trigger_event("telemetry", "telemetry_data", data)

        logger.info(f"Processed Kafka notification for user {notification.user_id}")
    except Exception as e:
        logger.error(f"Failed to process Kafka notification: {e}")

