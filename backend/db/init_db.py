"""Run once to create all tables and seed default patients."""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db.database import engine, Base

# Import all models so Base knows about them
from models import patient, vital, alert, protocol  # noqa: F401


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created.")


if __name__ == "__main__":
    asyncio.run(init_db())