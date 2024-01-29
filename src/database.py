import enum
from typing import Any

from sqlalchemy import (Boolean, Column, CursorResult, DateTime, Enum,
                        ForeignKey, Identity, Insert, Integer, LargeBinary,
                        MetaData, Select, String, Update, delete, desc, func,
                        insert, select, update)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, relationship

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

Base = declarative_base()
DATABASE_URL = str(settings.DATABASE_URL)
SYNC_DATABASE_URL = str(settings.SYNC_DATABASE_URL)

engine = create_async_engine(DATABASE_URL)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


class VoteType(enum.IntEnum):
    """Тип голоса."""

    PLUS = 1
    MINUS = -1
    CANCEL = 0


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'auth_user'

    email = Column(String, nullable=False)
    id = Column(Integer, Identity(), primary_key=True)
    password = Column(LargeBinary, nullable=True)
    is_admin = Column(Boolean, server_default="false", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


class Token(Base):
    """Модель токена."""

    __tablename__ = 'auth_refresh_token'

    uuid = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


class Post(Base):
    """Модель голоса."""

    __tablename__ = 'post'
    id = Column(Integer, Identity(), primary_key=True)
    text = Column(String, nullable=False)
    rating = Column(Integer, server_default="0", nullable=False)
    votes_amount = Column(Integer, server_default="0", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    author_id = Column(Integer, nullable=False)
    voters = relationship('Voter', back_populates='post')

    @classmethod
    async def fetch_latest_items(cls):
        query = select(cls).order_by(desc(cls.created_at)).limit(10)
        async with engine.begin() as conn:
            rows = (await conn.execute(query)).all()
            return [row._mapping for row in rows]

    @classmethod
    async def fetch_rated_items(cls):
        query = select(cls).order_by(desc(cls.rating)).limit(10)
        async with engine.begin() as conn:
            rows = (await conn.execute(query)).all()
            return [row._mapping for row in rows]


class Voter(Base):
    """Модель голосующего."""

    __tablename__ = 'voters'

    user_id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    post_id = Column(Integer, ForeignKey(Post.id), nullable=False, primary_key=True)
    rate = Column(Enum(VoteType,
                       name="rate",
                       values_callable=lambda objects: [element.name for element in objects]),
                  default=VoteType.CANCEL,
                  nullable=False)
    post = relationship('Post', back_populates='voters')

    @classmethod
    async def cancel(cls, user_id, post_id):
        async with engine.begin() as conn:
            if vote := (
                    await conn.execute(select(cls).where(cls.user_id == user_id, cls.post_id == post_id))).first():
                await conn.execute(delete(cls).where(cls.user_id == user_id, cls.post_id == post_id))
                await conn.execute(
                    update(Post).values(
                        rating=Post.rating - vote.rate,
                        votes_amount=Post.votes_amount - 1)
                    .where(Post.id == post_id))

    @classmethod
    async def change(cls, rating, user_id, post_id):
        async with engine.begin() as conn:
            if vote := (
                    await conn.execute(select(cls).where(cls.user_id == user_id, cls.post_id == post_id))).first():
                if vote.rate != rating:
                    await conn.execute(update(Post).values(rating=Post.rating + 2 * rating).where(Post.id == post_id))
                return  # noqa
            await conn.execute(
                update(Post).values(
                    rating=Post.rating + rating,
                    votes_amount=Post.votes_amount + 1)
                .where(Post.id == post_id))
            return await conn.execute(insert(Voter).values(
                {
                    "user_id": user_id,
                    "post_id": post_id,
                    "rate": rating
                }).returning(Voter))


async def fetch_one(select_query: Select | Insert | Update) -> dict[str, Any] | None:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> list[dict[str, Any]]:
    async with engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r._asdict() for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with engine.begin() as conn:
        await conn.execute(select_query)
