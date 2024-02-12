from models.tasks import *
from models.base import GenericResponseModel
from service.context_manager import context_actor_user_data, context_log_meta
from repository.users import get_user_repository
from repository.tasks import get_task_repository, get_shared_tasks_repository
from uuid import UUID
from entity.tasks import Task, SharedTasks
from entity.users import User
from typing import List
import http
from config.logger import logger


class TaskService:
    ERROR_NO_TASK_WITH_ID = "No Task found for given Task ID"
    ERROR_NO_USER_WITH_EMAIL_ID = "No User found for given EMAIL ID"
    ERROR_SHARED_TASK_WITH_EMAIL_ID = "No Previous Shared Task found for given EMAIL ID"
    FETCHED_LIST_OF_TASKS = "Fetched List of Tasks Successfully"
    ADD_TASK_SUCCESS = "Task Added Successfully"
    MODIFY_TASK_SUCCESS = "Task Modified Successfully"
    DELETE_TASK_SUCCESS = "Task Deleted Successfully"
    REORDER_TASK_SUCCESS = "Task Reordered Successfully"
    SHARED_EMAIL_SUCCESS = "Shared with the Email Successfully"
    ALREADY_EMAIL_SUCCESS = "Already Shared with the Email"
    UNSHARED_EMAIL_SUCCESS = "Unshared with the Email Successfully"
    SHARED_PERSONAL_EMAIL = "Can not share with your own email id"

    @staticmethod
    def get_list() -> GenericResponseModel:
        user_repository = get_user_repository()
        task_repository = get_task_repository()
        shared_tasks_repository = get_shared_tasks_repository()

        user_entity:User = user_repository.get_by_user_id(user_id=UUID(context_actor_user_data.get().user_id))

        personal_task_entities: List[Task] = task_repository.get_by_user_id(user_id=user_entity.user_id)
        personal_tasks: List[TaskResponseData] = list(map(lambda t:TaskModel.model_validate(t)
                                                                .build_response_model(), personal_task_entities))
        
        shared_tasks_entities: List[SharedTasks] = shared_tasks_repository.get_by_to_user_id(to_user_id=user_entity.user_id)
        shared_tasks: List[SharedTaskResponseData] = []
        for shared_task in shared_tasks_entities:
            shared_user:User = user_repository.get_by_user_id(user_id=shared_task.from_user_id)
            shared_task_entities: List[Task] = task_repository.get_by_user_id(user_id=shared_task.from_user_id)
            shared_task_models: List[TaskResponseData] = list(map(lambda t:TaskModel.model_validate(t)
                                                                .build_response_model(), shared_task_entities))
            
            shared_tasks.append(SharedTaskResponseData.model_validate({"username":shared_user.username, "tasks":shared_task_models}))
        
        response_dict = dict()
        response_dict["personal_tasks"] = personal_tasks
        response_dict["shared_tasks"] = shared_tasks
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.FETCHED_LIST_OF_TASKS,
                                    data=TaskListResponse.model_validate(response_dict))

    @staticmethod
    def add(add_task: AddTaskModel) -> GenericResponseModel:
        """
        Adds a new Task
        :param add_task: Task to add
        :return: GenericResponseModel
        """
        task_repository = get_task_repository()
        user_id = UUID(context_actor_user_data.get().user_id)
        last_task: Task = task_repository.get_last_by_user_id(user_id=user_id)

        priority = 1
        if last_task:
            priority = last_task.priority + 1

        task: Task = task_repository.create(add_task.create_db_entity(priority=priority, user_id=user_id))
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.ADD_TASK_SUCCESS,
                                    data=TaskModel.model_validate(task).build_response_model())

    @staticmethod
    def modify(modify_task: ModifyTaskModel) -> GenericResponseModel:
        """
        Modifies an existing Task
        :param modify_task: Task to modify
        :return: GenericResponseModel
        """
        task_repository = get_task_repository()
        user_id = UUID(context_actor_user_data.get().user_id)
        
        task_entity: Task = task_repository.get_by_task_id(task_id=modify_task.task_id)

        if not task_entity or task_entity.user_id != user_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No Task found with task_id {modify_task.task_id}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_TASK_WITH_ID)

        dict_modify_task = modify_task.model_dump()
        dict_modify_task.pop('task_id')
        task_entity.description = modify_task.description
        task_entity = task_repository.modify(task=task_entity, updated_data=dict_modify_task)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.MODIFY_TASK_SUCCESS,
                                    data=TaskModel.model_validate(task_entity).build_response_model())
    

    @staticmethod
    def update_status(modify_task: UpdateTaskStatusModel) -> GenericResponseModel:
        """
        Updates an existing Task Status
        :param modify_task: Task to modify
        :return: GenericResponseModel
        """
        task_repository = get_task_repository()
        user_id = UUID(context_actor_user_data.get().user_id)
        
        task_entity: Task = task_repository.get_by_task_id(task_id=modify_task.task_id)

        if not task_entity or task_entity.user_id != user_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No Task found with task_id {modify_task.task_id}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_TASK_WITH_ID)

        dict_modify_task = modify_task.model_dump()
        dict_modify_task.pop('task_id')
        task_entity.status = modify_task.status
        task_entity = task_repository.modify(task=task_entity, updated_data=dict_modify_task)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.MODIFY_TASK_SUCCESS,
                                    data=TaskModel.model_validate(task_entity).build_response_model())
    

    @staticmethod
    def delete(task_id: UUID) -> GenericResponseModel:
        """
        Deletes an existing Task
        :param task_id: Task ID to Delete
        :return: GenericResponseModel
        """
        task_repository = get_task_repository()
        user_id = UUID(context_actor_user_data.get().user_id)
        
        task_entity: Task = task_repository.get_by_task_id(task_id=task_id)
        if not task_entity or task_entity.user_id != user_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No Task found with task_id {task_id}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_TASK_WITH_ID)

        task_repository.delete(task=task_entity)

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.DELETE_TASK_SUCCESS,
                                    data=TaskModel.model_validate(task_entity).build_response_model())
    

    @staticmethod
    def reorder(reorder_task: ReorderTaskModel) -> GenericResponseModel:
        """
        Modifies an existing Task
        :param modify_task: Task to modify
        :return: GenericResponseModel
        """
        task_repository = get_task_repository()
        user_id = UUID(context_actor_user_data.get().user_id)
        
        task_entity: Task = task_repository.get_by_task_id(task_id=reorder_task.task_id)
        if not task_entity or task_entity.user_id != user_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No Task found with task_id {reorder_task.task_id}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_TASK_WITH_ID)
        
        task_entity = task_repository.reorder(task=task_entity, new_priority=reorder_task.priority)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.REORDER_TASK_SUCCESS,
                                    data=TaskModel.model_validate(task_entity).build_response_model())
    

    @staticmethod
    def share(share_task: ShareTasksRequest) -> GenericResponseModel:
        """
        Modifies an existing Task
        :param modify_task: Task to modify
        :return: GenericResponseModel
        """
        user_repository = get_user_repository()
        shared_tasks_repository = get_shared_tasks_repository()
        from_user_id = UUID(context_actor_user_data.get().user_id)
        to_user: User = user_repository.get_by_email(share_task.email)

        if not to_user:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No User found with email {share_task.email}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_USER_WITH_EMAIL_ID) 
        
        if to_user.user_id == from_user_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"Can not share with your own email {share_task.email}")
            return GenericResponseModel(status_code=http.HTTPStatus.FORBIDDEN,
                                        error=TaskService.SHARED_PERSONAL_EMAIL)
        
        shared_task_entity = shared_tasks_repository.get_by_from_and_to_user_id(from_user_id=from_user_id, to_user_id=to_user.user_id)
        if shared_task_entity:
            return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.ALREADY_EMAIL_SUCCESS,
                                    data=SharedTasksModel.model_validate(shared_task_entity).build_response_model())
        
        shared_task_entity = shared_tasks_repository.create(shared_task=share_task.create_db_entity(from_user_id=from_user_id, 
                                                                                             to_user_id=to_user.user_id))
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.SHARED_EMAIL_SUCCESS,
                                    data=SharedTasksModel.model_validate(shared_task_entity).build_response_model())
    


    @staticmethod
    def unshare(unshare_task: ShareTasksRequest) -> GenericResponseModel:
        """
        Modifies an existing Task
        :param modify_task: Task to modify
        :return: GenericResponseModel
        """
        user_repository = get_user_repository()
        shared_tasks_repository = get_shared_tasks_repository()
        from_user_id = UUID(context_actor_user_data.get().user_id)
        to_user: User = user_repository.get_by_email(unshare_task.email)
        if not to_user:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No User found with email {unshare_task.email}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_NO_USER_WITH_EMAIL_ID)
        
        shared_task_entity: SharedTasks = shared_tasks_repository.get_by_from_and_to_user_id(from_user_id=from_user_id,
                                                                                             to_user_id=to_user.user_id)
        if not shared_task_entity:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No Previous Tasks shared with email {unshare_task.email}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=TaskService.ERROR_SHARED_TASK_WITH_EMAIL_ID)

        shared_task_entity = shared_tasks_repository.unshare(shared_task=shared_task_entity)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=TaskService.UNSHARED_EMAIL_SUCCESS,
                                    data=SharedTasksModel.model_validate(shared_task_entity).build_response_model())



