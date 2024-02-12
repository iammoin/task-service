from pydantic import BaseModel, validator, EmailStr
from models.base import DBBaseModel
from entity.users import User
from uuid import UUID

class UserBaseModel(BaseModel):
    email: EmailStr
    username: str
    


class UserRegister(UserBaseModel):
    password: str

    @validator('password')
    def password_validator(cls, password):
        """
        Validates that the password is at least 8 characters long,
        contains at least one uppercase letter, one lowercase letter,
        one number, and one special character.
        """
        special_chars = {'!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '='}
        if len(password) < 8:
            raise ValueError('password must be at least 8 characters long')
        if not any(char.isupper() for char in password):
            raise ValueError('password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in password):
            raise ValueError('password must contain at least one number')
        if not any(char in special_chars for char in password):
            raise ValueError('password must contain at least one special character')
        return password

    def create_db_entity(self, password_hash: str) -> User:
        """
        Creates a db entity from the UserRegister model
        """
        dict_to_build_db_entity = self.model_dump()
        dict_to_build_db_entity['password_hash'] = password_hash
        dict_to_build_db_entity.pop('password')
        return User(**dict_to_build_db_entity)


class UserLoginModel(BaseModel):
    """User login model"""
    username: str
    password: str


class UserTokenData(BaseModel):
    """User token data"""
    user_id: str
    email: EmailStr
    username: str

class UserModel(UserBaseModel, DBBaseModel):
    """User model"""
    password_hash: str
    user_id: UUID

    class Config:
        orm_mode = True
        from_attributes=True

    def build_user_token_data(self) -> dict:
        """
        Builds the user token data
        :return: dict
        """
        res_dict = self.model_dump()
        res_dict['user_id'] = str(self.user_id)
        return UserTokenData.model_validate(res_dict).model_dump()

    def build_response_model(self) -> UserTokenData:
        res_dict = self.model_dump()
        res_dict['user_id'] = str(self.user_id)
        return UserTokenData.model_validate(res_dict)


class UserTokenResponseModel(BaseModel):
    """User token model"""
    user_id: UUID
    access_token: str