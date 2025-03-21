import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Boolean, Integer, UUID
from sqlalchemy.orm import declarative_base
import os

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Primary Key"
    )
    login = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    birth_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
