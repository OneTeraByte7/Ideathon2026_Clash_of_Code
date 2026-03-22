from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import get_settings

settings = get_settings()

# MongoDB client
client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.database_name]


async def init_db():
    """Initialize Beanie with the Product document model"""
    from models.patient import Patient
    from models.vital import Vital
    from models.alert import Alert
    from models.protocol import Protocol
    
    await init_beanie(
        database=database,
        document_models=[Patient, Vital, Alert, Protocol]
    )
    print("✅ MongoDB connected and Beanie initialized")


async def get_db():
    """Dependency to get database"""
    return database


def get_db_connection():
    """Get database connection (non-async version for compatibility)"""
    return database


async def close_db():
    """Close database connection"""
    client.close()
    print("✅ MongoDB connection closed")