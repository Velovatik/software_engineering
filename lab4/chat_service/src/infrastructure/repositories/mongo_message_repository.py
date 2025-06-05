from typing import List, Optional
from bson import ObjectId
from src.domain.entities.message import Message as MessageEntity
from src.domain.interfaces.message_repository import MessageRepository
from src.infrastructure.database.connection import message_collection
from src.infrastructure.database.models import Message as MessageModel

# TODO: add message editing functionality later
# TODO: maybe add message status (read/unread)

class MongoMessageRepository(MessageRepository):
    ## MongoDB impl
    
    async def save_message(self, message: MessageEntity) -> MessageEntity:
        return await self.create(message)
    
    async def create(self, message: MessageEntity) -> MessageEntity:
        message_dict = {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at
        }
        
        result = await message_collection.insert_one(message_dict)
        message_dict["_id"] = result.inserted_id  # add the generated id
        return MessageEntity(**message_dict)

    async def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        try:
            message = await message_collection.find_one({"_id": ObjectId(message_id)})
            if message:
                return MessageEntity(**message)
        except Exception as e:
            print(f"Error getting message: {e}")
        return None

    async def get_chat_messages(self, user1_id: int, user2_id: int) -> List[MessageEntity]:
        messages = await message_collection.find({
            "$or": [
                {"sender_id": user1_id, "receiver_id": user2_id},
                {"sender_id": user2_id, "receiver_id": user1_id}
            ]
        }).sort("created_at", 1).to_list(None)
        
        return [MessageEntity(**msg) for msg in messages]

    async def get_user_messages(self, user_id: int) -> List[MessageEntity]:
        messages = await message_collection.find({
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }).sort("created_at", -1).to_list(None)
        
        return [MessageEntity(**msg) for msg in messages]

    async def update(self, message: MessageEntity) -> Optional[MessageEntity]:
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
        try:
            result = await message_collection.delete_one({"_id": ObjectId(message_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Failed to delete message: {e}")  # replace with proper logging
            return False 