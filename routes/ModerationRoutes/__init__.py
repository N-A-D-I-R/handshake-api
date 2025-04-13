from fastapi import APIRouter
from ..ModerationRoutes import approve_post, reject_post, all_posts

router = APIRouter(prefix="/moderation")
router.include_router(approve_post.router)
router.include_router(reject_post.router)
router.include_router(all_posts.router)