from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    role: str = "user"

class UserInDB(BaseModel):
    id: int
    username: str
    password: str  # This will contain hashed password
    role: str 