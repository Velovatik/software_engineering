from fastapi import FastAPI, Depends
from src.presentation.routes import user_router, wall_router
from src.infrastructure.database.connection import get_db
from scripts.init_db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(user_router.router)
app.include_router(wall_router.router)

@app.get("/")
async def root():
    return {"message": "API Service is running"} 