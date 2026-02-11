import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional

from warmhouse.ms_device_manager.depends.dependencies import get_client
from warmhouse.ms_device_manager.settings import DEVICE_SERVICE_URL

logger = logging.getLogger(__name__)


async def send_device_command(
    device_id: str,
    command: str,
    parameters: Optional[Dict] = None,
):
    """Отправить команду устройству через Device Service"""
    try:
        url = f"{DEVICE_SERVICE_URL}/devices/{device_id}/command"
        payload = {"command": command, "parameters": parameters or {}}
        http_client = get_client()
        async with http_client as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to send command to device {device_id}: {e}")
        raise


async def execute_scenario_async(scenario_id: str, db_pool):
    async with db_pool.acquire() as conn:
        scenario = await conn.fetchrow("SELECT * FROM scenarios WHERE id = $1", scenario_id)

        if not scenario:
            logger.error(f"Scenario {scenario_id} not found")
            return

        # Создаем запись о выполнении
        execution_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT INTO scenario_executions (id, scenario_id, status)
            VALUES ($1, $2, $3)
        """,
            execution_id,
            scenario_id,
            "running",
        )

        # Обновляем время последнего выполнения
        await conn.execute("UPDATE scenarios SET last_executed = $1 WHERE id = $2", datetime.utcnow(), scenario_id)

        actions = json.loads(scenario["actions"])
        for action in actions:
            try:
                await send_device_command(action["device_id"], action["command"], action.get("parameters"))

                action_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO executed_actions (id, execution_id, device_id, command, status)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                    action_id,
                    execution_id,
                    action["device_id"],
                    action["command"],
                    "success",
                )

            except Exception as e:
                logger.error(f"Action failed: {e}")
                # Записываем ошибку
                action_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO executed_actions (id, execution_id, device_id, command, status)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                    action_id,
                    execution_id,
                    action["device_id"],
                    action["command"],
                    "failed",
                )

        # Обновляем статус выполнения
        await conn.execute(
            """
            UPDATE scenario_executions 
            SET status = $1, completed_at = $2
            WHERE id = $3
        """,
            "completed",
            datetime.utcnow(),
            execution_id,
        )
