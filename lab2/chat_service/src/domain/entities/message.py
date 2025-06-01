from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    sender: str
    receiver: str
    content: str
    timestamp: datetime = datetime.now() 