from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.domain.entities.user import User, UserInDB
from src.infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from src.infrastructure.database.connection import get_db
from src.presentation.schemas.user import UserCreate, UserResponse, UserLogin
from src.application.services.auth_service import create_access_token

router = APIRouter(prefix="/users", tags=["users"])

def get_user_repository(db: Session = Depends(get_db)) -> PostgresUserRepository:
    return PostgresUserRepository(db)

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, repo: PostgresUserRepository = Depends(get_user_repository)):
    existing_user = repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_in_db = UserInDB(
        username=user_data.username,
        hashed_password=user_data.password,  # Will be hashed in repository
        email=None,
        full_name=None,
        disabled=False
    )
    created_user = repo.create(user_in_db)
    return UserResponse(
        id=created_user.id,
        username=created_user.username,
        role=created_user.role
    )

@router.post("/login")
async def login(user_data: UserLogin, repo: PostgresUserRepository = Depends(get_user_repository)):
    if not repo.verify_password_by_username(user_data.username, user_data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    user = repo.get_by_username(user_data.username)
    access_token = create_access_token(data={"sub": user.username, "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=list[UserResponse])
async def get_users(repo: PostgresUserRepository = Depends(get_user_repository)):
    users = repo.get_all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role
        )
        for user in users
    ]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, repo: PostgresUserRepository = Depends(get_user_repository)):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role
    ) 