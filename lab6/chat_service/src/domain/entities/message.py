from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    id: Optional[str] = None
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime = datetime.now() 