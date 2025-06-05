from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from src.infrastructure.database.models import Message

# TODO: move these to environment variables
MONGODB_URL = "mongodb://mongodb:27017"  # using docker service name
DATABASE_NAME = "chat_service"
COLLECTION_NAME = "messages"

# might need to add retry logic here later
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]
message_collection = database[COLLECTION_NAME]

async def init_db():
    """Initialize database with indexes and test data"""
    # Create indexes for faster queries
    # Note: might need to add compound indexes if query patterns change
    try:
        await message_collection.create_indexes([
            # most common queries will be by sender/receiver
            IndexModel([("sender_id", ASCENDING)]),
            IndexModel([("receiver_id", ASCENDING)]),
            # for message history and sorting
            IndexModel([("created_at", ASCENDING)])
        ])
        print("Indexes created successfully")
    except Exception as e:
        print(f"Failed to create indexes: {e}")
        # maybe should raise here? but then docker-compose gets messy
        # will handle this better later

    # Add test data - helpful for development
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