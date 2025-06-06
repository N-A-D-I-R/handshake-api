from fastapi import APIRouter

from . import user_profile, user_profile_me, user_search

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(user_search.router)
router.include_router(user_profile_me.router)
router.include_router(user_profile.router)