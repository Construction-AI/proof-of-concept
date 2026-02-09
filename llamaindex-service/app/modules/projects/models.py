from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
        
    # 1. The Database Column (The actual link)
    # "users.id" refers to the __tablename__="users" in your User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # 2. The Python Relationship (The magic)
    # Allows you to do: project.owner.email
    owner = relationship("User", back_populates="projects")
    