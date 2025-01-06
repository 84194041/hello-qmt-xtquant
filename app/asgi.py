import http
import os
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.models.exception import HttpException
from app.controllers.router import root_api_router, root_api_no_auth_router
from app.utils import utils
from fastapi.security import HTTPBearer
        
oauth2_scheme = HTTPBearer(scheme_name="bearer", bearerFormat="JWT", description="JWT Authorization header using the Bearer scheme.")

def exception_handler(request: Request, e: HttpException):
    return JSONResponse(
        status_code=e.status_code,
        content=utils.error_response()
    )

def validation_exception_handler(request: Request, e: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=utils.error_response()
    )

async def general_exception_handler(request: Request, e: Exception):
    return JSONResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        content=utils.error_response(message=str(e))
    )

def get_application() -> FastAPI:
    instance = FastAPI(
        title=config.project_name,
        description=config.project_description,
        version=config.project_version,
        debug=False
    )
    instance.include_router(root_api_router, dependencies=[Depends(oauth2_scheme)])
    instance.include_router(root_api_no_auth_router)
    instance.add_exception_handler(Exception, general_exception_handler)
    instance.add_exception_handler(HttpException, exception_handler)
    instance.add_exception_handler(RequestValidationError, validation_exception_handler)
    return instance

app = get_application()

# Configures the CORS middleware for the FastAPI app
cors_allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = cors_allowed_origins_str.split(",") if cors_allowed_origins_str else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("shutdown")
def shutdown_event():
    logger.info("shutdown event")

@app.on_event("startup")
def startup_event():
    logger.info("startup event")
