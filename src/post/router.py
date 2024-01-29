from fastapi import APIRouter, Depends, status

from src.auth.jwt import parse_jwt_user_data
from src.auth.schemas import JWTData
from src.database import VoteType
from src.post import service
from src.post.schemas import CreatePost

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(text: CreatePost, jwt_data: JWTData = Depends(parse_jwt_user_data)):
    return await service.create_post(jwt_data, text)


@router.get("/get")
async def get_post(post_id: int):
    return await service.get_post_by_id(post_id)


@router.post("/vote")
async def vote(
        post_id: int,
        rating: VoteType,
        jwt_data: JWTData = Depends(parse_jwt_user_data)):
    return await service.vote(post_id, rating, jwt_data)


@router.get("/get_10_latest_posts")
async def get_latest_post():
    return await service.get_latest_posts()


@router.get("/get_10_rated_posts")
async def get_rated_post():
    return await service.get_rated_posts()
