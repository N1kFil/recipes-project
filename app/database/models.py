from sqlalchemy import Column, Integer, String, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.database.database import Base  # Замените, если у вас другой путь к Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    reviews = relationship("Review", back_populates="user", cascade="all, delete")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cuisine = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    giga_chat_description = Column(String, nullable=False)

    ratings = Column(ARRAY(Integer), default=[])  # PostgreSQL ARRAY для хранения оценок
    average_rating = Column(Float, default=0.0)
    ratings_count = Column(Integer, default=0)

    reviews = relationship("Review", back_populates="recipe", cascade="all, delete")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(String)

    user = relationship("User", back_populates="reviews")
    recipe = relationship("Recipe", back_populates="reviews")
