# Simple database connection without Beanie
import motor.motor_asyncio
from pymongo import MongoClient
import os
from typing import Optional

# Simple MongoDB client
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None

async def init_db():
    """Initialize database connection"""
    global client, db
    
    # Use local MongoDB if no connection string provided
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        db = client.asclepius_ai
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Database connected successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Starting without database - using in-memory storage")
        return False

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("✅ Database connection closed")

# In-memory storage as fallback
patients_data = []
vitals_data = []
alerts_data = []
protocols_data = []