from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
import uuid
from typing import List, Optional

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # Дополнительные поля поверх стандартных из SQLAlchemyBaseUserTableUUID
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Связи
    links: Mapped[List["Link"]] = relationship("Link", back_populates="user", cascade="all, delete-orphan")
    expired_links: Mapped[List["ExpiredLink"]] = relationship("ExpiredLink", back_populates="user")


class Link(Base):
    __tablename__ = "links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    original_url: Mapped[str] = mapped_column(String(2048))
    short_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    clicks: Mapped[int] = mapped_column(default=0)
    last_clicked_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_custom: Mapped[bool] = mapped_column(default=False)
    project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="links")


class ExpiredLink(Base):
    __tablename__ = "expired_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    original_url: Mapped[str] = mapped_column(String(2048))
    short_code: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    expired_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    total_clicks: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="expired_links")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)