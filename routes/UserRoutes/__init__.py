from fastapi import APIRouter

from . import user_create, user_login, user_logout, user_refresh, user_verify

router = APIRouter(prefix="/user")
router.include_router(user_create.router)
router.include_router(user_verify.router)
router.include_router(user_login.router)
router.include_router(user_logout.router)
router.include_router(user_refresh.router)