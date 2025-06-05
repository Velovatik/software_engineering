from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WallPost(BaseModel):
    id: Optional[int]
    user_id: int
    content: str
    created_at: Optional[datetime] = None 