from sqlalchemy.orm import Session
from app.modules.chats.models import Chat, Message
from app.modules.chats.schemas import ChatCreateRequest, ChatPostMessageRequest

from fastapi import HTTPException, status

from typing import List, Optional

class ChatService:
    
    @staticmethod
    def create_chat(db: Session, user_id: int, chat: ChatCreateRequest):
        db_chat = Chat(
            title=chat.title,
            project_id=chat.project_id,
            user_id=user_id
        )
        
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    
    @staticmethod
    def create_message(db: Session, user_id: int, chat_id: int, role: str, content: str):
        ChatService.check_chat_ownership(db=db, user_id=user_id, chat_id=chat_id)
        
        db_message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    @staticmethod
    def read_chat_by_id(db: Session, user_id: int, chat_id: int):
        chat: Chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
        return chat
    
    @staticmethod
    def read_my_project_chats(db: Session, user_id: int, project_id: int):
        chats: List[Chat] = db.query(Chat).filter(Chat.project_id == project_id, Chat.user_id == user_id).all()
        return chats
    
    @staticmethod
    def read_my_chats(db: Session, user_id: int):
        chats: List[Chat] = db.query(Chat).filter(Chat.user_id == user_id).all()
        return chats
    
    @staticmethod
    def read_chat_messages(db: Session, user_id: int, chat_id: int, limit: Optional[int] = 20):
        chat: Chat = ChatService.read_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found or belongs to another user."
            )

        messages: List[Message] = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())   # newest first
            .limit(limit)
            .all()
        )

        # Optional: reverse so they return oldest → newest
        return list(reversed(messages))

    
    @staticmethod
    def check_chat_ownership(db: Session, user_id: int, chat_id: int):
        chat: Chat = ChatService.read_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or belongs to another user.")
        return True
    
    @staticmethod
    async def complete(db: Session, user_id: int, request: ChatPostMessageRequest):
        from app.modules.projects.service import ProjectService
        from app.modules.rag.service import RagService
        
        # 1. Save prompt to DB
        ChatService.create_message(db=db, user_id=user_id, chat_id=request.chat_id, role="user", content=request.content)
        
        # 1b. Get chat
        chat = ChatService.read_chat_by_id(db=db, user_id=user_id, chat_id=request.chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or belongs to another user.")
        
        # 2. Get history from DB
        previous_messages: List[Message] = ChatService.read_chat_messages(db=db, user_id=user_id, chat_id=request.chat_id)
        
        # 3. Prepare history
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in previous_messages]
        
        storage_keys = ProjectService.get_storage_keys_for_project_id(db=db, user_id=user_id, project_id=chat.project_id)
        
        system_prompt = (
            "Jesteś asystentem AI ekspertem budowlanym. "
            "Odpowiadaj na pytania opierając się na dostarczonej dokumentacji. "
            "Jeśli czegoś nie wiesz, nie zmyślaj."
        )
        
        # 3. Odpytaj RAG uwzględniając historię
        answer = await RagService.chat_with_history(
            question=request.content,
            history=history_dicts,
            storage_keys=storage_keys,
            system_prompt=system_prompt
        )
        
        # 4. Zapisz odpowiedź asystenta w DB
        ChatService.create_message(db=db, user_id=user_id, chat_id=request.chat_id, role="assistant", content=answer)
        return answer
        
        
        
        
        
    