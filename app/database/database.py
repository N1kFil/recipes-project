from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# Dependency при каждом запросе создается новая асинхронная сессия БД, которая автоматически закрывается после использования.
async def get_db():
    async with async_session() as session:
        yield session
