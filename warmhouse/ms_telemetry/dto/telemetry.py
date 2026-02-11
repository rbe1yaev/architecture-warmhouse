from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class TelemetryData(BaseModel):
    device_id: str
    timestamp: datetime
    metrics: Dict[str, float]
    tags: Optional[Dict[str, str]] = {}
