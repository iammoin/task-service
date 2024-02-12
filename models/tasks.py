from pydantic import BaseModel, validator, EmailStr
from models.base import DBBaseModel
from entity.tasks import Task, SharedTasks
from uuid import UUID
from datetime import datetime
from typing import List
from enum import Enum

class TaskStatus(str, Enum):
    OPEN = "OPEN"
    DONE = "DONE"

class TaskBaseModel(BaseModel):
    description: str


class AddTaskModel(TaskBaseModel):
    def create_db_entity(self, user_id: UUID, priority: int) -> Task:
        """
        Creates a db entity from the AddTask model
        """
        status = TaskStatus.OPEN
        dict_to_build_db_entity = self.model_dump()
        dict_to_build_db_entity['priority'] = priority
        dict_to_build_db_entity['user_id'] = user_id
        dict_to_build_db_entity['status'] = status
        return Task(**dict_to_build_db_entity)


class ModifyTaskModel(BaseModel):
    """Modify Task model"""
    task_id: UUID
    description: str

class UpdateTaskStatusModel(BaseModel):
    """Update Task Status model"""
    task_id: UUID
    status: TaskStatus

class ReorderTaskModel(BaseModel):
    """Reorder Task"""
    task_id: UUID
    priority: int
    
    @validator('priority')
    def priority_validator(cls, priority):
        if priority < 1:
             raise ValueError('task priority must be at greater than 0')
        return priority
        
class ShareTasksRequest(BaseModel):
    """Share Tasks with other users"""
    email: EmailStr

    def create_db_entity(self, from_user_id: UUID, to_user_id: UUID) -> SharedTasks:
        """
        Creates a db entity from the AddTask model
        """
        dict_to_build_db_entity = dict()
        dict_to_build_db_entity['from_user_id'] = from_user_id
        dict_to_build_db_entity['to_user_id'] = to_user_id
        dict_to_build_db_entity['is_shared'] = True
        return SharedTasks(**dict_to_build_db_entity)

class TaskResponseData(BaseModel):
    task_id: str
    user_id: str
    description: str
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime

class SharedTaskResponseData(BaseModel):
    username: str
    tasks: List[TaskResponseData]

class TaskModel(TaskBaseModel, DBBaseModel):
    """Task model"""
    task_id: UUID
    user_id: UUID
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

    def build_task_data(self) -> dict:
        """
        Builds the user token data
        :return: dict
        """
        res_dict = self.model_dump()
        res_dict['task_id'] = str(self.task_id)
        res_dict['user_id'] = str(self.user_id)
        return TaskResponseData.model_validate(res_dict).model_dump()

    def build_response_model(self) -> TaskResponseData:
        res_dict = self.model_dump()
        res_dict['task_id'] = str(self.task_id)
        res_dict['user_id'] = str(self.user_id)
        return TaskResponseData.model_validate(res_dict)

class SharedTasksData(BaseModel):
    share_id: str
    from_user_id: str
    to_user_id: str
    is_shared: bool
    created_at: datetime
    updated_at: datetime

class SharedTasksModel(DBBaseModel):
    """Shared Tasks model"""
    share_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    is_shared: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

    def build_task_data(self) -> dict:
        """
        Builds the user token data
        :return: dict
        """
        res_dict = self.model_dump()
        res_dict['share_id'] = str(self.share_id)
        res_dict['from_user_id'] = str(self.from_user_id)
        res_dict['to_user_id'] = str(self.from_user_id)
        return SharedTasksData.model_validate(res_dict).model_dump()

    def build_response_model(self) -> SharedTasksData:
        res_dict = self.model_dump()
        res_dict['share_id'] = str(self.share_id)
        res_dict['from_user_id'] = str(self.from_user_id)
        res_dict['to_user_id'] = str(self.from_user_id)
        return SharedTasksData.model_validate(res_dict)


class TaskListResponse(BaseModel):
    """Task List Response"""
    personal_tasks: List[TaskResponseData]
    shared_tasks: List[SharedTaskResponseData]