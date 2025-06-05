from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WallPostCreate(BaseModel):
    content: str

class WallPostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime 