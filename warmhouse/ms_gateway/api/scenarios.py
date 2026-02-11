from typing import Optional

from fastapi import APIRouter, Depends

from warmhouse.ms_gateway.depends.dependencies import get_service_client, validate_token
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter(prefix="/scenarios")


@router.get("")
async def get_scenarios(client: ServiceClient = Depends(get_service_client), _: dict = Depends(validate_token)):
    """Получить список сценариев"""
    response = await client._make_request("device_manager", "GET", "/scenarios")
    return response


@router.get("/{scenario_id}")
async def get_scenario(client: ServiceClient = Depends(get_service_client), _: dict = Depends(validate_token)):
    """Получить список сценариев"""
    response = await client._make_request("device_manager", "GET", "/scenarios/{scenario_id}")
    return response


@router.post("")
async def create_scenario(
    request_data: dict, client: ServiceClient = Depends(get_service_client), _: dict = Depends(validate_token)
):
    """Создать сценарий"""
    response = await client._make_request("device_manager", "POST", "/scenarios", request_data)
    return response


@router.post("/{scenario_id}/execute")
async def execute_scenario(
    scenario_id: str,
    request: Optional[dict] = None,
    client: ServiceClient = Depends(get_service_client),
    _: dict = Depends(validate_token),
):
    """Выполнить сценарий"""
    response = await client._make_request("device_manager", "POST", f"/scenarios/{scenario_id}/execute", request)
    return response
