from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from warmhouse.lib.models import DeviceStatus, DeviceType


class DeviceCreate(BaseModel):
    name: str
    device_type: DeviceType
    location: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[DeviceStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class DeviceCommand(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None
    priority: str = "normal"


class DeviceResponse(BaseModel):
    id: str
    name: str
    device_type: DeviceType
    status: DeviceStatus
    location: Optional[str]
    configuration: Dict[str, Any]
    metadata: Dict[str, Any]
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime
