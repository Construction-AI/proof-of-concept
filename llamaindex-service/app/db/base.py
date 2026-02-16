from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    