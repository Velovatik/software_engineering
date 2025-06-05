import bcrypt
from sqlalchemy import create_engine
from src.infrastructure.database.models import Base, User
from src.infrastructure.database.connection import SQLALCHEMY_DATABASE_URL

def init_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        password_hash = bcrypt.hashpw("secret".encode('utf-8'), bcrypt.gensalt())
        admin_user = User(
            username="admin",
            password_hash=password_hash.decode('utf-8'),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
    
    db.close()

if __name__ == "__main__":
    print("Initializing the database...")
    init_db()
    print("Database initialization completed.") 