from sqlalchemy import Table, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

# Tabela pośrednia
template_library_link = Table(
    "template_library_link",
    Base.metadata,
    Column("template_id", Integer, ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("library_id", Integer, ForeignKey("template_libraries.id", ondelete="CASCADE"), primary_key=True)
)

class TemplateLibrary(Base):
    __tablename__ = "template_libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)          
    industry: Mapped[str] = mapped_column(String, index=True)      
    description: Mapped[str] = mapped_column(String)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False) 
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    templates = relationship("Template", secondary=template_library_link, back_populates="libraries")