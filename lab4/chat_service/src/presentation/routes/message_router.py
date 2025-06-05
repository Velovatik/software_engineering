from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from src.domain.entities.message import Message
from src.infrastructure.repositories.mongo_message_repository import MongoMessageRepository
from src.presentation.schemas.message import MessageCreate, MessageResponse
from src.presentation.dependencies.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

message_repository = MongoMessageRepository()

@router.post("/", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):

    message = Message(
        id=None,
        sender_id=current_user["id"],
        receiver_id=message_data.receiver_id,
        content=message_data.content,
        created_at=datetime.utcnow()
    )
    
    created_message = await message_repository.create(message)
    
    return MessageResponse(
        id=str(created_message.id),
        sender_id=created_message.sender_id,
        receiver_id=created_message.receiver_id,
        content=created_message.content,
        created_at=created_message.created_at
    )

@router.get("/chat/{other_user_id}", response_model=List[MessageResponse])
async def get_chat_messages(
    other_user_id: int,
    current_user: dict = Depends(get_current_user)
):

    messages = await message_repository.get_chat_messages(current_user["id"], other_user_id)
    

    return [
        MessageResponse(
            id=str(msg.id),
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]

@router.get("/my", response_model=List[MessageResponse])
async def get_my_messages(current_user: dict = Depends(get_current_user)):

    messages = await message_repository.get_user_messages(current_user["id"])
    
    return [
        MessageResponse(
            id=str(msg.id),
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):

    message = await message_repository.get_by_id(message_id)
    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )
    
    # only message sender can delet
    if message.sender_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this message"
        )
    
    await message_repository.delete(message_id)
    return {"message": "Message deleted successfully"} 