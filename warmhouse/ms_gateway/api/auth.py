from fastapi import APIRouter, Depends

from warmhouse.ms_gateway.depends.dependencies import get_service_client
from warmhouse.ms_gateway.services.client import ServiceClient

router = APIRouter(prefix="/auth")


@router.post("/login")
async def login(request: dict, client: ServiceClient = Depends(get_service_client)):
    response = await client._make_request("auth", "POST", "/auth/login", request)
    return response


@router.post("/register")
async def register(request: dict, client: ServiceClient = Depends(get_service_client)):
    response = await client._make_request("auth", "POST", "/auth/register", request)
    return response


@router.post("/users/me")
async def user_me(request: dict, client: ServiceClient = Depends(get_service_client)):
    response = await client._make_request("auth", "GET", "/auth/users/me", request)
    return response


@router.post("/logout")
async def logout(request: dict, client: ServiceClient = Depends(get_service_client)):
    response = await client._make_request("auth", "POST", "/auth/logout", request)
    return response
