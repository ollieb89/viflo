"""
API v1 router.
"""
from fastapi import APIRouter

router = APIRouter()

# Import and include endpoint routers here
# from app.api.v1.endpoints.users import router as users_router
# router.include_router(users_router, prefix="/users", tags=["users"])


@router.get("/")
def api_info():
    """API information."""
    return {"version": "1.0", "status": "active"}
