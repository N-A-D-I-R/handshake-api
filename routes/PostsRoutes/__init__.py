from fastapi import APIRouter
from ..PostsRoutes import my_posts, post_create, post_delete, post_edit, get_post

router = APIRouter(prefix="/offers")
router.include_router(my_posts.router)
router.include_router(post_create.router)
router.include_router(post_delete.router)
router.include_router(post_edit.router)
router.include_router(get_post.router)