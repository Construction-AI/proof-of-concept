from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String, index=True)
    storage_key: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String)
    size: Mapped[BigInteger] = mapped_column(BigInteger)
    content_hash: Mapped[str] = mapped_column(String)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    
    owner = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")