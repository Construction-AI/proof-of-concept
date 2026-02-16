from typing import Optional

from app.modules.documents.models import Document

def document_check_user_access(user_id: int, document: Optional[Document] = None):
    if not document:
        raise Exception("Document was not found.")
    if not user_id == document.owner_id:
        raise Exception("Document does not belong to user")