from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WallPost(BaseModel):
    id: Optional[int]
    content: str
    user_id: int
    created_at: datetime = datetime.now() 