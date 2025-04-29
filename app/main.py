from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import async_session, engine, Base
from app.database.crud import UserCrud, RecipeCrud
import uvicorn
from app.database.database import get_db
from typing import Optional
from fastapi import Query

from fastapi import Depends, APIRouter

router = APIRouter()
app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Recipes API!"}


# Создать таблицы при старте приложения
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Регистрация пользователя создает нового пользователя в БД
@app.post("/register")
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await UserCrud.create_user(db, username, password)
    return {"message": "User created", "user_id": user.id}

# Авторизация пользователя Если введены правильные данные — успешный ответ с user_id
@app.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await UserCrud.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful", "user_id": user.id}

# Создание рецепта в бд
@app.post("/recipes")
async def create_recipe(title: str, description: str, cuisine: str, giga_chat_description: str, cooking_time: int, db: AsyncSession = Depends(get_db)):
    recipe = await RecipeCrud.create_recipe(db, title, description, cuisine, giga_chat_description)
    return {"message": "Recipe created", "recipe_id": recipe.id}

# Получение рецепта по ID, Если он найден — возвращает подробную информацию о рецепте инчаче 404
@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await RecipeCrud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "cuisine": recipe.cuisine,
        "average_rating": recipe.average_rating,
        "ratings_count": recipe.ratings_count
    }

# Добавление отзыва на рецепт от пользователя
@app.post("/recipes/{recipe_id}/review")
async def add_review(recipe_id: int, user_id: int, rating: int, text: str, db: AsyncSession = Depends(get_db)):
    review = await RecipeCrud.add_review(db, recipe_id, user_id, rating, text)
    return {"message": "Review added", "review_id": review.id}


@app.get("/recipes_f/")
async def get_recipes(
    cuisine: Optional[str] = Query(None),
    max_cooking_time: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    recipes = await RecipeCrud.get_recipes_by_filters(db, cuisine, max_cooking_time)
    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cuisine": recipe.cuisine,
            "cooking_time": recipe.cooking_time,
            "average_rating": recipe.average_rating,
            "ratings_count": recipe.ratings_count
        }
        for recipe in recipes
    ]
@router.delete("/recipes/clear_all")
async def clear_recipes(db: AsyncSession = Depends(get_db)):
    await RecipeCrud.clear_recipes_table(db)
    return {"message": "All recipes deleted"}
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5436)