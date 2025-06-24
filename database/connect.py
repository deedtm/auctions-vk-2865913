import os
from config.database import DB_PATH
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base

dirpath = os.path.dirname(DB_PATH)
if (dirpath):
    os.makedirs(dirpath, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

from . import models

async def init_db() -> None:
    """Initialize database schema (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous SQLAlchemy session generator"""
    async with async_session() as session:
        yield session
