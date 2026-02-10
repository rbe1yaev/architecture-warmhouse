from typing import Optional

from fastapi import APIRouter, Depends

from warmhouse.ms_gateway.depends.dependencies import validate_token, get_service_client
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter(prefix="/telemetry")


@router.get("/latest")
async def get_latest_telemetry(
        device_id: Optional[str] = None,
        limit: int = 10,
        client: ServiceClient = Depends(get_service_client),
        _: dict = Depends(validate_token)
):
    params = [f"limit={limit}"]
    if device_id:
        params.append(f"device_id={device_id}")

    query = "?" + "&".join(params)
    response = await client._make_request("telemetry", "GET", f"/telemetry/latest{query}")
    return response


@router.get("/history")
async def get_telemetry_history(
        device_id: str,
        start_date: str,
        end_date: Optional[str] = None,
        interval: str = "raw",
        client: ServiceClient = Depends(get_service_client),
        _: dict = Depends(validate_token)
):
    params = [f"device_id={device_id}", f"start_date={start_date}", f"interval={interval}"]
    if end_date:
        params.append(f"end_date={end_date}")

    query = "?" + "&".join(params)
    response = await client._make_request("telemetry", "GET", f"/telemetry/history{query}")
    return response


@router.get("/devices/{device_id}/stats")
async def get_telemetry_history(
        device_id: str,
        client: ServiceClient = Depends(get_service_client),
        _: dict = Depends(validate_token)
):
    response = await client._make_request("telemetry", "GET", f"/telemetry/devices/{device_id}/stats")
    return response