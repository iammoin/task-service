from sqlalchemy.orm import Session
from entity.users import User
from sqlalchemy import or_
from uuid import UUID
from typing import List

class UserRepository():
    db:Session = NotImplementedError

    def __init__(self, input_db: Session = None):
        if input_db:
            self.db = input_db
        else:
            from service.context_manager import get_db_session
            self.db = get_db_session()
    
    def get_by_user_id(self, user_id: UUID) -> User:
        """This method gets a user from the database."""
        user = None
        with self.db as session:
            user = (
                session.query(User)
                .filter(User.user_id == user_id)
                .first()
            )
        return user
    
    def get_by_username(self, username: str) -> User:
        """This method gets a user from the database."""
        user = None
        with self.db as session:
            user = (
                session.query(User)
                .filter(User.username == username)
                .first()
            )
        return user

    def get_by_email_or_username(self, email: str, username: str) -> User:
        """This method gets a user from the database
            either by email or by username
        """
        user = None
        with self.db as session:
            user = (
                session.query(User)
                .filter(or_(User.email == email, User.username == username))
                .first()
            )
        return user
    
    def get_by_email(self, email: str) -> User:
        user = None
        with self.db as session:
            user = (
                session.query(User)
                .filter(User.email == email)
                .first()
            )
        return user

    def create(self, user: User) -> User:
        """This method creates a user."""
        with self.db as session:
            session.add(user)
            session.commit()
            session.refresh(user)

        return user

    def update_user(self, id: int, updated_data: dict):
        """This method updates a user."""
        
        user = self.get(id)
        if user:
            with self.db as session:
                for key, value in updated_data.items():
                    setattr(user, key, value)
                session.commit()
            return user
        return None

    def delete_user(self, id):
        """This method deletes a user."""

        user = self.get_user(id)
        if user:
            with self.db as session:
                session.delete(user)
                session.commit()
            return True
        return False


def get_user_repository():
    return UserRepository()