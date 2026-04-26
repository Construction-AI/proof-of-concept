from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

from app.modules.auth import models, schemas
from app.core.security import get_password_hash, verify_password, create_token
from app.core.config import settings
from app.core.logger import get_logger
from app.db.session import get_db

class AuthService:  
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
      
    def create_user(self, user: schemas.UserCreate):
        hashed_password = get_password_hash(password=user.password)
        
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception:
            self.db.rollback()
            return None
        
    def authenticate_user(self, email: str, password: str):
        user = self.db.query(models.User).filter(models.User.email == email).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_tokens_for_user(self, user: models.User):        
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
        self.db.add(db_token)
        self.db.commit()
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    def rotate_refresh_token(self, refresh_token: str):
        existing_token = self.db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token).first()
        
        if not existing_token:
            return None
        
        if existing_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            self.db.delete(existing_token)
            self.db.commit()
            return None
        
        user = existing_token.user
        self.db.delete(existing_token)
        self.db.commit()
        
        return self.create_tokens_for_user(user=user)
    
    def logout_user(self, refresh_token: str):
        existing_token = self.db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token).first()
        if existing_token:
            self.db.delete(existing_token)
            self.db.commit()
    
    def get_user_by_email(self, email: str) -> models.User | None:
        user = self.db.query(models.User).filter(models.User.email == email).first()
        return user
    

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db=db)