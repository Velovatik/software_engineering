from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# base clase for messages
class MessageBase(BaseModel):
    content: str  # just the text for  now
    # TODO: add support for  images and files  later


class MessageCreate(MessageBase):
    receiver_id: int  # who gets the  mesage
    # mby add some metadata??


# this is what we send back to the  client
class MessageResponse(MessageBase):
    id: str            # converted from  mongo ObjectId
    sender_id: int     # who sent it
    receiver_id: int   # who recieved it
    content: str       # the actual  mesage
    created_at: datetime  # when it was  sent

    class Config:
        orm_mode = True  # not rly orm but works  similarly 