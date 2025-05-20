from fastapi import APIRouter

from . import all_pending_offers
from ..ModerationRoutes import approve_post, reject_post

router = APIRouter(prefix="/moderation")
router.include_router(approve_post.router)
router.include_router(reject_post.router)
router.include_router(all_pending_offers.router)