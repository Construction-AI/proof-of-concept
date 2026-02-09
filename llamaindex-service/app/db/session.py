from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

print(f"SETTINGS.DATABASE_URL: {settings.DATABASE_URL}")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()