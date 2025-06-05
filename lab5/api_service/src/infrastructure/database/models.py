from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)

    # Create indexes for frequently searched fields
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_role', 'role'),
    )

class WallPost(Base):
    __tablename__ = "wall_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(String)
    created_at = Column(DateTime)

    # Create indexes for frequently searched fields
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
    ) 