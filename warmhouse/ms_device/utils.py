import json
import logging

from fastapi import Depends

from warmhouse.ms_device.depends.dependencies import get_kafka

logger = logging.getLogger(__name__)


async def send_kafka_event(topic: str, event: dict, kafka=Depends(get_kafka)):
    try:
        await kafka.send_and_wait(topic, json.dumps(event).encode("utf-8"))
    except Exception as e:
        logger.error(f"Failed to send Kafka event: {e}")
