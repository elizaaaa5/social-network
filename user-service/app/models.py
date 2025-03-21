from datetime import datetime
from sqlalchemy import create_engine, Column, String, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()
metadata = Base.metadata  # Add explicit metadata export

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    birth_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


#Base.metadata.create_all(bind=engine)

