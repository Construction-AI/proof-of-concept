from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db

from app.modules.chats.schemas import MessageResponse, ChatPostMessageRequest
from app.modules.chats.service import ChatService

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.get("/{chat_id}", response_model=List[MessageResponse])
def read_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    chat = ChatService.read_chat_messages(db=db, user_id=current_user.id, chat_id=chat_id)
    return chat

@router.post("/{chat_id}/messages", response_model=str, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    request: ChatPostMessageRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    ai_response = await ChatService.complete(db=db, user_id=current_user.id, request=request)
    return ai_response