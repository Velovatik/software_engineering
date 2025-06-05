from typing import List, Optional
from bson import ObjectId
from src.domain.interfaces.message_repository import MessageRepository
from src.domain.entities.message import Message as MessageEntity
from src.infrastructure.database.connection import message_collection
from src.infrastructure.database.models import Message as MessageModel
from aiokafka import AIOKafkaProducer
import json

# TODO: add message editing functionality later
# TODO: maybe add message status (read/unread)

class MongoMessageRepository(MessageRepository):
    """
    MongoDB implementation of the message repository.
    Using MongoDB because it's better for chat systems - faster for read/write operations
    and more flexible for future message format changes
    """
    
    async def create(self, message: MessageEntity) -> MessageEntity:
        # convert to dict for mongo
        message_dict = {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at  # might need timezone handling later
        }
        
        result = await message_collection.insert_one(message_dict)
        return MessageEntity(
            id=str(result.inserted_id),
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            created_at=message.created_at
        )

    async def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        # might need to handle invalid ObjectId format here
        try:
            message = await message_collection.find_one({"_id": ObjectId(message_id)})
            if message:
                return MessageEntity(
                    id=str(message["_id"]),
                    sender_id=message["sender_id"],
                    receiver_id=message["receiver_id"],
                    content=message["content"],
                    created_at=message["created_at"]
                )
        except Exception as e:
            print(f"Error getting message: {e}")  # should use proper logging
        return None

    async def get_chat_messages(self, user1_id: int, user2_id: int) -> List[MessageEntity]:
        # get messages between two users, sorted by time
        # using $or for both directions of communication
        messages = await message_collection.find({
            "$or": [
                {"sender_id": user1_id, "receiver_id": user2_id},
                {"sender_id": user2_id, "receiver_id": user1_id}
            ]
        }).sort("created_at", 1).to_list(None)  # None means no limit
        
        return [MessageEntity(
            id=str(msg["_id"]),
            sender_id=msg["sender_id"],
            receiver_id=msg["receiver_id"],
            content=msg["content"],
            created_at=msg["created_at"]
        ) for msg in messages]

    async def get_user_messages(self, user_id: int) -> List[MessageEntity]:
        # get all messages where user is either sender or receiver
        # newest first - that's why -1 in sort
        messages = await message_collection.find({
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }).sort("created_at", -1).to_list(None)
        
        return [MessageEntity(
            id=str(msg["_id"]),
            sender_id=msg["sender_id"],
            receiver_id=msg["receiver_id"],
            content=msg["content"],
            created_at=msg["created_at"]
        ) for msg in messages]

    async def update(self, message: MessageEntity) -> Optional[MessageEntity]:
        # not sure if we need this method, but implementing for CRUD completeness
        message_dict = {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at
        }
        
        result = await message_collection.update_one(
            {"_id": ObjectId(message.id)},
            {"$set": message_dict}
        )
        
        if result.modified_count:
            return MessageEntity(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                created_at=message.created_at
            )
        return None

    async def delete(self, message_id: str) -> bool:
        # simple deletion - might need to add "soft delete" later
        try:
            result = await message_collection.delete_one({"_id": ObjectId(message_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Failed to delete message: {e}")  # replace with proper logging
            return False 