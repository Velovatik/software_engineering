from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from ..domain.entities.user import User
from ..domain.entities.wall_post import WallPost
from ..application.use_cases.user_use_cases import UserUseCases
from ..application.use_cases.wall_use_cases import WallUseCases
from ..application.auth.jwt_handler import JWTHandler
from ..infrastructure.repositories.in_memory_user_repository import InMemoryUserRepository
from ..infrastructure.repositories.in_memory_wall_repository import InMemoryWallRepository

SECRET_KEY = "your-secret-key-keep-it-secret"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI(title="Social Network API Service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_repository = InMemoryUserRepository()
wall_repository = InMemoryWallRepository()
user_use_cases = UserUseCases(user_repository)
wall_use_cases = WallUseCases(wall_repository)
jwt_handler = JWTHandler(SECRET_KEY)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    username = jwt_handler.decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_use_cases.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_use_cases.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt_handler.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/user/create", response_model=User)
async def create_user(user: User, password: str, current_user: User = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create users")
    try:
        return user_use_cases.create_user(user, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/user/search/{username}", response_model=User)
async def search_user_by_login(username: str, current_user: User = Depends(get_current_user)):
    user = user_use_cases.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/v1/wall/post", response_model=WallPost)
async def create_wall_post(post: WallPost, current_user: User = Depends(get_current_user)):
    post.author = current_user.username
    return wall_use_cases.create_post(post)

@app.get("/api/v1/wall", response_model=List[WallPost])
async def get_wall_posts(current_user: User = Depends(get_current_user)):
    return wall_use_cases.get_all_posts() 