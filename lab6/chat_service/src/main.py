from fastapi import FastAPI
from src.presentation.routes import message_router
from src.infrastructure.database.connection import init_db

# main app  instance
app = FastAPI()

# init db when app  starts
@app.on_event("startup")
async def startup_event():
    # TODO: add proper error  handling
    # TODO: add retries if mongo is  down
    await init_db()  # hope this  works

# setup  routes
app.include_router(message_router.router)  # all the mesaging stuff

# basic health  check
@app.get("/")
async def root():
    # mby add more info  here??
    return {"message": "Chat Service is running"}  # good  enuff for now 