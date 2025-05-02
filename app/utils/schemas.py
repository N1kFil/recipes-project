from pydantic import BaseModel, Field
from typing import Optional

class RecipeBase(BaseModel):
    title: str
    description: Optional[str]
    cuisine: Optional[str]
    average_rating: float
    ratings_count: int
    cooking_time: Optional[int]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None

class ReviewResponse(ReviewBase):
    user_id: int


