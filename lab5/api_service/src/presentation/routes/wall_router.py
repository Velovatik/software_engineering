from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.domain.entities.wall_post import WallPost
from src.infrastructure.repositories.postgres_wall_repository import PostgresWallRepository
from src.infrastructure.database.connection import get_db
from src.presentation.schemas.wall_post import WallPostCreate, WallPostResponse
from src.presentation.dependencies.auth import get_current_user

router = APIRouter(prefix="/wall", tags=["wall"])

def get_wall_repository(db: Session = Depends(get_db)) -> PostgresWallRepository:
    return PostgresWallRepository(db)

@router.post("/posts", response_model=WallPostResponse)
async def create_post(
    post_data: WallPostCreate,
    current_user: dict = Depends(get_current_user),
    repo: PostgresWallRepository = Depends(get_wall_repository)
):
    post = WallPost(
        id=None,
        user_id=current_user["id"],
        content=post_data.content,
        created_at=datetime.utcnow()
    )
    created_post = repo.create(post)
    return WallPostResponse(
        id=created_post.id,
        user_id=created_post.user_id,
        content=created_post.content,
        created_at=created_post.created_at
    )

@router.get("/posts", response_model=list[WallPostResponse])
async def get_posts(repo: PostgresWallRepository = Depends(get_wall_repository)):
    posts = repo.get_all()
    return [
        WallPostResponse(
            id=post.id,
            user_id=post.user_id,
            content=post.content,
            created_at=post.created_at
        )
        for post in posts
    ]

@router.get("/posts/{user_id}", response_model=list[WallPostResponse])
async def get_user_posts(user_id: int, repo: PostgresWallRepository = Depends(get_wall_repository)):
    posts = repo.get_by_user_id(user_id)
    return [
        WallPostResponse(
            id=post.id,
            user_id=post.user_id,
            content=post.content,
            created_at=post.created_at
        )
        for post in posts
    ]

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    repo: PostgresWallRepository = Depends(get_wall_repository)
):
    post = repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    repo.delete(post_id)
    return {"message": "Post deleted successfully"} 