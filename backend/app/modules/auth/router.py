from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from app.modules.auth import schemas, models
from app.modules.auth.service import get_auth_service, AuthService
from app.modules.auth.dependencies import get_current_user
from app.core.logger import get_logger

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    logger = get_logger(register_user.__name__)
    try:
        # TODO: Move this logic and error checking to service
        logger.info(f"Received register request for email: {user_in.email}")
        existing_user = auth_service.get_user_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
        
        new_user = auth_service.create_user(user=user_in)
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
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    logger = get_logger(login_for_access_token.__name__)
    try:
        logger.info(f"Received authentication request from user: {form_data.username}")
        user = auth_service.authenticate_user(email=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        logger.info(f"User has been reauthenticated")
        return auth_service.create_tokens_for_user(user=user)
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
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    logger = get_logger(refresh_token.__name__)
    try:
        logger.info(f"Received refresh token request for refresh token: {token_in}")
        new_tokens = auth_service.rotate_refresh_token(
            refresh_token=token_in.refresh_token
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
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    auth_service.logout_user(refresh_token=token_in.refresh_token)

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(
    current_user: models.User = Depends(get_current_user)
) -> Any:
    return current_user
    