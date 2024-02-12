from sqlalchemy import Column, String
from config.database import DBBase

from sqlalchemy import Column, TIMESTAMP, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid
from datetime import datetime

class User(DBBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Boolean, default=False)

    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)