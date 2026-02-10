from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.infra.auth.instances_auth import get_auth_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_service = get_auth_service()
    token_data = auth_service.login_user(email=form_data.username, password=form_data.password)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return token_data

async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    auth_service = get_auth_service()
    email = auth_service.validate_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email