from fastapi import APIRouter
from routes.AuthRoutes import account_create, account_login, account_refresh

router = APIRouter(prefix="/account")
router.include_router(account_create.router)
router.include_router(account_login.router)
router.include_router(account_refresh.router)