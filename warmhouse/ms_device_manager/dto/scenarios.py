from typing import Dict, Any, Optional, List

from pydantic import BaseModel


class ScenarioAction(BaseModel):
    device_id: str
    command: str
    parameters: Optional[Dict] = None
    delay_seconds: int = 0


class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str  # "time" или "manual"
    cron_schedule: Optional[str] = None  # Для триггера времени
    actions: List[ScenarioAction]

