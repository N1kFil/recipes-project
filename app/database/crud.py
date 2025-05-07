import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, delete
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database.models import User, Recipe, Review
from app.database.database import get_db

router = APIRouter(tags=["CRUD Operations"])

# ======== SCHEMAS ========
class UserCreate(BaseModel):
    username: str
    password: str

class RecipeCreate(BaseModel):
    title: str
    description: str
    cuisine: str
    giga_chat_description: str
    cooking_time: int

class ReviewCreate(BaseModel):
    user_id: int
    rating: int
    text: str

# ======== USER CRUD ========
class UserCrud:

    @staticmethod
    async def create_user(db: AsyncSession, username: str, password: str):
        # Хеширование пароля с использованием bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Преобразуем байты в строку, если необходимо
        hashed_password_str = hashed_password.decode('utf-8') if isinstance(hashed_password, bytes) else hashed_password
        # Создание нового пользователя
        new_user = User(username=username, hashed_password=hashed_password_str)
        # Добавление пользователя в сессию и сохранение
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        query = await db.execute(select(User).where(User.username == username))
        user = query.scalars().first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
            return user
        return None

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        query = await db.execute(select(User).where(User.id == user_id))
        return query.scalars().first()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        query = await db.execute(select(User).where(User.username == username))
        return query.scalars().first()

# ======== RECIPE CRUD ========
class RecipeCrud:

    @staticmethod
    async def create_recipe(db: AsyncSession, title: str, description: str, cuisine: str, giga_chat_description: str, cooking_time: int):
        new_recipe = Recipe(
            title=title,
            description=description,
            cuisine=cuisine,
            average_rating=0.0,
            ratings_count=0,
            giga_chat_description=giga_chat_description,
            cooking_time=cooking_time
        )
        db.add(new_recipe)
        await db.commit()
        await db.refresh(new_recipe)
        return new_recipe

    @staticmethod
    async def get_recipe(db: AsyncSession, recipe_id: int):
        query = await db.execute(
            select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.reviews))
        )
        return query.scalars().first()

    @staticmethod
    async def get_recipes_by_cuisine(db: AsyncSession, cuisine: str):
        query = await db.execute(select(Recipe).where(Recipe.cuisine == cuisine))
        return query.scalars().all()

    @staticmethod
    async def add_review(db: AsyncSession, recipe_id: int, user_id: int, rating: int, text: str):
        new_review = Review(recipe_id=recipe_id, user_id=user_id, rating=rating, text=text)
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)

        # Пересчёт средней оценки и количества отзывов
        result = await db.execute(select(Review.rating).where(Review.recipe_id == recipe_id))
        ratings = result.scalars().all()

        if ratings:
            avg = sum(ratings) / len(ratings)
            count = len(ratings)

            query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
            recipe = query.scalars().first()
            if recipe:
                recipe.average_rating = avg
                recipe.ratings_count = count
                await db.commit()
                await db.refresh(recipe)

        return new_review

    @staticmethod
    async def get_recipes_by_filters(db: AsyncSession, cuisine: str = None, max_cooking_time: int = None):
        query = select(Recipe)
        filters = []
        if cuisine:
            filters.append(Recipe.cuisine == cuisine)
        if max_cooking_time is not None:
            filters.append(Recipe.cooking_time <= max_cooking_time)
        if filters:
            query = query.where(and_(*filters))
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def clear_recipes_table(db: AsyncSession):
        await db.execute(delete(Recipe))
        await db.commit()

# ======== ROUTES ========

# User
@router.post("/users/", summary="Создать пользователя")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserCrud.create_user(db, data.username, data.password)

@router.post("/auth/", summary="Аутентификация пользователя")
async def auth_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserCrud.authenticate_user(db, data.username, data.password)
    return user or {"error": "Invalid credentials"}

@router.get("/users/by-id/{user_id}", summary="Найти пользователя по ID")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserCrud.get_user_by_id(db, user_id)

@router.get("/users/by-username/{username}", summary="Найти пользователя по имени")
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    return await UserCrud.get_user_by_username(db, username)

# Recipe
@router.post("/recipes/", summary="Создать рецепт")
async def create_recipe(data: RecipeCreate, db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.create_recipe(
        db,
        title=data.title,
        description=data.description,
        cuisine=data.cuisine,
        giga_chat_description=data.giga_chat_description,
        cooking_time=data.cooking_time
    )

@router.get("/recipes/{recipe_id}", summary="Получить рецепт по ID")
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.get_recipe(db, recipe_id)

@router.get("/recipes/cuisine/{cuisine}", summary="Получить рецепты по кухне")
async def get_recipes_by_cuisine(cuisine: str, db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.get_recipes_by_cuisine(db, cuisine)

@router.post("/recipes/{recipe_id}/reviews/", summary="Добавить отзыв к рецепту")
async def add_review(recipe_id: int, data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.add_review(db, recipe_id, data.user_id, data.rating, data.text)

@router.get("/recipes/", summary="Фильтр по рецептам")
async def get_recipes_by_filters(cuisine: str = None, max_cooking_time: int = None, db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.get_recipes_by_filters(db, cuisine, max_cooking_time)

@router.delete("/recipes/", summary="Очистить таблицу рецептов")
async def clear_recipes_table(db: AsyncSession = Depends(get_db)):
    await RecipeCrud.clear_recipes_table(db)
    return {"message": "Recipes table cleared"}



# Создание таблицы users
# CREATE TABLE users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(255) UNIQUE NOT NULL,
#     hashed_password VARCHAR(255) NOT NULL
# );
#
# Создание таблицы recipes
# CREATE TABLE recipes (
#     id SERIAL PRIMARY KEY,
#     title VARCHAR(255) NOT NULL,
#     description TEXT NOT NULL,
#     cuisine VARCHAR(255) NOT NULL,
#     cooking_time INT NOT NULL,
#     giga_chat_description TEXT NOT NULL,
#     ratings INTEGER[] DEFAULT ARRAY[]::INTEGER[],  -- Это для массива оценок
#     average_rating FLOAT DEFAULT 0.0,
#     ratings_count INT DEFAULT 0
# );
#
# Создание таблицы reviews
# CREATE TABLE reviews (
#     id SERIAL PRIMARY KEY,
#     user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#     recipe_id INT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
#     rating INT NOT NULL,
#     text TEXT
# );

