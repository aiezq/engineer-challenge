import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://orbitto_user:orbitto_password@localhost:5432/orbitto_db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        # Create tables if they do not exist
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
