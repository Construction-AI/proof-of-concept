from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base import Base, TimestampMixin
from enum import Enum
from sqlalchemy import Enum as SQLEnum

from typing import Optional, Any, Dict, List

class Template(Base, TimestampMixin):
    __tablename__ = "templates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String)
    
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="templates")
    
    nodes: Mapped[List["TemplateNodes"]] = relationship(
        "TemplateNodes",
        back_populates="template",
        cascade="all, delete-orphan"
    )
    
class TemplateNodes(Base, TimestampMixin):
    __tablename__ = "template_nodes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("template_nodes.id", ondelete="CASCADE"), nullable=True)
    type: Mapped[String] = mapped_column(String, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    template = relationship("Template", back_populates="nodes")
    parent: Mapped[Optional["TemplateNodes"]] = relationship(
        "TemplateNodes",
        remote_side=[id],
        back_populates="children"
    )
    
    children: Mapped[List["TemplateNodes"]] = relationship(
        "TemplateNodes",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
class NodeType(str, Enum):
    