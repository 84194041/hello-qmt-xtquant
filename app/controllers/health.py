from app.controllers.base import new_router

router = new_router()

@router.get("/health")
def read_health():
    return "health"
