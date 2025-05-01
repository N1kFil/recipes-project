from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import async_session, engine, Base
from app.database.database import get_db
from app.database.crud import UserCrud, RecipeCrud

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


router = APIRouter()
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def start():
    return RedirectResponse("/login", status_code=308)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(username: str, password: str, db: AsyncSession = Depends(get_db)):
    pass


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
