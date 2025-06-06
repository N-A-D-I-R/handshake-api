from fastapi import APIRouter

from . import edit_profile

router = APIRouter(prefix="/settings", tags=["Settings"])
router.include_router(edit_profile.router)