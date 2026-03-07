from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.modules.auth import schemas, models
from app.modules.auth.service import AuthService
from app.modules.auth.dependencies import get_current_user
from app.core.logger import get_logger

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    logger = get_logger(register_user.__name__)
    try:
        logger.info(f"Received register request for email: {user_in.email}")
        existing_user = AuthService.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
        
        new_user = AuthService.create_user(db, user=user_in)
        return new_user
    except Exception as e:
        logger.error(f"Failed to register user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    logger = get_logger(login_for_access_token.__name__)
    try:
        logger.info(f"Received authentication request from user: {form_data.username}")
        user = AuthService.authenticate_user(db, email=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        logger.info(f"User has been reauthenticated")
        return AuthService.create_tokens_for_user(db=db, user=user)
    except Exception as e:
        logger.error(f"Failed to authenticate user: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    token_in: schemas.TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    logger = get_logger(refresh_token.__name__)
    try:
        logger.info(f"Received refresh token request for refresh token: {token_in}")
        new_tokens = AuthService.rotate_refresh_token(
            db=db, refresh_token=token_in.refresh_token
        )
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return new_tokens
    except Exception as e:
        logger.error(f"Failed to rotate refresh token: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/logout", status_code=204)
def logout(
    token_in: schemas.TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> None:
    AuthService.logout_user(db=db, refresh_token=token_in.refresh_token)

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(
    current_user: models.User = Depends(get_current_user)
) -> Any:
    return current_user
    