from fastapi import APIRouter, Depends, HTTPException
import http
from models.base import GenericResponseModel
from service.context_manager import build_request_context
from service.tasks import TaskService
from routers.base import build_api_response
from models.tasks import AddTaskModel, ModifyTaskModel, ReorderTaskModel, ShareTasksRequest, UpdateTaskStatusModel, TaskListResponse
from uuid import UUID
from fastapi.responses import FileResponse
from service.context_manager import context_actor_user_data
from uuid import UUID
from utils.pdf_generator import json_to_pdf

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])


@router.get("/", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def get_tasks(_=Depends(build_request_context)):
    """
    Get all tasks for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.get_list()
    return build_api_response(response)


@router.post("/add", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def add_task(task: AddTaskModel, _=Depends(build_request_context)):
    """
    Adds a Task for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.add(add_task=task)
    return build_api_response(response)

@router.put("/modify", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def modify_task(task: ModifyTaskModel, _=Depends(build_request_context)):
    """
    Modifies a Task for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.modify(modify_task=task)
    return build_api_response(response)

@router.put("/status", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def update_task_status(task: UpdateTaskStatusModel, _=Depends(build_request_context)):
    """
    Updates the Task Status for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.update_status(modify_task=task)
    return build_api_response(response)


@router.put("/reorder", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def reorder_task(task: ReorderTaskModel, _=Depends(build_request_context)):
    """
    Reorders a Task for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.reorder(reorder_task=task)
    return build_api_response(response)


@router.put("/share", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def share_tasks(share_task: ShareTasksRequest, _=Depends(build_request_context)):
    """
    Shares all the Tasks of the current user with the given email
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.share(share_task=share_task)
    return build_api_response(response)


@router.put("/unshare", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def unshare_tasks(unshare_task: ShareTasksRequest, _=Depends(build_request_context)):
    """
    Shares all the Tasks of the current user with the given email
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.unshare(unshare_task=unshare_task)
    return build_api_response(response)

@router.delete("/{task_id}", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def delete_task(task_id: str, _=Depends(build_request_context)):
    """
    Deletes a Task for the current user
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = TaskService.delete(task_id=UUID(task_id))
    return build_api_response(response)

@router.get("/pdf")
async def get_pdf(_=Depends(build_request_context)):
    user_id = context_actor_user_data.get().user_id
    filename = user_id + ".pdf"
    headers = {
        "Content-Disposition": f"inline; filename={filename}"
    } 
    
    response: GenericResponseModel = TaskService.get_list()
    data: TaskListResponse = response.data
    json_to_pdf(json_data=data.model_dump(), output_file="files/" + filename)
    file_response = FileResponse("files/" + filename, media_type="application/pdf", headers=headers)
    return file_response