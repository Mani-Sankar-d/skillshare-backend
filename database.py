from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://skillshare_db_uokv_user:RdCmGw0eIpQCVlz3tRfhc5qqyCLLgCb4@dpg-d2edf0qli9vc73dtsmug-a.oregon-postgres.render.com/skillshare_db_uokv"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_= AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


