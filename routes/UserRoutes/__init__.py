from fastapi import APIRouter
from ..UserRoutes import account_create, account_verify, account_login, account_logout, account_refresh

router = APIRouter(prefix="/user")
router.include_router(account_create.router)
router.include_router(account_verify.router)
router.include_router(account_login.router)
router.include_router(account_logout.router)
router.include_router(account_refresh.router)