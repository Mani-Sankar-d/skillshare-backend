import asyncio
from models import Base
from database import engine

async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_all_tables())
