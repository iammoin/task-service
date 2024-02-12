
# from sqlalchemy.orm import Session
# from routers.context_manager import get_db_session
# from entity.base import BaseEntity

# class BaseRepository(BaseEntity):
# class BaseRepository():
#     def __init__(self):
#         self.db: Session = get_db_session

    # @classmethod
    # def get_by_uuid(self, cls, uuid):
    #     return self.db.query(cls).filter(cls.uuid == uuid, cls.is_deleted.is_(False)).first()

    # @staticmethod
    # def get_by_id(cls, id):
    #     from routers.context_manager import get_db_session
    #     db: Session = get_db_session()
    #     return db.query(cls).filter(cls.id == id, cls.is_deleted.is_(False)).first()

    # @staticmethod
    # def create(cls, entity) -> BaseEntity:
    #     from routers.context_manager import get_db_session
    #     db: Session = get_db_session()
    #     db.add(cls, entity)
    #     db.flush()
    #     return entity