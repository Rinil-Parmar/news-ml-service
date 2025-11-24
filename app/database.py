from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.db_name]

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_uri)
        # Test connection
        await db.client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("❌ Closed MongoDB connection")