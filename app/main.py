import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.database import async_session, engine, Base, get_db
from app.database.models import Recipe, User
from app.database.crud import UserCrud, RecipeCrud
from app.schemas import RecipeBase, ReviewBase, ReviewResponse, UserCreate, UserResponse
import uvicorn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


router = APIRouter()
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=f"{BASE_DIR}/app/templates")
app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/app/static/"), name="static")


@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse("/login")


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_model=UserResponse)
async def register_post(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await UserCrud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    await UserCrud.create_user(db=db, username=user_data.username, password=user_data.password)

    return RedirectResponse("/recipes", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserCrud.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return RedirectResponse("/recipes", status_code=302)


@app.get("/recipes", response_model=List[RecipeBase])
async def get_all_recipes(db: AsyncSession = Depends(get_db)):
    return await RecipeCrud.get_recipes_by_filters(db)


@app.get("/recipes/popular", response_model=List[RecipeBase])
async def get_popular_recipes(
        db: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=1)
):
    query = select(Recipe).order_by(Recipe.average_rating.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/recipes/cuisine/{cuisine}", response_model=List[RecipeBase])
async def get_recipes_by_cuisine(
        cuisine: str,
        db: AsyncSession = Depends(get_db)
):
    return await RecipeCrud.get_recipes_by_cuisine(db, cuisine=cuisine)


@app.get("/recipes/time/{max_cooking_time}", response_model=List[RecipeBase])
async def get_recipes_by_time(
        max_cooking_time: int,
        db: AsyncSession = Depends(get_db)
):
    return await RecipeCrud.get_recipes_by_filters(db, max_cooking_time=max_cooking_time)


@app.get("/recipes/{recipe_id}", response_model=RecipeBase)
async def get_recipe_details(
        recipe_id: int,
        db: AsyncSession = Depends(get_db)
):
    recipe = await RecipeCrud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
