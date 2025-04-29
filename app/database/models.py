from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    reviews = relationship("Review", back_populates="user")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)  # краткое описание
    cuisine = Column(String, nullable=True)  # вид кухни
    ratings = Column(JSON, default=list)  # список оценок
    average_rating = Column(Float, default=0.0)  # средняя оценка
    ratings_count = Column(Integer, default=0)  # количество оценок
    giga_chat_description = Column(String, nullable=True) # описание с giga chat
    cooking_time = Column(Integer, nullable=True)  # время готовки в минутах

    reviews = relationship("Review", back_populates="recipe")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)
    text = Column(String, nullable=True)

    user = relationship("User", back_populates="reviews")
    recipe = relationship("Recipe", back_populates="reviews")
