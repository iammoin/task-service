from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import DB
from sqlalchemy.orm import Session

from logger import logging

DBTYPE_POSTGRES = 'postgresql'
CORE_SQLALCHEMY_DATABASE_URI = '%s://%s:%s@%s:%s/%s' % (
    DBTYPE_POSTGRES, DB.user, quote_plus(DB.pass_), DB.host, DB.port, DB.name)

db_engine = create_engine(CORE_SQLALCHEMY_DATABASE_URI)

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

DBBase = declarative_base()

def get_uri():
    return CORE_SQLALCHEMY_DATABASE_URI

def get_db():
    """this function is used to inject db_session dependency in every rest api requests"""
    from service.context_manager import context_set_db_session_rollback
    db: Session = SessionLocal()
    try:
        yield db
        #  commit the db session if no exception occurs
        #  if context_set_db_session_rollback is set to True then rollback the db session
        if context_set_db_session_rollback.get():
            logging.info('====> rollback in db session')
            db.rollback()
        else:
            logging.info('====> committing in db session')
            db.commit()
    except Exception as e:
        #  rollback the db session if any exception occurs
        logging.error(e)
        db.rollback()
    finally:
        #  close the db session
        db.close()