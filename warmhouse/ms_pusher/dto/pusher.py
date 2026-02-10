from typing import Optional, Dict

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    data: Optional[Dict] = None
