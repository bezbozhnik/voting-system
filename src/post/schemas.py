from pydantic import BaseModel, Field


class CreatePost(BaseModel):
    text: str = Field(min_length=1, max_length=1024)
