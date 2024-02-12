from sqlalchemy import Column, String
from config.database import DBBase
from sqlalchemy import Column, TIMESTAMP, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid
from datetime import datetime

class Task(DBBase):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), onupdate=datetime.now(), nullable=False)
    is_deleted = Column(Boolean, default=False)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    priority = Column(Integer, nullable=False, index=True)


class SharedTasks(DBBase):
    __tablename__ = 'shared_tasks'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    share_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), onupdate=datetime.now(), nullable=False)
    
    from_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    to_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    is_shared = Column(Boolean, default=True)