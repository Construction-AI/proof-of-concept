from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from typing import List, Optional
from app.db.session import get_db

from app.core.logger import get_logger
from app.modules.chats.models import Chat, Message
from app.modules.chats.schemas import ChatCreateRequest, ChatPostMessageRequest

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
    
    def create_chat(self, user_id: int, chat: ChatCreateRequest, project_id: int):
        db_chat = Chat(
            title=chat.title,
            project_id=project_id,
            user_id=user_id
        )
        
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat
    
    def create_message(self, user_id: int, chat_id: int, role: str, content: str):
        self.check_chat_ownership(user_id=user_id, chat_id=chat_id)
        
        db_message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
        )
        
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def read_chat_by_id(self, user_id: int, chat_id: int):
        chat: Chat = self.db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
        return chat
    
    def read_my_project_chats(self, user_id: int, project_id: int):
        chats: List[Chat] = self.db.query(Chat).filter(Chat.project_id == project_id, Chat.user_id == user_id).all()
        return chats
    
    def read_my_chats(self, user_id: int):
        chats: List[Chat] = self.db.query(Chat).filter(Chat.user_id == user_id).all()
        return chats
    
    def read_chat_messages(self, user_id: int, chat_id: int, limit: Optional[int] = 20):
        chat: Chat = self.read_chat_by_id(user_id=user_id, chat_id=chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found or belongs to another user."
            )

        messages: List[Message] = (
            self.db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return list(reversed(messages))

    
    def check_chat_ownership(self, user_id: int, chat_id: int):
        chat: Chat = self.read_chat_by_id(user_id=user_id, chat_id=chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or belongs to another user.")
        return True
    
    async def complete(self, user_id: int, request: ChatPostMessageRequest):
        from app.modules.projects.service import ProjectService
        from app.modules.rag.service import RagService
        
        # 1. Save prompt to DB
        self.create_message(user_id=user_id, chat_id=request.chat_id, role="user", content=request.content)
        
        # 1b. Get chat
        chat = self.read_chat_by_id(user_id=user_id, chat_id=request.chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or belongs to another user.")
        
        # 2. Get history from DB
        previous_messages: List[Message] = self.read_chat_messages(user_id=user_id, chat_id=request.chat_id)
        
        # 3. Prepare history
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in previous_messages]
        
        project_service = ProjectService(db=self.db)
        storage_keys = project_service.get_storage_keys_for_project_id(user_id=user_id, project_id=chat.project_id)
        
        system_prompt = (
            "Jesteś asystentem AI ekspertem budowlanym. "
            "Odpowiadaj na pytania opierając się na dostarczonej dokumentacji. "
            "Jeśli czegoś nie wiesz, nie zmyślaj."
        )
        
        # 3. Odpytaj RAG uwzględniając historię
        rag_service = RagService(db=self.db)
        answer = await rag_service.chat_with_history(
            question=request.content,
            history=history_dicts,
            storage_keys=storage_keys,
            system_prompt=system_prompt
        )
        
        # 4. Zapisz odpowiedź asystenta w DB
        self.create_message(user_id=user_id, chat_id=request.chat_id, role="assistant", content=answer)
        return answer
        
def get_chat_service(db: Session = Depends(get_db)):
    return ChatService(db=db)