# from sqlalchemy import Column, TIMESTAMP, Boolean, Integer
# from sqlalchemy.dialects.postgresql import UUID
# import uuid as uuid
# from datetime import datetime
# from models.base import DBBaseModel
# from abc import ABC, abstractmethod
# # from config.database import DBBase

# class BaseEntity():
#     """Base class for all db orm models"""
#     id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
#     uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), nullable=False)
#     updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now(), onupdate=datetime.now(), nullable=False)
#     is_deleted = Column(Boolean, default=False)

#     @abstractmethod
#     def __to_model(self) -> DBBaseModel:
#         """every child class needs to convert db orm object to pydantic model"""
#         ...