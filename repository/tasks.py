from sqlalchemy.orm import Session
from entity.tasks import Task, SharedTasks
from uuid import UUID
from typing import List
from sqlalchemy import and_, desc, update
from logger import logger

class SharedTasksRepository():
    db:Session = NotImplementedError

    def __init__(self):
        from service.context_manager import get_db_session
        self.db = get_db_session()
    
    def get_by_from_user_id(self, from_user_id: UUID) -> List[SharedTasks]:
        """This method gets shared_tasks from the database."""
        shared_tasks = []
        with self.db as session:
            shared_tasks = (
                session.query(SharedTasks)
                .filter(and_(SharedTasks.from_user_id == from_user_id, SharedTasks.is_shared == True))
                .all()
            )
        return shared_tasks
    
    def get_by_to_user_id(self, to_user_id: UUID) -> List[SharedTasks]:
        """This method gets shared_tasks from the database."""
        shared_tasks = []
        with self.db as session:
            shared_tasks = (
                session.query(SharedTasks)
                .filter(and_(SharedTasks.to_user_id == to_user_id, SharedTasks.is_shared == True))
                .all()
            )
        return shared_tasks
    
    def get_by_from_and_to_user_id(self, from_user_id: UUID, to_user_id: UUID) -> SharedTasks:
        """This method gets shared_tasks from the database."""
        shared_task = None
        with self.db as session:
            shared_task = (
                session.query(SharedTasks)
                .filter(and_(SharedTasks.to_user_id == to_user_id, 
                             SharedTasks.from_user_id == from_user_id,
                             SharedTasks.is_shared == True))
                .first()
            )
        return shared_task

    def create(self, shared_task: SharedTasks) -> SharedTasks:
        """This method creates a shared_task."""
        with self.db as session:
            session.add(shared_task)
            session.commit()
            session.refresh(shared_task)

        return shared_task

    def unshare(self, shared_task: SharedTasks):
        """This method updates a shared_task."""
        if shared_task:
            with self.db as session:
                session.execute(update(SharedTasks).where(SharedTasks.share_id == shared_task.share_id)
                                .values(is_shared=False))
                session.commit()
            return shared_task
        return None

    def delete(self, id):
        """This method deletes a shared_task."""

        shared_task = self.get(id)
        if shared_task:
            with self.db as session:
                session.delete(shared_task)
                session.commit()
            return True
        return False
    

class TaskRepository():
    db:Session = NotImplementedError

    def __init__(self):
        from service.context_manager import get_db_session
        self.db = get_db_session()
    
    def get_by_task_id(self, task_id: UUID) -> Task:
        """This method gets a task from the database."""
        task = None
        with self.db as session:
            task = (
                session.query(Task)
                .filter(and_(Task.task_id == task_id, Task.is_deleted==False))
                .first()
            )
        return task
    
    def get_last_by_user_id(self, user_id: UUID) -> Task:
        task = None
        with self.db as session:
            task = (
                session.query(Task)
                .filter(Task.user_id == user_id)
                .order_by(desc(Task.priority))
                .first()
            )
        return task
    
    def get_by_user_id(self, user_id: UUID) -> List[Task]:
        tasks = []
        with self.db as session:
            tasks = (
                session.query(Task)
                .filter(and_(Task.user_id == user_id, Task.is_deleted == False))
                .order_by(Task.priority)
                .all()
            )
        return tasks

    def create(self, task: Task) -> Task:
        """This method creates a task."""
        with self.db as session:
            session.add(task)
            session.commit()
            session.refresh(task)

        return task

    def modify(self, task: Task, updated_data: dict):
        """This method updates a task."""
        logger.info(msg=f"updated data for modify : {updated_data}")
        if task:
            with self.db as session:
                update_query = session.query(Task).filter(Task.task_id == task.task_id)
                updates = update_query.update(updated_data)
                session.commit()
            return task
        return None
    

    def reorder(self, task: Task, new_priority: int):
        """This method updates a task."""
        logger.info(msg=f"new_priority : {new_priority}, task : {task.priority}")
        old_priority = task.priority
        if task:
            with self.db as session:
                stmt = None
                if new_priority < task.priority:
                    stmt = (update(Task).where(and_(Task.priority >= new_priority, Task.priority < old_priority))
                            .values(priority=Task.priority + 1))
                else:
                    stmt = (update(Task).where(and_(Task.priority > old_priority, Task.priority <= new_priority))
                            .values(priority=Task.priority - 1))
                session.execute(stmt)
                session.execute(update(Task).where(Task.task_id == task.task_id).values(priority=new_priority))
                session.commit()
            task.priority = new_priority
            return task
        return None

    def delete(self, task: Task):
        """This method deletes a task."""
        if task:
            task.is_deleted = True
            with self.db as session:
                session.execute(update(Task).where(Task.task_id == task.task_id).values(is_deleted=True))
                session.commit()
            return True
        return False

def get_task_repository():
    return TaskRepository()

def get_shared_tasks_repository():
    return SharedTasksRepository()