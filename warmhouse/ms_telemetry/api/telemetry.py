import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from warmhouse.ms_telemetry.dto.telemetry import TelemetryData
from warmhouse.ms_telemetry.utils import execute_clickhouse_query

router = APIRouter(prefix="/telemetry")

logger = logging.getLogger(__name__)


@router.post("")
async def save_telemetry(data: TelemetryData):
    """Сохранить телеметрические данные"""
    try:
        metrics_json = json.dumps(data.metrics)
        tags_json = json.dumps(data.tags or {})

        query = f"""
            INSERT INTO telemetry (device_id, timestamp, metrics, tags)
            VALUES (
                '{data.device_id}',
                '{data.timestamp.isoformat()}',
                '{metrics_json}',
                '{tags_json}'
            )
        """

        await execute_clickhouse_query(query)

        return {
            "status": "success",
            "message": "Telemetry saved",
            "device_id": data.device_id,
            "timestamp": data.timestamp,
        }
    except Exception as e:
        logger.error(f"Failed to save telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_telemetry(device_id: Optional[str] = None, limit: int = 10):
    """Получить последние данные телеметрии"""
    try:
        if device_id:
            query = f"""
                SELECT device_id, timestamp, metrics, tags
                FROM telemetry
                WHERE device_id = '{device_id}'
                ORDER BY timestamp DESC
                LIMIT {limit}
            """
        else:
            query = f"""
                SELECT device_id, timestamp, metrics, tags
                FROM telemetry
                ORDER BY timestamp DESC
                LIMIT {limit}
            """

        result = await execute_clickhouse_query(query)
        if result and "data" in result:
            return result["data"]
        return []
    except Exception as e:
        logger.error(f"Failed to fetch telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_telemetry_history(
    device_id: str, start_date: str, end_date: Optional[str] = None, interval: str = "raw", limit: int = 1000
):
    """Получить исторические данные телеметрии"""
    try:
        # Базовый запрос
        base_query = f"""
            SELECT timestamp, metrics
            FROM telemetry
            WHERE device_id = '{device_id}'
            AND timestamp >= '{start_date}'
        """

        if end_date:
            base_query += f" AND timestamp <= '{end_date}'"

        # Агрегация по интервалам
        if interval != "raw":
            if interval == "hour":
                interval_func = "toStartOfHour"
            elif interval == "day":
                interval_func = "toStartOfDay"
            elif interval == "minute":
                interval_func = "toStartOfMinute"
            else:
                interval_func = "toStartOfHour"

            query = f"""
                SELECT 
                    {interval_func}(timestamp) as interval_start,
                    avg(JSONExtractFloat(metrics, 'temperature')) as avg_temperature,
                    min(JSONExtractFloat(metrics, 'temperature')) as min_temperature,
                    max(JSONExtractFloat(metrics, 'temperature')) as max_temperature,
                    count() as data_points
                FROM telemetry
                WHERE device_id = '{device_id}'
                AND timestamp >= '{start_date}'
            """

            if end_date:
                query += f" AND timestamp <= '{end_date}'"

            query += f"""
                GROUP BY interval_start
                ORDER BY interval_start DESC
                LIMIT {limit}
            """
        else:
            query = base_query + f" ORDER BY timestamp DESC LIMIT {limit}"

        result = await execute_clickhouse_query(query)
        if result and "data" in result:
            return result["data"]
        return []
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}/stats")
async def get_device_stats(device_id: str):
    """Получить статистику по устройству"""
    try:
        query = f"""
            SELECT 
                count() as total_records,
                min(timestamp) as first_record,
                max(timestamp) as last_record,
                avg(JSONExtractFloat(metrics, 'temperature')) as avg_temperature
            FROM telemetry
            WHERE device_id = '{device_id}'
        """

        result = await execute_clickhouse_query(query)
        if result and "data" in result and len(result["data"]) > 0:
            return result["data"][0]
        return {}
    except Exception as e:
        logger.error(f"Failed to get device stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
