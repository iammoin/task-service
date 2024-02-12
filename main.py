import http
import json

from fastapi import FastAPI, Depends, Request
from pydantic import ValidationError
from sqlalchemy.exc import ProgrammingError, DataError, IntegrityError

from routers import users, tasks
from routers.base import build_api_response
from service.context_manager import context_log_meta, context_set_db_session_rollback
from logger import logger
from models.base import GenericResponseModel
from config.auth import JWTBearer
from models.exceptions import AppException

from config.logger import logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info("Starting up...")
    logger.info("run alembic upgrade head...")
    run_migrations()
    yield
    logger.info("Shutting down...")
    
app = FastAPI()

@app.get("/") 
async def main_route():     
  return {"message": "Hey, It is me Moin"}

# user registration and login apis should be open
app.include_router(users.router)

#  token based authentication apis should have dependency on authenticate_token
app.include_router(tasks.router, dependencies=[Depends(JWTBearer())])


#  register exception handlers here
@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(), msg=f"data validation failed {exc.errors()}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                                   error="Data Validation Failed"))


@app.exception_handler(ProgrammingError)
async def sql_exception_handler(request: Request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Data Source Error"))


@app.exception_handler(DataError)
async def sql_data_exception_handler(request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql data exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Data Error for data provided"))


@app.exception_handler(AppException)
async def application_exception_handler(request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(),
                 msg=f"application exception occurred error: {json.loads(str(exc))}")
    return build_api_response(GenericResponseModel(status_code=exc.status_code,
                                                   error=exc.message))


@app.exception_handler(IntegrityError)
async def sql_integrity_exception_handler(request, exc):
    context_set_db_session_rollback.set(True)
    logger.error(extra=context_log_meta.get(),
                 msg=f"sql integrity exception occurred error: {str(exc.args)} statement : {exc.statement}")
    return build_api_response(GenericResponseModel(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                                   error="Integrity Error for data provided"))


# register event handlers here
@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")
