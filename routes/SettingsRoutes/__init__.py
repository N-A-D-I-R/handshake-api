from fastapi import APIRouter

from . import edit_profile, change_password, change_email

router = APIRouter(prefix="/settings", tags=["Settings"])
router.include_router(edit_profile.router)
router.include_router(change_password.router)
router.include_router(change_email.router)