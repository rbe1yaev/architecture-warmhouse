from typing import Optional

from fastapi import Depends, APIRouter
from starlette.responses import JSONResponse

from warmhouse.ms_gateway.depends.dependencies import get_service_client
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter()


@router.get("/api/v1/sensors")
async def legacy_get_sensors(
        location: Optional[str] = None,
        client: ServiceClient = Depends(get_service_client)
):
    """Легаси эндпоинт для получения сенсоров"""
    response = await client._make_request("device", "GET", "/devices")
    devices = response.json()

    # Фильтрация только сенсоров и конвертация формата
    sensors = []
    for device in devices:
        if device.get("device_type") in ["temperature_sensor", "humidity_sensor"]:
            sensors.append({
                "id": device["id"],
                "name": device["name"],
                "type": device["device_type"],
                "location": device.get("location", ""),
                "value": device.get("configuration", {}).get("last_value", 0),
                "status": device["status"],
                "last_updated": device.get("last_seen")
            })

    if location:
        sensors = [s for s in sensors if s.get("location") == location]

    return JSONResponse(content=sensors, status_code=200)
