from sqlalchemy.orm import Session
from app.modules.auth import models, schemas
from app.core.security import get_password_hash, verify_password, create_token
from app.core.config import settings
from app.core.logger import get_logger

from datetime import timedelta, datetime, timezone

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
    def create_tokens_for_user(db: Session, user: models.User):        
        access_token = create_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        db_token = models.RefreshToken(
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires,
            user_id=user.id
        )
        db.add(db_token)
        db.commit()
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    @staticmethod
    def rotate_refresh_token(db: Session, refresh_token: str):
        existing_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token).first()
        
        if not existing_token:
            return None
        
        if existing_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(existing_token)
            db.commit()
            return None
        
        user = existing_token.user
        db.delete(existing_token)
        db.commit()
        
        return AuthService.create_tokens_for_user(db=db, user=user)
    
    @staticmethod
    def logout_user(db: Session, refresh_token: str):
        existing_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token).first()
        if existing_token:
            db.delete(existing_token)
            db.commit()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> models.User | None:
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    
