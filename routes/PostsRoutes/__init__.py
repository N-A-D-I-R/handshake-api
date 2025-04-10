from fastapi import APIRouter
from routes.PostsRoutes import all_posts, my_posts, post_create, post_delete, post_edit

router = APIRouter(prefix="/post")
router.include_router(all_posts.router)
router.include_router(my_posts.router)
router.include_router(post_create.router)
router.include_router(post_delete.router)
router.include_router(post_edit.router)