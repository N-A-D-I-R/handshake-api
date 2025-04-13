from fastapi import APIRouter
from ..SuperuserRoutes import superuser_login

router = APIRouter(prefix="/superuser")
router.include_router(superuser_login.router)