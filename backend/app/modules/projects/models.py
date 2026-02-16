from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base, TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
        
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    