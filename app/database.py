from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///ecommerce.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

"""
Connect async database
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://ecommerce_user:{getenv("DB_PASS")}@localhost:5432/ecommerce_db"

class Base(DeclarativeBase):
    pass
