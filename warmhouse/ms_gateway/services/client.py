import logging
from typing import Optional
import httpx
from fastapi import HTTPException

from warmhouse.ms_gateway.settings import SERVICES

logger = logging.getLogger(__name__)

class ServiceClient:
    def __init__(self):
        self.timeout = 30.0
        self.services = SERVICES

    async def _make_request(self, service_name: str, method: str, path: str,
                            data: Optional[dict] = None, headers: Optional[dict] = None):
        base_url = self.services.get(service_name)
        if not base_url:
            raise HTTPException(status_code=500, detail=f"Service {service_name} not configured")

        url = f"{base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            method_func = getattr(client, method.lower())
            response = await method_func(url, json=data, headers=headers)

            if response.status_code >= 400:
                logger.error(f"Service {service_name} error: {response.status_code} - {response.text}")

            return response
