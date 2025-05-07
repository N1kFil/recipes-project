from fastapi import FastAPI
from app.database.crud import router

app = FastAPI(title="Swagger тест CRUD")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("temp_main:app", host="127.0.0.1", port=8000, reload=True)