from typing import List, Optional
from bson import ObjectId
from src.domain.interfaces.message_repository import MessageRepository
from src.domain.entities.message import Message as MessageEntity
from src.infrastructure.database.connection import message_collection
from src.infrastructure.database.models import Message as MessageModel

# TODO: add message editing functionality later
# TODO: maybe add message status (read/unread)

class MongoMessageRepository(MessageRepository):
    """
    MongoDB implementation of the message repository.
    Using MongoDB because it's better for chat systems - faster for read/write operations
    and more flexible for future message format changes
    """
    
    async def save_message(self, message: MessageEntity) -> MessageEntity:
        """Required abstract method from interface"""
        return await self.create(message)
    
    async def create(self, message: MessageEntity) -> MessageEntity:
        # convert to dict for mongo
        message_dict = {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at  # might need timezone handling later
        }
        
        result = await message_collection.insert_one(message_dict)
        message_dict["_id"] = result.inserted_id  # add the generated id
        return MessageEntity(**message_dict)

    async def get_user_messages(self, username: str) -> List[MessageEntity]:
        """Required abstract method from interface"""
        # For now, assuming username is user_id (we'd need user service integration for proper username lookup)
        try:
            user_id = int(username)  # temporary conversion
            messages = await message_collection.find({
                "$or": [
                    {"sender_id": user_id},
                    {"receiver_id": user_id}
                ]
            }).sort("created_at", -1).to_list(None)
            
            return [MessageEntity(**msg) for msg in messages]
        except ValueError:
            return []

    async def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        # might need to handle invalid ObjectId format here
        try:
            message = await message_collection.find_one({"_id": ObjectId(message_id)})
            if message:
                return MessageEntity(**message)
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
        
        return [MessageEntity(**msg) for msg in messages]

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
            message_dict["_id"] = ObjectId(message.id)
            return MessageEntity(**message_dict)
        return None

    async def delete(self, message_id: str) -> bool:
        # simple deletion - might need to add "soft delete" later
        try:
            result = await message_collection.delete_one({"_id": ObjectId(message_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Failed to delete message: {e}")  # replace with proper logging
            return False 