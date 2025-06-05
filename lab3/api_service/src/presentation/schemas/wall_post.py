from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WallPostBase(BaseModel):
    content: str

class WallPostCreate(WallPostBase):
    pass

class WallPostResponse(WallPostBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 