from typing import Optional

from fastapi import APIRouter, Depends

from warmhouse.ms_gateway.depends.dependencies import get_service_client, validate_token
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter(prefix="/device")


@router.get("")
async def get_devices(
    device_type: Optional[str] = None,
    location: Optional[str] = None,
    client: ServiceClient = Depends(get_service_client),
    _: dict = Depends(validate_token),
):
    """Получить список устройств"""
    params = []
    if device_type:
        params.append(f"device_type={device_type}")
    if location:
        params.append(f"location={location}")

    query = "?" + "&".join(params) if params else ""
    response = await client._make_request("device", "GET", f"/devices{query}")
    return response


@router.get("/{device_id}")
async def get_device(
    device_id: str, client: ServiceClient = Depends(get_service_client), _: dict = Depends(validate_token)
):
    """Получить устройство по ID"""
    response = await client._make_request("device", "GET", f"/devices/{device_id}")
    return response


@router.post("")
async def create_device(
    request: dict, client: ServiceClient = Depends(get_service_client), _: dict = Depends(validate_token)
):
    """Создать новое устройство"""
    response = await client._make_request("device", "POST", "/devices", request)
    return response


@router.post("/{device_id}/command")
async def send_device_command(
    device_id: str,
    request: dict,
    client: ServiceClient = Depends(get_service_client),
    _: dict = Depends(validate_token),
):
    """Отправить команду устройству"""
    response = await client._make_request("device", "POST", f"/devices/{device_id}/command", request)
    return response
