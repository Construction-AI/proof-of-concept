from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db
from app.core.logger import get_logger

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
    logger = get_logger(read_chat_messages.__name__)
    try:
        logger.info(f"Received a request to retrieve chat messages, chat id: {chat_id}")
        chat = ChatService.read_chat_messages(db=db, user_id=current_user.id, chat_id=chat_id)
        logger.info(f"Chat messages retrieved")
        return chat
    except Exception as e:
        logger.error(f"Failed to retrieve messages: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        

@router.post("/{chat_id}/messages", response_model=str, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    request: ChatPostMessageRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    logger = get_logger(send_chat_message.__name__)
    try:
        logger.info(f"Received chat completion request for chat_id: {request.chat_id}")
        ai_response = await ChatService.complete(db=db, user_id=current_user.id, request=request)
        logger.info(f"Chat completion completed")
        return ai_response
    except Exception as e:
        logger.error(f"Failed to retrieve messages: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )