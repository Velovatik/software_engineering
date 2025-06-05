from fastapi import FastAPI
from src.presentation.routes import message_router
from src.infrastructure.database.connection import init_db


app = FastAPI()


@app.on_event("startup")
async def startup_event():

    await init_db()

# setup  routes
app.include_router(message_router.router)

@app.get("/")
async def root():
    return {"message": "Chat Service is running"}