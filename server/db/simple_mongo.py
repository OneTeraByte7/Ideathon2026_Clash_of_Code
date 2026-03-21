"""
Simple MongoDB adapter without Beanie
Works with basic motor operations for Render deployment
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings
import logging

logger = logging.getLogger("asclepius.db")
settings = get_settings()

# MongoDB client
client = None
database = None

async def init_db():
    """Initialize MongoDB connection without Beanie"""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

async def get_db():
    """Get database instance"""
    return database

# Simple collection helpers
class SimpleCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
    
    @property
    def collection(self):
        return database[self.collection_name]
    
    async def find_all(self, filter_dict=None, limit=100):
        """Find documents"""
        filter_dict = filter_dict or {}
        cursor = self.collection.find(filter_dict).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_one(self, filter_dict):
        """Find one document"""
        return await self.collection.find_one(filter_dict)
    
    async def insert_one(self, document):
        """Insert document"""
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def update_one(self, filter_dict, update_dict):
        """Update document"""
        return await self.collection.update_one(filter_dict, {"$set": update_dict})
    
    async def delete_one(self, filter_dict):
        """Delete document"""
        return await self.collection.delete_one(filter_dict)

# Collection instances
patients = SimpleCollection("patients")
vitals = SimpleCollection("vitals")
alerts = SimpleCollection("alerts")
protocols = SimpleCollection("protocols")