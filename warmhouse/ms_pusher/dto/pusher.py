from typing import Dict, Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    data: Optional[Dict] = None
