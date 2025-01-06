from fastapi import APIRouter
from app.controllers import health

root_api_router = APIRouter()
# v1
# root_api_router.include_router(permissions.router)
# root_api_router.include_router(generate.router)

# no authentication required
root_api_no_auth_router = APIRouter()
root_api_no_auth_router.include_router(health.router)
