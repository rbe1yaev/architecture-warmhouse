from typing import Optional, Any, Dict

from fastapi import Depends, APIRouter, HTTPException, Body
from starlette.responses import JSONResponse

from warmhouse.ms_gateway.depends.dependencies import get_service_client
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter()


def _device_to_sensor(device: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": device["id"],
        "name": device["name"],
        "type": device.get("device_type"),
        "location": device.get("location", ""),
        "value": device.get("configuration", {}).get("last_value", 0),
        "unit": device.get("configuration", {}).get("unit", ""),
        "status": device.get("status"),
        "last_updated": device.get("last_seen"),
        "created_at": device.get("created_at"),
    }


def _sensor_type_to_device_type(sensor_type: str) -> str:
    if sensor_type == "temperature":
        return "temperature_sensor"
    if sensor_type == "humidity":
        return "humidity_sensor"
    return sensor_type


@router.get("/api/v1/sensors")
async def legacy_get_sensors(
        location: Optional[str] = None,
        client: ServiceClient = Depends(get_service_client),
):
    response = await client._make_request("device", "GET", "/devices")
    devices = response.json()

    sensors = []
    for device in devices:
        if device.get("device_type") in ["temperature_sensor", "humidity_sensor"]:
            sensors.append(_device_to_sensor(device))

    if location:
        sensors = [s for s in sensors if s.get("location") == location]

    return JSONResponse(content=sensors, status_code=200)


@router.get("/api/v1/sensors/{sensor_id}")
async def legacy_get_sensor_by_id(
        sensor_id: str,
        client: ServiceClient = Depends(get_service_client),
):
    response = await client._make_request("device", "GET", f"/devices/{sensor_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Sensor not found")
    device = response.json()
    return JSONResponse(content=_device_to_sensor(device), status_code=200)


@router.post("/api/v1/sensors")
async def legacy_create_sensor(
        payload: Dict[str, Any] = Body(...),
        client: ServiceClient = Depends(get_service_client),
):
    device_payload: Dict[str, Any] = {
        "name": payload.get("name"),
        "device_type": _sensor_type_to_device_type(payload.get("type", "temperature")),
        "location": payload.get("location"),
        "configuration": {
            "unit": payload.get("unit", ""),
            "last_value": payload.get("value", 0),
        },
        "metadata": {},
    }

    response = await client._make_request("device", "POST", "/devices", device_payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    device = response.json()
    return JSONResponse(content=_device_to_sensor(device), status_code=201)


@router.put("/api/v1/sensors/{sensor_id}")
async def legacy_update_sensor(
        sensor_id: str,
        payload: Dict[str, Any] = Body(...),
        client: ServiceClient = Depends(get_service_client),
):
    configuration: Dict[str, Any] = {}
    if "value" in payload and payload["value"] is not None:
        configuration["last_value"] = payload["value"]
    if "unit" in payload and payload["unit"]:
        configuration["unit"] = payload["unit"]

    device_update: Dict[str, Any] = {}
    if "name" in payload:
        device_update["name"] = payload["name"]
    if "location" in payload:
        device_update["location"] = payload["location"]
    if "status" in payload:
        device_update["status"] = payload["status"]
    if configuration:
        device_update["configuration"] = configuration

    if not device_update:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = await client._make_request("device", "PATCH", f"/devices/{sensor_id}", device_update)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    device = response.json()
    return JSONResponse(content=_device_to_sensor(device), status_code=200)


@router.delete("/api/v1/sensors/{sensor_id}")
async def legacy_delete_sensor(
        sensor_id: str,
        client: ServiceClient = Depends(get_service_client),
):
    response = await client._make_request("device", "DELETE", f"/devices/{sensor_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return JSONResponse(content={"message": "Sensor deleted successfully"}, status_code=200)


@router.patch("/api/v1/sensors/{sensor_id}/value")
async def legacy_update_sensor_value(
        sensor_id: str,
        payload: Dict[str, Any] = Body(...),
        client: ServiceClient = Depends(get_service_client),
):
    if "value" not in payload or "status" not in payload:
        raise HTTPException(status_code=400, detail="value and status are required")

    device_update = {
        "status": payload["status"],
        "configuration": {
            "last_value": payload["value"],
        },
    }

    response = await client._make_request("device", "PATCH", f"/devices/{sensor_id}", device_update)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(content={"message": "Sensor value updated successfully"}, status_code=200)


@router.get("/api/v1/sensors/temperature/{location}")
async def legacy_get_temperature_by_location(
        location: str,
        client: ServiceClient = Depends(get_service_client),
):
    response = await client._make_request("device", "GET", "/devices")
    devices = response.json()

    candidates = [
        d for d in devices
        if d.get("device_type") == "temperature_sensor" and d.get("location") == location
    ]
    if not candidates:
        raise HTTPException(status_code=404, detail="No temperature sensors for this location")

    device = candidates[0]
    config = device.get("configuration", {}) or {}

    result = {
        "location": location,
        "value": config.get("last_value", 0),
        "unit": config.get("unit", "C"),
        "status": device.get("status", "unknown"),
        "timestamp": device.get("last_seen"),
        "description": f"Temperature from device {device.get('id')}",
    }
    return JSONResponse(content=result, status_code=200)
