from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_storage_key= Column(String)
    content_type = Column(String)
    size = Column(BigInteger)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    owner = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")