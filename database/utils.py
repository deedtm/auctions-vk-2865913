from .log import logger
from .connect import init_db, Base


async def init_schemas():
    """Initialize database schema using SQLAlchemy"""
    logger.info("Initializing database schemas...")
    await init_db()

    table_names = list(Base.metadata.tables.keys())
    logger.info(f"Tables: {', '.join(table_names)}")
    return table_names

