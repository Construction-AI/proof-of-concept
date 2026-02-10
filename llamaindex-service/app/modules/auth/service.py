from sqlalchemy.orm import Session
from app.modules.auth import models, schemas
from app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        hashed_password = get_password_hash(password=user.password)
        
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception:
            db.rollback()
            return None
        
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_token_for_user(user: models.User):
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> models.User | None:
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    
