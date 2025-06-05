from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from src.infrastructure.database.models import User as UserModel

# These should match the values in auth_service.py
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user is None:
        raise credentials_exception
    
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role} 