from models.users import UserRegister
from models.base import GenericResponseModel
from utils.password_hasher import PasswordHasher
from entity.users import User
from config.logger import logger
from service.context_manager import context_log_meta
import http
from repository.users import get_user_repository
from models.users import UserModel, UserLoginModel, UserTokenResponseModel
from models.users import UserLoginModel
from utils.jwt_handler import JWTHandler

class UserService:
    MSG_USER_CREATED_SUCCESS = "User created successfully"
    MSG_USER_LOGIN_SUCCESS = "Login successful"
    MSG_USER_SUSPENDED = "User is suspended successfully"

    ERROR_INVALID_CREDENTIALS = "Invalid credentials"
    ERROR_USER_NOT_FOUND = "User not found"


    @staticmethod
    def register(user: UserRegister) -> GenericResponseModel:
        """
        Register user
        :param user: user details to add
        :return: GenericResponseModel
        """
        user_repository = get_user_repository()
        existing_user = user_repository.get_by_email_or_username(user.email, user.username)

        if existing_user:
            return GenericResponseModel(status_code=http.HTTPStatus.CONFLICT, error="email or username already exists")
        
        try:
            hashed_password = PasswordHasher.get_password_hash(user.password)
            user:User = user.create_db_entity(password_hash=hashed_password)
            updated_user:User = user_repository.create(user)
            logger.info(extra=context_log_meta.get(),
                        msg="User created successfully with user_id {}".format(updated_user.user_id))
            return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=UserService.MSG_USER_CREATED_SUCCESS,
                                        data=UserModel.model_validate(updated_user).build_response_model())
        
        except Exception as e:
            return GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, error=str(e))
        
    
    @staticmethod
    def login_user(user_login_request: UserLoginModel) -> GenericResponseModel:
        """
        Login user
        :param user_login_request: user login details
        :return: GenericResponseModel
        """
        user_repository = get_user_repository()
        user_entity: User = user_repository.get_by_username(user_login_request.username)

        if not user_entity:
            logger.error(extra=context_log_meta.get(), msg=f"user not found for username {user_login_request.username}")
            return GenericResponseModel(status_code=http.HTTPStatus.UNAUTHORIZED,
                                        error=UserService.ERROR_USER_NOT_FOUND)
        
        user: UserModel = UserModel.model_validate(user_entity)

        if PasswordHasher.verify_password(user_login_request.password, user.password_hash):
            token = JWTHandler.create_access_token(user.build_user_token_data())
            logger.info(extra=context_log_meta.get(), msg=f"Login successful for user {user.username}"
                                                          f" with token {token}")
            #  return token to client for further use
            return GenericResponseModel(status_code=http.HTTPStatus.OK, data=UserTokenResponseModel(
                access_token=token, user_id=user.user_id), message=UserService.MSG_USER_LOGIN_SUCCESS)
        
        logger.error(extra=context_log_meta.get(), msg=f"Invalid credentials for user {user.username}")
        return GenericResponseModel(status_code=http.HTTPStatus.UNAUTHORIZED,
                                    error=UserService.ERROR_INVALID_CREDENTIALS)
