from fastapi import Request,APIRouter
from app.models.exception import HttpException

def new_router(dependencies=None):
    router = APIRouter()
    router.tags = ['V1']
    router.prefix = '/api'
    # 将认证依赖项应用于所有路由
    if dependencies:
        router.dependencies = dependencies
    return router
