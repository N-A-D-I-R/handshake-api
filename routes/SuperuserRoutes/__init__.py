from fastapi import APIRouter
from ..SuperuserRoutes import superuser_login, superuser_logout, superuser_refresh

router = APIRouter(prefix="/superuser")
router.include_router(superuser_login.router)
router.include_router(superuser_logout.router)
router.include_router(superuser_refresh.router)