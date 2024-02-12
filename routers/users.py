from fastapi import APIRouter, Depends, HTTPException
from models.users import UserRegister
from models.users import UserLoginModel
import http
from service.context_manager import build_request_context
from models.base import GenericResponseModel
from service.users import UserService
from .base import build_api_response

router = APIRouter(prefix="/v1/user", tags=["User"])


@router.post("/register", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
async def register(user: UserRegister, _=Depends(build_request_context)):
    """
    Sign up user
    :param _: build_request_context dependency injection handles the request context
    :param user: user details to add
    :return:
    """
    response: GenericResponseModel = UserService.register(user=user)
    return build_api_response(response)

@router.post("/login", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def login_user(user_login_request: UserLoginModel, _=Depends(build_request_context)):
    """
    Login user
    :param _: build_request_context dependency injection handles the request context
    :param user_login_request: user login details
    :return: GenericResponseModel
    """
    response: GenericResponseModel = UserService.login_user(user_login_request=user_login_request)
    return build_api_response(response)
