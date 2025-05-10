from pydantic import BaseModel, Field
from typing import Optional


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None


class RecipeBase(BaseModel):
    title: str
    description: Optional[str]
    cuisine: Optional[str]
    ratings: Optional[list[ReviewBase]]
    average_rating: float
    ratings_count: int
    giga_chat_description: Optional[str]
    cooking_time: Optional[int]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=6, max_length=10)

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class ReviewResponse(ReviewBase):
    user_id: int
