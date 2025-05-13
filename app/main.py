from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Query, status, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session, engine, Base, get_db
from app.database.crud import UserCrud, RecipeCrud
from app.schemas import RecipeBase, ReviewBase, ReviewResponse, UserCreate, UserResponse

from app.auth import utils as auth_utils
import jwt

from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
import uvicorn

BASE_DIR = Path(__file__).parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


router = APIRouter()
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


def verify_token(token: str):
    try:
        payload = auth_utils.decode_jwt(token)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(access_token: str = Cookie(default=None)):
    if access_token:
        payload = auth_utils.decode_jwt(access_token)
        if payload:
            return payload
    return None


@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse("/login")


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request, user: dict | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/recipes")
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_post(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await UserCrud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    user = await UserCrud.create_user(db=db, username=user_data.username, password=user_data.password)
    jwt_payload = {
        "sub": str(user.id),
        "username": user.username,
    }
    token = auth_utils.encode_jwt(jwt_payload)
    cookie = auth_utils.create_cookie(token)
    response = JSONResponse(content={"success": True, "redirect_url": "/recipes", "token": token})
    response.set_cookie(**cookie)
    return response


@app.get("/login")
def login_page(request: Request, user: dict | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/recipes")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserCrud.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    jwt_payload = {
        "sub": str(user.id),
        "username": user.username,
    }
    token = auth_utils.encode_jwt(jwt_payload)
    cookie = auth_utils.create_cookie(token)
    response = JSONResponse(content={"success": True, "redirect_url": "/recipes", "token": token})
    response.set_cookie(**cookie)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


@app.get("/recipes", response_model=List[RecipeBase])
async def get_all_recipes(db: AsyncSession = Depends(get_db), user: dict | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return await RecipeCrud.get_recipes_by_filters(db)


@app.get("/recipes/popular", response_model=List[RecipeBase])
async def get_popular_recipes(db: AsyncSession = Depends(get_db),
                              limit: int = Query(10, ge=1),
                              user: dict | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return await RecipeCrud.get_popular_recipes(db, limit=limit)


@app.get("/recipes/cuisine/{cuisine}", response_model=List[RecipeBase])
async def get_recipes_by_cuisine(
        cuisine: str,
        db: AsyncSession = Depends(get_db),
        user: dict | None = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
    return await RecipeCrud.get_recipes_by_cuisine(db, cuisine=cuisine)


@app.get("/recipes/time/{max_cooking_time}", response_model=List[RecipeBase])
async def get_recipes_by_time(
        max_cooking_time: int,
        db: AsyncSession = Depends(get_db),
        user: dict | None = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
    return await RecipeCrud.get_recipes_by_filters(db, max_cooking_time=max_cooking_time)


@app.get("/recipes/{recipe_id}", response_model=RecipeBase)
async def get_recipe_details(
        recipe_id: int,
        db: AsyncSession = Depends(get_db),
        user: dict | None = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
    recipe = await RecipeCrud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
