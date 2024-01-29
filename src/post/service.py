from datetime import datetime
from typing import Any

from sqlalchemy import insert, select

from src.auth.schemas import JWTData
from src.database import Post, Voter, VoteType, fetch_one
from src.post.schemas import CreatePost


async def create_post(user: JWTData, data: CreatePost):
    insert_query = (
        insert(Post)
        .values(
            {
                "author_id": user.user_id,
                "rating": 0,
                "text": data.text,
                "created_at": datetime.utcnow(),
            }
        )
        .returning(Post)
    )

    return await fetch_one(insert_query)


async def get_post_by_id(post_id: int) -> dict[str, Any] | None:
    select_query = select(Post).where(Post.id == post_id)

    return await fetch_one(select_query)


async def vote(post_id: int, rating: VoteType, user: JWTData) -> dict[str, Any] | None:
    if not rating:
        await Voter().cancel(user.user_id, post_id)
        return
    return await Voter().change(rating, user.user_id, post_id)


async def get_latest_posts():
    return await Post().fetch_latest_items()


async def get_rated_posts():
    return await Post().fetch_rated_items()
