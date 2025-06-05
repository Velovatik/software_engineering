from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from src.infrastructure.database.models import Message

# TODO: move these to environment variables
MONGODB_URL = "mongodb://mongodb:27017"
DATABASE_NAME = "chat_service"
COLLECTION_NAME = "messages"

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]
message_collection = database[COLLECTION_NAME]

async def init_db():
    try:
        await message_collection.create_indexes([
            IndexModel([("sender_id", ASCENDING)]),
            IndexModel([("receiver_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)])
        ])
        print("Indexes created successfully")
    except Exception as e:
        print(f"Failed to create indexes: {e}")

    if await message_collection.count_documents({}) == 0:
        print("Adding test messages...")
        test_messages = [
            {
                "sender_id": 1,
                "receiver_id": 2,
                "content": "Hello, how are you?",
                "created_at": Message.Config.schema_extra["example"]["created_at"]
            },
            {
                "sender_id": 2,
                "receiver_id": 1,
                "content": "I'm good, thanks!",
                "created_at": Message.Config.schema_extra["example"]["created_at"]
            }
        ]
        await message_collection.insert_many(test_messages)
        print("Test messages added") 