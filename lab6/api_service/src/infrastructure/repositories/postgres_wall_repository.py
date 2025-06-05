from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.interfaces.wall_repository import WallRepository
from src.domain.entities.wall_post import WallPost as WallPostEntity
from src.infrastructure.database.models import WallPost as WallPostModel
from src.infrastructure.cache.redis_client import RedisClient
import json

class PostgresWallRepository(WallRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, wall_post: WallPostEntity) -> WallPostEntity:
        db_post = WallPostModel(
            user_id=wall_post.user_id,
            content=wall_post.content,
            created_at=wall_post.created_at or datetime.utcnow()
        )
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)
        return WallPostEntity(
            id=db_post.id,
            user_id=db_post.user_id,
            content=db_post.content,
            created_at=db_post.created_at
        )

    def get_by_id(self, post_id: int) -> Optional[WallPostEntity]:
        db_post = self.db.query(WallPostModel).filter(WallPostModel.id == post_id).first()
        if not db_post:
            return None
        return WallPostEntity(
            id=db_post.id,
            user_id=db_post.user_id,
            content=db_post.content,
            created_at=db_post.created_at
        )

    def get_by_user_id(self, user_id: int) -> List[WallPostEntity]:
        db_posts = self.db.query(WallPostModel).filter(WallPostModel.user_id == user_id).all()
        return [
            WallPostEntity(
                id=post.id,
                user_id=post.user_id,
                content=post.content,
                created_at=post.created_at
            )
            for post in db_posts
        ]

    def get_all(self) -> List[WallPostEntity]:
        db_posts = self.db.query(WallPostModel).all()
        return [
            WallPostEntity(
                id=post.id,
                user_id=post.user_id,
                content=post.content,
                created_at=post.created_at
            )
            for post in db_posts
        ]

    def update(self, wall_post: WallPostEntity) -> Optional[WallPostEntity]:
        db_post = self.db.query(WallPostModel).filter(WallPostModel.id == wall_post.id).first()
        if not db_post:
            return None
        
        db_post.content = wall_post.content
        self.db.commit()
        self.db.refresh(db_post)
        
        return WallPostEntity(
            id=db_post.id,
            user_id=db_post.user_id,
            content=db_post.content,
            created_at=db_post.created_at
        )

    def delete(self, post_id: int) -> bool:
        db_post = self.db.query(WallPostModel).filter(WallPostModel.id == post_id).first()
        if not db_post:
            return False
        self.db.delete(db_post)
        self.db.commit()
        return True 